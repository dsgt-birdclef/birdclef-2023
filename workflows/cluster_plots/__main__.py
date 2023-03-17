import json
import os

import luigi
from google.cloud import storage

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
from workflows.utils.pull import Pull

from .plotting import ClusterPlotAllTasks


class ClusterPlotTaskWrapper(luigi.WrapperTask):
    output_path = luigi.Parameter()
    list_species = luigi.Parameter()

    def requires(self):
        pull_data = Pull(
            input_path="data/processed/birdclef-2022/birdnet-embeddings-with-neighbors",
            output_path="../data/processed/birdclef-2022/birdnet-embeddings-with-neighbors",
            parallelism=os.cpu_count(),
        )
        yield pull_data

        yield ClusterPlotAllTasks(
            output_path=self.output_path,
            total_cnt=len(self.list_species),
        )
        # yield cluster_plot_all_task


def list_species():
    f = open(
        "/home/nzhon/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-agreement-static/v1/agreement.json"
    )
    agreement = json.load(f)
    return agreement


if __name__ == "__main__":
    species_list = [t["ego_primary_label"] for t in list_species()]
    luigi.build(
        [
            ClusterPlotTaskWrapper(
                output_path="/home/nzhon/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1",
                list_species=species_list,
            ),
        ],
        # scheduler_host="luigi.us-central1-a.c.birdclef-2023.internal",
        workers=2,
    )
