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
        yield ClusterPlotAllTasks(
            spark_path=self.spark_path,
            local_path=self.plot_local_path,
            total_cnt=len(self.list_species),
        )

        for i in range(len(self.list_species)):
            name = self.list_species[i]
            push_data = Push(
                input_path=f"{self.plot_local_path}/{name}",
                output_path=f"{self.plot_cloud_path}/{name}",
                parallelism=1,
            )
            yield push_data


def get_species_list(path):
    agreement_path = Path(
        f"{path}/birdnet-embeddings-with-neighbors-agreement-static/v1/agreement.json"
    )
    return [t["ego_primary_label"] for t in json.loads(agreement_path.read_text())]


if __name__ == "__main__":
    data_path = (
        Path(__file__).parent.parent.parent.parent / "data/processed/birdclef-2022"
    )
    os.makedirs(data_path)
    os.makedirs(data_path / "birdnet-embeddings-with-neighbors-static/v1")
    luigi.build(
        [
            Pull(
                input_path="data/processed/birdclef-2022/birdnet-embeddings-with-neighbors/v1",
                output_path=f"{str(data_path)}/birdnet-embeddings-with-neighbors/v1",
                parallelism=os.cpu_count(),
            ),
            Pull(
                input_path="data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-agreement-static/v1",
                output_path=f"{str(data_path)}/birdnet-embeddings-with-neighbors-agreement-static/v1",
                parallelism=os.cpu_count(),
            ),
        ],
        scheduler_host="luigi.us-central1-a.c.birdclef-2023.internal",
        workers=2,
    )
    species_list = get_species_list(str(data_path))
    storage_client = storage.Client("birdclef-2023")
    bucket = storage_client.get_bucket("birdclef-2023")
    for species in species_list:
        blobs = list(
            bucket.list_blobs(
                prefix=f"data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1/{species}"
            )
        )
        if len(blobs) > 0:
            luigi.build(
                [
                    Pull(
                        input_path=f"data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1/{species}",
                        output_path=f"{data_path}/birdnet-embeddings-with-neighbors-static/v1/{species}",
                        parallelism=os.cpu_count(),
                    )
                ],
                scheduler_host="luigi.us-central1-a.c.birdclef-2023.internal",
                workers=2,
            )
    luigi.build(
        [
            ClusterPlotTaskWrapper(
                spark_path=str(data_path / "birdnet-embeddings-with-neighbors/v1"),
                data_input_path="data/processed/birdclef-2022",
                data_output_path=str(data_path),
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
