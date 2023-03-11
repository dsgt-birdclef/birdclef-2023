import luigi
from luigi.parameter import ParameterVisibility


class DynamicRequiresMixin:
    dynamic_requires = luigi.Parameter(
        default=[], visibility=ParameterVisibility.HIDDEN
    )

    def requires(self):
        return self.dynamic_requires
