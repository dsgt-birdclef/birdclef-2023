import json
import os
from pathlib import Path

import luigi
from google.cloud import storage
from pyspark.sql import functions as F

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
from workflows.utils.push import Push

from .plotting import ClusterPlotAllTasks


class ClusterPlotTaskWrapper(luigi.WrapperTask):
    data_input_path = luigi.Parameter()
    data_output_path = luigi.Parameter()
    plot_local_path = luigi.Parameter()
    plot_cloud_path = luigi.Parameter()
    spark_path = luigi.Parameter()
    list_species = luigi.Parameter()

    def requires(self):
        pull_data = Pull(
            input_path=self.data_input_path,
            output_path=self.data_output_path,
            parallelism=os.cpu_count(),
        )
        yield pull_data

        yield ClusterPlotAllTasks(
            spark_path=self.spark_path,
            local_path=self.plot_local_path,
            total_cnt=len(self.list_species),
        )

        for i in len(self.list_species):
            name = self.list_species[i]
            push_data = Push(
                input_path=f"{self.plot_local_path}/{name}",
                output_path=f"{self.plot_cloud_path}/{name}",
                parallelism=1,
            )
            yield push_data


def list_species(path):
    return json.loads(path.read_text())


if __name__ == "__main__":
    data_path = (
        Path(__file__).parent.parent.parent.parent / "data/processed/birdclef-2022"
    )
    agreement_path = (
        data_path
        / "birdnet-embeddings-with-neighbors-agreement-static/v1/agreement.json"
    )
    species_list = [t["ego_primary_label"] for t in list_species(agreement_path)]

    luigi.build(
        [
            ClusterPlotTaskWrapper(
                spark_path=str(data_path / "birdnet-embeddings-with-neighbors/v1"),
                data_input_path="data/processed/birdclef-2022/birdnet-embeddings-with-neighbors",
                data_output_path=str(data_path / "birdnet-embeddings-with-neighbors"),
                plot_local_path=str(
                    data_path / "birdnet-embeddings-with-neighbors-static/v1"
                ),
                plot_cloud_path="data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1",
                list_species=species_list,
            ),
        ],
        scheduler_host="luigi.us-central1-a.c.birdclef-2023.internal",
        workers=2,
    )
