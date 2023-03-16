import os
import json

import luigi
from google.cloud import storage
from plotting import ClusterPlottingTask

from workflows.utils.pull import Pull
from workflows.utils.push import Push


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
    species_list = luigi.Parameter()

    def requires(self):
        pull_data = Pull(
            input_path = "data/processed/birdclef-2022/birdnet-embeddings-with-neighbors",
            output_path = "../data/processed/birdclef-2022/birdnet-embeddings-with-neighbors",
            parallelism=os.cpu_count()
        )
        yield pull_data

        for i in range(3):
            cluster_plots = ClusterPlottingTask(
                output_path=self.output_path,
                index=i,
            )
            yield cluster_plots
        

def list_species(birdclef_root_path):
    storage_client = storage.Client("birdclef-2023")

    bucket = storage_client.get_bucket("birdclef-2023")

    species = bucket.list_blobs(prefix=birdclef_root_path)

    species_list = []
    for blob in species:
        name = blob.name
        name = name.replace(birdclef_root_path + "/", "")
        name = name.split("/")[0]
        species_list.append(name.strip())

    return list(set(species_list))

if __name__ == "__main__":
    luigi.build(
        [
            ClusterPlotTask(
                species_list = list_species("data/raw/birdclef-2022/train_audio"),
                output_path="../data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1",
            ),
        ],
        scheduler_host="luigi.us-central1-a.c.birdclef-2023.internal",
        workers=2,
    )
