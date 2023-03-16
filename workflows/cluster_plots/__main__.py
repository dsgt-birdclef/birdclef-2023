import os
import json

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
    output_path = luigi.Parameter()

    def requires(self):
        agreement = open("../data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-agreement-static/v1/agreement.json")
        agreement = json.loads(agreement.read())
        for i in range(3):
            cluster_plots = ClusterPlottingTask(
                output_path=self.output_path,
                index=i,
            )
            yield cluster_plots


if __name__ == "__main__":
    luigi.build(
        [
            ClusterPlotTask(
                output_path="../data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1",
            ),
        ],
        workers=2,
    )
