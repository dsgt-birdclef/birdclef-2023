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
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
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
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(args)
    spark = get_spark(cores=16, memory="16g")
    df = spark.read.parquet(
        "data/processed/birdclef-2023/train_postprocessed/v7"
    ).select("species", "embedding")

    if args.dry_run:
        df = df.limit(2000)
        args.n_iter = 1
    df = df.withColumn(
        "species_count", F.count("*").over(Window.partitionBy("species"))
    ).where("species_count > 1")
    data = df.toPandas()
    print(data.shape)
    spark.stop()

    def prepare_data(df, mlb):
        labels = mlb.transform(df.species)
        # labels = df.species
        embeddings = np.stack(df.embedding.values)
        # next_embeddings = np.stack(df.next_embedding.values)
        # track_embeddings = np.stack(df.track_embedding.values)
        # embeddings = np.concatenate(
        #     [embeddings, next_embeddings, track_embeddings], axis=1
        # )
        return embeddings, labels

    mlb = LabelEncoder()
    labels = mlb.fit_transform(data.species)
    print("num labels", len(mlb.classes_))

    train_df, test_df = train_test_split(data, train_size=0.8, stratify=labels)

    train_x, train_y = prepare_data(train_df, mlb)
    test_x, test_y = prepare_data(test_df, mlb)

    # def scorer(estimator, X, y):
    #     return roc_auc_score(y, estimator.predict_proba(X), average="macro")

    search = BayesSearchCV(
        XGBClassifier(tree_method="gpu_hist", eta=0.1, verbosity=1),
        {
            "max_depth": (3, 15, "uniform"),
            "gamma": (0.0, 1.0, "uniform"),
            "min_child_weight": (1, 20, "uniform"),
        },
        n_iter=args.n_iter,
        scoring="f1_macro",
        verbose=4,
        # cv=zip(
        #     [np.arange(0, int(len(train_x) * 0.7))],
        #     [np.arange(int(len(train_x) * 0.7) + 1, len(train_x))],
        # ),
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
                class_weight="balanced", y=train_df.species
            )
            if args.weighted
            else None
        ),
        callback=bar_callback,
    )

    # print the best params
    print(search.best_params_)

    model_eval(test_y, search.predict(test_x))
    # print(
    #     "average precision",
    #     average_precision_score(test_y, search.predict_proba(test_x)),
    # )

    # display the scores as a dataframe
    results = pd.DataFrame(search.cv_results_)
    print(results)

    # now let's train a model on the full dataset
    X, y = prepare_data(data, mlb)
    clf = XGBClassifier(tree_method="gpu_hist", eta=0.1, **search.best_params_)
    clf.fit(
        X,
        y,
        sample_weight=(
            class_weight.compute_sample_weight(class_weight="balanced", y=data.species)
            if args.weighted
            else None
        ),
    )

    prefix = args.prefix
    results.to_csv(f"data/models/baseline_v2/{prefix}.csv")
    pickle.dump(
        clf,
        Path(f"data/models/baseline_v2/{prefix}.pkl").open("wb"),
    )
    pickle.dump(
        mlb,
        Path(f"data/models/baseline_v2/{prefix}_mlb.pkl").open("wb"),
    )


if __name__ == "__main__":
    main()
