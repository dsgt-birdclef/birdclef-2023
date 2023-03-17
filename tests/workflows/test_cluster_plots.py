import json
import os

import luigi
import pytest
from google.cloud import storage

from workflows.cluster_plots.__main__ import ClusterPlotTaskWrapper

default_output_path = "/home/nzhon/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1"


def test_cluster_plots_task_luigi_build(output_path=default_output_path):
    f = open(
        "/home/nzhon/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-agreement-static/v1/agreement.json"
    )
    agreement = json.load(f)
    species_list = [t["ego_primary_label"] for t in agreement]

    task = ClusterPlotTaskWrapper(
        output_path=output_path,
        list_species=species_list,
    )
    res = luigi.build([task], local_scheduler=True, workers=1, detailed_summary=True)
    assert res
    output_dir = list(os.listdir(output_path))
    assert len(output_dir) == 23
    # assert(output_dir == len(list_species))

    storage_client = storage.Client("birdclef-2023")
    bucket = storage_client.get_bucket("birdclef-2023")
    species = list(
        bucket.list_blobs(
            prefix="data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1"
        )
    )
    species = [s.name.split("/")[-2] for s in species]
    for s in species:
        pictures = list(
            bucket.list_blobs(
                prefix=f"data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1/{s}"
            )
        )
        pictures = [picture.name.split("/")[-1] for picture in pictures]
        assert len(pictures) == 4
        assert "_SUCCESS" in pictures
        assert "distances.png" in pictures
        assert "ego_birdnet_label.png" in pictures
        assert "knn_birdnet_label.png" in pictures
