import luigi
from luigi.contrib.external_program import ExternalProgramTask
from luigi.contrib.gcs import GCSTarget

from workflows.utils.mixin import DynamicRequiresMixin


class GSUtilRsyncTask(ExternalProgramTask, DynamicRequiresMixin):
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    is_dir = luigi.BoolParameter(default=True)
    capture_output = True

    def program_args(self):
        in_path = self.input_path.rstrip("/")
        out_path = self.output_path.rstrip("/")

        if self.is_dir:
            return f"gsutil -m rsync -r {in_path}/ {out_path}/ && touch {out_path}/_SUCCESS".split()
        else:
            return f"gsutil -m rsync -r {in_path} {out_path}".split()

    def output(self):
        is_gs_path = self.output_path.startswith("gs://")
        if is_gs_path:
            return GCSTarget(self.output_path)
        else:
            return luigi.LocalTarget(f"{self.output_path}/_SUCCESS")
