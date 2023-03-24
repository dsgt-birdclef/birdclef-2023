import json
import os
import shutil
import subprocess

import luigi
import pytest
from google.cloud import storage

from workflows.cluster_plots.plotting import ClusterPlotAllTasks

default_spark_path = (
    "/home/nzhon/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors/v1"
)


def test_cluster_plots_task_luigi_build(
    spark_path=default_spark_path, tmp_path="test_output"
):
    abs_path = os.path.dirname(__file__)
    filename = os.path.join(abs_path, "agreement_test.json")
    tmp_path = os.path.join(abs_path, tmp_path)
    os.mkdir(tmp_path)

    f = open(filename)
    agreement = json.load(f)
    species_list = [t["ego_primary_label"] for t in agreement]

    task = ClusterPlotAllTasks(
        spark_path=spark_path,
        local_path=tmp_path,
        total_cnt=len(species_list),
    )
    res = luigi.build([task], local_scheduler=True, workers=1, detailed_summary=True)
    assert res

    output_dir = list(os.listdir(tmp_path))
    assert len(output_dir) == 10

    for species in species_list:
        assert species in output_dir
    shutil.rmtree(tmp_path)
