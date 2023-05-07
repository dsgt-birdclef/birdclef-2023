import argparse
import pickle
from birdclef.utils import get_spark
import pyspark.sql.functions as F
from pyspark.sql.functions import concat, rand

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["logistic_reg_3"], required=True, type=str)
    parser.add_argument("--input", "--i", required=True, type=str)
    # parser.add_argument("--output", "--o", required=True, type=str)
    args, other_args = parser.parse_known_args()
    args = vars(args)

    spark = get_spark()
    df = spark.read.parquet(
        args["input"]
    )

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
        concat(explode_preds.track_name, explode_preds.start_time, explode_preds.track_type).alias("track_id"),
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

    model = pickle.load(open(f"../models/{args['model']}.pkl", 'rb'))

    result = model.predict(x)

    print(result)

if __name__ == "__main__":
    main()