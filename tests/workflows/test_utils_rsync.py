# A way to test the rsync command by mocking out the program_args. This is
# useful because we want to test a larger workflow that uses this command.
import luigi
import pytest

from workflows.utils.rsync import GSUtilRsyncTask


def test_gsutil_rsync_task_run(tmp_path):
    in_path = tmp_path / "input"
    in_path.mkdir(parents=True, exist_ok=True)
    # create some files
    for i in range(3):
        (in_path / f"file{i}").touch()

    out_path = tmp_path / "output"
    task = GSUtilRsyncTask(
        input_path=in_path.as_posix(),
        output_path=out_path.as_posix(),
    )
    task.run()

    # ensure properties
    assert task.output().exists()
    assert (out_path / "_SUCCESS").exists()
    assert len(list(out_path.glob("*"))) == 4


def test_gsutil_rsync_task_luigi_build(tmp_path):
    in_path = tmp_path / "input"
    in_path.mkdir(parents=True, exist_ok=True)
    # create some files
    for i in range(3):
        (in_path / f"file{i}").touch()

    out_path = tmp_path / "output"
    task = GSUtilRsyncTask(
        input_path=in_path.as_posix(),
        output_path=out_path.as_posix(),
    )
    res = luigi.build([task], local_scheduler=True, workers=1)
    assert res

    # ensure properties
    assert task.output().exists()
    assert (out_path / "_SUCCESS").exists()
    assert len(list(out_path.glob("*"))) == 4
