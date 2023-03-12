import os

import luigi
from plotting import ClusterPlottingTask

from birdclef.knn_labels import (
    compute_embedding_2d,
    get_knn_labels,
    get_label_agreement,
    get_subset_pdf,
    plot_distances,
    plot_embedding,
    write_plots_to_disk,
)
from birdclef.utils import get_spark


class ClusterPlotTask(luigi.WrapperTask):
    path_prefix = luigi.Parameter()

    def requires(self):
        spark = get_spark(memory="16g")
        df = spark.read.parquet(
            "../data/processed/birdclef-2022/birdnet-embeddings-with-neighbors/v1"
        )
        labeled_neighborhood = get_knn_labels(df).cache()

        for i in range(len(df)):
            cluster_plots = ClusterPlottingTask(
                path_prefix=self.path_prefix,
                df=df,
                labeled_neighborhood=labeled_neighborhood,
                index=i,
            )
            yield cluster_plots


if __name__ == "__main__":
    n_threads = 4
    luigi.build(
        [
            ClusterPlotTask(
                path_prefix="../data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1",
            ),
        ],
        workers=os.cpu_count() // n_threads,
    )
