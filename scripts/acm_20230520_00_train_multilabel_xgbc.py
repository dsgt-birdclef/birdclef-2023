import pickle
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd
import tqdm
from pyspark.sql import Window
from pyspark.sql import functions as F
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.utils import class_weight
from skopt import BayesSearchCV
from xgboost import XGBClassifier

from birdclef.utils import get_spark


def model_eval(truth, preds):
    print("Accuracy:", accuracy_score(truth, preds))
    print(
        "Precision:",
        precision_score(truth, preds, average="macro"),
    )
    print(
        "Recall:",
        recall_score(truth, preds, average="macro"),
    )
    print(
        "F1 Score:",
        f1_score(truth, preds, average="macro"),
    )


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--prefix",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--weighted",
        action="store_true",
    )
    parser.add_argument(
        "--n-iter",
        type=int,
        default=20,
    )
    parser.add_argument("--scoring", default="f1_macro")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(args)
    spark = get_spark(cores=16, memory="2g")
    df = spark.read.parquet("data/processed/birdclef-2023/train_postprocessed/v3")
    df = (
        df.withColumn("primary_label", F.col("metadata_species")[0])
        .withColumn("species", F.concat("metadata_species", "predicted_species"))
        .withColumn(
            "species_count", F.count("*").over(Window.partitionBy("primary_label"))
        )
    )
    df.printSchema()
    df.show(n=5)

    if args.dry_run:
        df = df.limit(2000)
        args.n_iter = 1

    df = df.where("species_count > 1")

    data = df.toPandas()
    print(data.shape)
    spark.stop()

    def prepare_data(df, mlb):
        labels = mlb.transform(df.species)
        embeddings = np.stack(df.embedding.values)
        return embeddings, labels

    mlb = MultiLabelBinarizer()
    mlb.fit(data.species)
    print("num labels", len(mlb.classes_))

    train_df, test_df = train_test_split(
        data, test_size=0.3, stratify=data.primary_label
    )
    train_x, train_y = prepare_data(train_df, mlb)
    test_x, test_y = prepare_data(test_df, mlb)

    search = BayesSearchCV(
        XGBClassifier(tree_method="gpu_hist", eta=0.2, verbosity=1),
        {
            "max_depth": (3, 15, "uniform"),
            "gamma": (0.0, 1.0, "uniform"),
            "min_child_weight": (1, 10, "uniform"),
        },
        n_iter=args.n_iter,
        scoring=args.scoring,
        verbose=4,
        cv=3,
    )
    # create a tqdm progress bar which is passed as a callback to search.fit
    bar = tqdm.tqdm(total=args.n_iter, desc="hyperparameter tuning")

    def bar_callback(*args, **kwargs):
        bar.update()

    search.fit(
        train_x,
        train_y,
        sample_weight=(
            class_weight.compute_sample_weight(
                class_weight="balanced", y=train_df.primary_label
            )
            if args.weighted
            else None
        ),
        callback=bar_callback,
    )

    model_eval(test_y, search.predict(test_x))
    print(average_precision_score(test_y, search.predict_proba(test_x)))

    # print the best params
    print(search.best_params_)

    # display the scores as a dataframe
    results = pd.DataFrame(search.cv_results_)
    print(results)

    if args.dry_run:
        print("dry running, not saving results")
        return

    prefix = args.prefix
    results.to_csv(f"data/models/baseline_v2/{prefix}.csv")
    pickle.dump(
        search.best_estimator_,
        Path(f"data/models/baseline_v2/{prefix}.pkl").open("wb"),
    )
    pickle.dump(
        mlb,
        Path(f"data/models/baseline/{prefix}_mlb.pkl").open("wb"),
    )


if __name__ == "__main__":
    main()
