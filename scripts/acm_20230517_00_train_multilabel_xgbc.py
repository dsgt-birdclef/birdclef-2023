import pickle
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd
import tqdm
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
    args = parser.parse_args()
    print(args)
    spark = get_spark(cores=16, memory="2g")
    df = spark.read.parquet("data/processed/birdclef-2023/train_postprocessed/v1")
    df.printSchema()
    df.show(n=5)

    # df = df.limit(2000)
    # args.n_iter = 1

    data = df.toPandas()
    spark.stop()

    mlb = MultiLabelBinarizer()
    labels = mlb.fit_transform(data.species)
    embeddings = np.stack(data.embedding.values)

    train_x, test_x, train_y, test_y = train_test_split(
        embeddings, labels, test_size=0.3
    )

    search = BayesSearchCV(
        XGBClassifier(tree_method="gpu_hist", eta=0.2, verbosity=1),
        {
            "max_depth": (3, 15, "uniform"),
            "gamma": (0.0, 1.0, "uniform"),
            "min_child_weight": (1, 10, "uniform"),
        },
        n_iter=args.n_iter,
        scoring="f1_macro",
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
            class_weight.compute_sample_weight(class_weight="balanced", y=train_y)
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

    prefix = args.prefix
    results.to_csv(f"data/models/baseline/{prefix}.csv")
    pickle.dump(
        search.best_estimator_,
        Path(f"data/models/baseline/{prefix}.pkl").open("wb"),
    )
    pickle.dump(
        mlb,
        Path(f"data/models/baseline/{prefix}_mlb.pkl").open("wb"),
    )


if __name__ == "__main__":
    main()
