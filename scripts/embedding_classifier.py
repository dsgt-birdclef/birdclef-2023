import argparse
import csv
import pickle
from pathlib import Path

import librosa
import pyspark.sql.functions as F
import tqdm
from pyspark.sql.functions import concat, rand

from birdclef import birdnet
from birdclef.data.utils import slice_seconds
from birdclef.utils import get_spark


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--birdnet_path", default="data/models/birdnet-analyzer-pruned", type=str
    )
    parser.add_argument("--input", "--i", required=True, type=str)
    parser.add_argument("--birdclef_root", default="data/raw/birdclef-2023", type=str)
    parser.add_argument("--model", choices=["logistic_reg_3"], required=True, type=str)
    parser.add_argument("--output", "--o", required=True, type=str)
    args, other_args = parser.parse_known_args()
    args = vars(args)

    repo_path = args["birdnet_path"]
    model = birdnet.load_model_from_repo(repo_path)
    prediction_func = birdnet.prediction_func(model)
    labels = birdnet.load_labels(repo_path)
    mapped_labels = birdnet.load_mapped_labels(repo_path)

    rows = []
    paths = sorted(Path(args["input"]).glob(f"{self.track_stem}*"))
    for path in tqdm.tqdm(paths):
        y, sr = librosa.load(path.as_posix(), sr=48_000)

        X = slice_seconds(y, sr, seconds=3, step=3)
        pred = prediction_func(X)[0]
        pred_sigmoid = 1 / (1 + np.exp(-pred))

        indices = birdnet.rank_indices(pred_sigmoid)
        for i in range(pred_sigmoid.shape[0]):
            predictions = [
                {
                    "index": int(j),
                    "label": labels[j],
                    "mapped_label": mapped_labels[j],
                    "probability": float(pred_sigmoid[i][j]),
                    "rank": rank,
                }
                for rank, j in enumerate(indices)
            ]
            rows.append(
                {
                    "track_name": "/".join(path.parts[-2:]),
                    "embedding": pred[i].tolist(),
                    "predictions": predictions,
                }
            )

    spark = get_spark()
    df = spark.read.parquet(args["input"])

    explode_preds = df.select(
        "species",
        "track_stem",
        "track_name",
        "embedding",
        "start_time",
        "track_type",
        F.explode(df.predictions).alias("col"),
    )
    explode_preds = explode_preds.select(
        concat(
            explode_preds.track_name, explode_preds.start_time, explode_preds.track_type
        ).alias("track_id"),
        "species",
        "embedding",
        explode_preds.col.label.alias("label"),
        explode_preds.col.mapped_label.alias("mapped_label"),
        explode_preds.col.probability.alias("probability"),
    )

    explode_preds_bird_calls = explode_preds.filter(explode_preds.probability > 0.5)

    length = len(explode_preds_bird_calls.select("embedding").take(1)[0]["embedding"])

    explode_preds_bird_calls = explode_preds_bird_calls.drop("probability")
    explode_preds_bird_calls = explode_preds_bird_calls.dropDuplicates(["track_id"])
    data = explode_preds_bird_calls.select(
        ["species"]
        + [
            explode_preds_bird_calls.embedding[i].alias("embedding" + str(i))
            for i in range(length)
        ]
    )
    data = data.orderBy(rand())
    data = data.toPandas()

    x, y = data.loc[:, data.columns != "species"], data["species"]

    model = pickle.load(open(f"../models/{args['model']}.pkl", "rb"))

    result = model.predict_proba(x)

    print(result)


if __name__ == "__main__":
    main()
