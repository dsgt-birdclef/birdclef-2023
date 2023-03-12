import luigi
import pandas as pd
import pytest

from workflows.train_durations import (
    GSUtilRsyncTask,
    TrainDurations,
    TrainDurationsWorkflow,
)


def test_train_durations_workflow_luigi_build(tmp_path, birdclef_root):
    # just ensure that we schedule the right tasks in the correct order
    # we don't need to test the actual functionality of the tasks

    out_path = tmp_path / "output.parquet"
    task = TrainDurationsWorkflow(
        birdclef_root_path=birdclef_root.as_posix(),
        local_data_root=tmp_path.as_posix(),
        output_path=out_path.as_posix(),
        parallelism=1,
    )
    res = luigi.build([task], local_scheduler=True, workers=1, detailed_summary=True)
    assert res.status == luigi.execution_summary.LuigiStatusCode.SUCCESS
    download_path = tmp_path / "raw" / birdclef_root.name
    assert (download_path / "_SUCCESS").exists()
    print(download_path)

    # assert that the output exists
    assert out_path.exists()
    df = pd.read_parquet(out_path)
    print(df)
    assert df.shape[0] == 3 * 2
    assert df["duration"].sum() > 0
