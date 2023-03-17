from pathlib import Path

import luigi
import matplotlib.pyplot as plt

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
from workflows.utils.push import Push


class ClusterPlotAllTasks(luigi.WrapperTask):
    output_path = luigi.Parameter()
    total_cnt = luigi.Parameter()

    def requires(self):
        spark = get_spark(memory="2g")
        df = spark.read.parquet(
            "/home/nzhon/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors/v1"
        )
        labeled_neighborhood = get_knn_labels(df).cache()

        for i in range(23):
            pdf = get_subset_pdf(df, labeled_neighborhood, i)
            name = pdf.ego_primary_label.iloc[0]
            path = Path(self.output_path) / name
            path.mkdir(parents=True, exist_ok=True)

            yield ClusterPlotSingleSpecies(
                path=path,
                pdf=pdf,
                name=name,
            )


class ClusterPlotSingleSpecies(luigi.WrapperTask):
    path = luigi.Parameter()
    pdf = luigi.Parameter()
    name = luigi.Parameter()

    def requires(self):
        distance = DistancePlotTask(
            path=self.path,
            pdf=self.pdf,
        )
        yield distance

        ego_birdnet_label = EgoBirdnetLabelTask(
            path=self.path,
            pdf=self.pdf,
        )
        yield ego_birdnet_label

        knn_birdnet_label = KnnBirdnetLabelTask(
            path=self.path,
            pdf=self.pdf,
        )
        yield knn_birdnet_label

        push_data = Push(
            input_path=f"/home/nzhon/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1/{self.name}",
            output_path=f"data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1/{self.name}",
            parallelism=1,
            dynamic_requires=[distance, ego_birdnet_label, knn_birdnet_label],
        )
        yield push_data


class DistancePlotTask(luigi.Task):
    path = luigi.Parameter()
    pdf = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.path / "distances.png")

    def run(self):
        plot_distances(self.pdf)
        plt.savefig(f"{self.path}/distances.png")
        plt.close()


class EgoBirdnetLabelTask(luigi.Task):
    path = luigi.Parameter()
    pdf = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.path / "ego_birdnet_label.png")

    def run(self):
        emb = compute_embedding_2d(self.pdf)
        plot_embedding(self.pdf, emb, "ego_birdnet_label", 5)
        plt.savefig(f"{self.path}/ego_birdnet_label.png")
        plt.close()


class KnnBirdnetLabelTask(luigi.Task):
    path = luigi.Parameter()
    pdf = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.path / "knn_birdnet_label.png")

    def run(self):
        emb = compute_embedding_2d(self.pdf)
        plot_embedding(self.pdf, emb, "knn_birdnet_label", 5)
        plt.savefig(f"{self.path}/knn_birdnet_label.png")
        plt.close()
