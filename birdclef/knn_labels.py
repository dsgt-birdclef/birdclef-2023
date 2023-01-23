from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pyspark.sql import Window
from pyspark.sql import functions as F
from umap import UMAP


def get_knn_labels(df):
    exploded_neighborhood = (
        df.select(
            "id",
            F.explode(F.arrays_zip("neighbors", "distances")).alias("neighbor"),
        )
        .selectExpr(
            "id", "neighbor.neighbors as neighbor_id", "neighbor.distances as distance"
        )
        .join(df.selectExpr("id as neighbor_id", "birdnet_label"), on="neighbor_id")
    )

    # lets get get the p05, p50, and p95 distances for each label
    distances = exploded_neighborhood.groupBy("id").agg(
        F.percentile_approx("distance", 0.05).alias("distance_p05"),
        F.percentile_approx("distance", 0.50).alias("distance_p50"),
        F.percentile_approx("distance", 0.95).alias("distance_p95"),
    )

    # Let's perform a k-nn classification on the neighborhood using the birdnet
    # labels. We'll compute the score for each label using majority vote. In later
    # iterations, we might only keep neighbors that are within a certain distance of
    # the ego node.
    labeled_neighborhood = (
        exploded_neighborhood
        # first add information to the neighbors so we can compute the classification
        .groupBy("id", "birdnet_label")
        # get the median distance
        .agg(F.count("*").alias("n"))
        .withColumn("total", F.sum("n").over(Window.partitionBy("id")))
        .withColumn("score", F.col("n") / F.col("total"))
        .withColumn(
            "rank", F.row_number().over(Window.partitionBy("id").orderBy(F.desc("n")))
        )
        .where("rank = 1")
        .drop("rank")
        .join(distances, on="id")
        # now let's join information back to the ego node
        .join(
            df.selectExpr(
                "id",
                "primary_label as ego_primary_label",
                "birdnet_label as ego_birdnet_label",
            ),
            on="id",
        )
        .withColumnRenamed("birdnet_label", "knn_birdnet_label")
    )
    return labeled_neighborhood


def get_label_agreement(labeled_neighborhood):
    agreement = (
        labeled_neighborhood.withColumn(
            "ego_birdnet_label_matches",
            (F.col("ego_primary_label") == F.col("ego_birdnet_label")).astype("int"),
        )
        .withColumn(
            "knn_birdnet_label_matches",
            (F.col("ego_primary_label") == F.col("knn_birdnet_label")).astype("int"),
        )
        .groupBy("ego_primary_label")
        .agg(
            F.count("*").alias("n"),
            F.sum("ego_birdnet_label_matches").alias("n_ego_birdnet_label_matches"),
            F.sum("knn_birdnet_label_matches").alias("n_knn_birdnet_label_matches"),
        )
        .withColumn(
            "pct_ego_birdnet_label_matches",
            F.col("n_ego_birdnet_label_matches") / F.col("n"),
        )
        .withColumn(
            "pct_knn_birdnet_label_matches",
            F.col("n_knn_birdnet_label_matches") / F.col("n"),
        )
        .orderBy(F.desc("n"))
    )
    return agreement


def get_subset_pdf(df, labeled_neighborhood, rank):
    freq_primary_labels = (
        df.groupBy("primary_label").agg(F.count("*").alias("n")).orderBy(F.desc("n"))
    ).toPandas()
    primary_label = freq_primary_labels.iloc[rank].primary_label
    subset = labeled_neighborhood.where(
        F.col("ego_primary_label") == primary_label
    ).join(df.select("id", "emb"), on="id")
    return subset.toPandas()


def plot_distances(pdf):
    _, axes = plt.subplots(1, 3, figsize=(8, 3))
    ax = axes.flatten()
    for i, col in enumerate(["distance_p05", "distance_p50", "distance_p95"]):
        pdf[col].plot.hist(ax=ax[i], title=col, bins=20)
        ax[i].set_xlabel("distance")
        ax[i].set_ylabel("count")
    plt.tight_layout()


def compute_embedding_2d(pdf, **kwargs):
    X = np.stack(pdf.emb.values)
    return UMAP(n_components=2, **kwargs).fit_transform(X)


# keep the 5 most common labels
def plot_embedding(pdf, emb, label_col, n_labels, **kwargs):
    primary_label = pdf.ego_primary_label.iloc[0]
    top_labels = (
        pdf.groupby(label_col).size().sort_values(ascending=False).head(n_labels).index
    ).tolist()
    labels = [x if x in top_labels else "other" for x in pdf[label_col].tolist()]
    # now create a color map
    cmap = {label: f"C{i}" for i, label in enumerate(top_labels + ["other"])}
    colors = [cmap[x] for x in labels]

    plt.scatter(emb[:, 0], emb[:, 1], s=5, c=colors, alpha=0.1)

    for label, color in cmap.items():
        plt.scatter([], [], c=color, label=label)
    plt.legend()
    plt.title(f"{label_col} for {primary_label}")


def write_plots_to_disk(df, labeled_neighborhood, rank, path_prefix):
    pdf = get_subset_pdf(df, labeled_neighborhood, rank)
    primary_label = pdf.ego_primary_label.iloc[0]

    path = Path(path_prefix) / primary_label
    path.mkdir(parents=True, exist_ok=True)

    plot_distances(pdf)
    plt.savefig(f"{path}/distances.png")
    plt.close()

    emb = compute_embedding_2d(pdf)
    plot_embedding(pdf, emb, "ego_birdnet_label", 5)
    plt.savefig(f"{path}/ego_birdnet_label.png")
    plt.close()

    plot_embedding(pdf, emb, "knn_birdnet_label", 5)
    plt.savefig(f"{path}/knn_birdnet_label.png")
    plt.close()
