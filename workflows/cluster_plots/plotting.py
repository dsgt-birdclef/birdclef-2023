import luigi

from birdclef.utils import get_spark
from birdclef.knn_labels import (
    get_knn_labels,
    get_label_agreement,
    get_subset_pdf,
    plot_distances,
    compute_embedding_2d,
    plot_embedding,
    write_plots_to_disk,
)

class ClusterPlottingTask(luigi.Task):
    path_prefix = luigi.Parameter()
    df = luigi.Parameter()
    labeled_neighborhood = luigi.Parameter()
    index = luigi.Parameter()

    def output(self):
        pdf = get_subset_pdf(self.df, self.labeled_neighborhood, self.index)
        outputs = set()
        outputs.add(luigi.LocalTarget(
            f"{self.path_prefix}/{pdf.ego_primary_label.iloc[0]}/distances.png"
        ))
        outputs.add(luigi.LocalTarget(
            f"{self.path_prefix}/{pdf.ego_primary_label.iloc[0]}/ego_birdnet_label.png"
        ))
        outputs.add(luigi.LocalTarget(
            f"{self.path_prefix}/{pdf.ego_primary_label.iloc[0]}/knn_birdnet_label.png"
        ))
        return outputs

    def run(self):
        write_plots_to_disk(self.df, self.labeled_neighborhood, self.index, self.path_prefix)

        
