import luigi
from pathlib import Path

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


class ClusterPlottingTask(luigi.Task):
    output_path = luigi.Parameter()
    name = luigi.Parameter(default="")
    index = luigi.Parameter()

    def output(self):
        outputs = set()
        outputs.add(
            luigi.LocalTarget(
                f"{self.output_path}/{self.name}/distances.png"
            )
        )
        outputs.add(
            luigi.LocalTarget(
                f"{self.output_path}/{self.name}/ego_birdnet_label.png"
            )
        )
        outputs.add(
            luigi.LocalTarget(
                f"{self.output_path}/{self.name}/knn_birdnet_label.png"
            )
        )
        return outputs

    def run(self):
        spark = get_spark(memory="2g")
        df = spark.read.parquet(
            "../data/processed/birdclef-2022/birdnet-embeddings-with-neighbors/v1"
        )
        labeled_neighborhood = get_knn_labels(df).cache()
        pdf = get_subset_pdf(df, labeled_neighborhood, self.index)

        self.name = pdf.ego_primary_label.iloc[0]

        path = Path(self.output_path) / self.name
        path.mkdir(parents=True, exist_ok=True)

        plot_distances(pdf)
        plt.savefig(f"{path}/distances.png")
        plt.close()

        emb = compute_embedding_2d(pdf)
        plot_embedding(pdf, emb, "ego_birdnet_label", 5)
        plt.savefig(f"{path}/ego_birdnet_label.png")
        plt.close()

        plot_embedding(pdf, emb, "knn_birdnet_label", 5)
        plt.savefig(f"{path}/knn_birdnet_label.png")
        plt.close()

