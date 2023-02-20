# luigi

This document describes the basic how-to of using luigi to run workflows.
See the official [luigi documentation](https://luigi.readthedocs.io/en/stable/index.html) for general usage and information.

## quickstart

The prototypical luigi workflow is a python script that defines a `Task` class.
Look at the [`workflows/train_durations.py`](../workflows/train_durations.py) script for a simple example.

We note that most of the tasks as of time of writing require pulling data from our cloud storage bucket for the raw training audio.
In the future, we will want to automate downloading data to the local machine (e.g. via `gsutil rync`), but for now, you will need to manually download the data to your local machine.

```bash
mkdir -p data/raw
gcloud storage cp -r gs://birdclef-2022/raw/birdclef-2022 data/raw
```

Now we can run the train durations task.
In one terminal, start the luigi scheduler:

```bash
luigid
```

Then run the following command:

```bash
python workflows/train_durations.py

# or more verbosely:
luigi \
    --module workflows.train_durations TrainDurations \
    --birdclef-root-path data/raw/birdclef-2022 \
    --output-path data/processed/birdclef-2022/train_durations.parquet \
    --local-scheduler
```

Forward port 8082 to view the luigi dashboard at http://localhost:8082.

You can also use the shared luigi instance to track and schedule tasks:

```bash
luigi \
    --module workflows.train_durations TrainDurations \
    --birdclef-root-path data/raw/birdclef-2022 \
    --output-path data/processed/birdclef-2022/train_durations.parquet \
    --scheduler-host luigi.us-central1-a.c.birdclef-2023.internal
```

Then you can visit https://luigi.dsgt-kaggle.org to view the luigi dashboard.
