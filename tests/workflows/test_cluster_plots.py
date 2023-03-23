import json
import os
import subprocess

import luigi
import pytest
from google.cloud import storage

from workflows.cluster_plots.plotting import ClusterPlotAllTasks

# default_output_path = "/home/nzhon/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1"


def test_cluster_plots_task_luigi_build(tmp_path="test_output"):
    abs_path = os.path.dirname(__file__)
    filename = os.path.join(abs_path, "agreement_test.json")
    tmp_path = os.path.join(abs_path, tmp_path)
    subprocess.run([f"rm -r {tmp_path}/*"], shell=True)

    f = open(filename)
    agreement = json.load(f)
    species_list = [t["ego_primary_label"] for t in agreement]

    task = ClusterPlotAllTasks(
        local_path=tmp_path,
        total_cnt=len(species_list),
    )
    res = luigi.build([task], local_scheduler=True, workers=1, detailed_summary=True)
    assert res

    output_dir = list(os.listdir(tmp_path))
    assert len(output_dir) == 10

    for species in species_list:
        assert species in output_dir
