# birdnet and mixit docker models

See [notes from the birdclef-eda-f22](https://github.com/dsgt-birdclef/birdclef-eda-f22/tree/main/users/acmiyaguchi) project.

### Data

Grab the entirety of the data from last year's bucket.

```bash
mkdir -p data/raw
gcloud storage cp -r gs://birdclef-2022/raw/birdclef-2022 data/raw
```

If you just want a subset of the data, consider the following:

```bash
suffix=raw/birdclef-2022/train_audio
species=afrsil1
mkdir -p data/${suffix}
gcloud storage cp -r gs://birdclef-2022/${suffix}/${species} data/${suffix}
```

### Configuring docker

Make sure to authenticate against the artifact repository.

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

Note that we include the `-u $(id -u):$(id -g)` flag throughout to avoid
permission issues between the container and the local user. This option may be
unnecessary on Mac or Windows, so adjust the commands as appropriate. For
simplicity, we opt to mount our data directory as a volume instead of
individually mounting directories.

### Durations

It turns out that it's valuable to have the durations of the training audio in
our metadata. The following script will generate a parquet file that we can use
to find this information as a preprocessing step.

```bash
python workflows/train_durations.py
gsutil -m cp data/processed/train_durations.parquet gs://birdclef-2023/data/processed/birdclef-2023/train_durations.parquet
```

### BirdNET

#### Building

We build the [BirdNET analyzer model](https://github.com/kahst/BirdNET-Analyzer), which relies on tensorflow.

```bash
docker-compose -f docker/docker-compose.birdnet.yml build
docker-compose -f docker/docker-compose.birdnet.yml push
```

#### Usage

We can mount our local paths into the container to run the scripts:

```bash
touch /tmp/error_log.txt
docker run --rm \
    -u $(id -u):$(id -g) \
    -v ${PWD}/data:/mnt/data \
    -v /tmp/error_log.txt:/error_log.txt \
    -e NUMBA_CACHE_DIR=/tmp \
    -it us-central1-docker.pkg.dev/birdclef-2023/birdclef-2023/birdnet:latest \
    analyze.py \
        --i /mnt/data/raw/birdclef-2022/train_audio/afrsil1 \
        --o /mnt/data/processed/birdclef-2022/birdnet/analysis/afrsil1 \
        --threads 4 \
        --rtype csv
```

Note the `NUMBA_CACHE_DIR` to avoid librosa/numba cache issues (see [this
stackoverflow
post](https://stackoverflow.com/questions/59290386/runtimeerror-at-cannot-cache-function-shear-dense-no-locator-available-fo)).
There are also error logs that get written to the code directory within the
container, and permission errors can cause some headaches.

See [2022-10-23-birdnet-exploration](https://github.com/dsgt-birdclef/birdclef-eda-f22/tree/main/users/acmiyaguchi/notebooks/2022-10-23-birdnet-exploration.ipynb) for an interactive introduction into using the docker images.

We put together a luigi script to generate analysis of all of the training data, given that training data from the kaggle competition exists under `data/raw/birdclef-2022/train_audio`.

```bash
python workflows/birdnet.py
```

See [2022-10-30-birdnet-analyze-v1](https://github.com/dsgt-birdclef/birdclef-eda-f22/tree/main/users/acmiyaguchi/notebooks/2022-10-30-birdnet-analyze-v1.ipynb) for a notebook that shows how to use the dataset.

### Bird MixIT

#### Building

Building the image is requires a bit more setup. We need to download the model checkpoints [as per the repository instructions](https://github.com/google-research/sound-separation/tree/master/models/bird_mixit):

```bash
mkdir -p data/raw/sound_separation
gcloud storage cp -r gs://gresearch/sound_separation/bird_mixit_model_checkpoints data/raw/sound_separation
```

To facilitate building the container, we upload the checkpoint files into our cloud storage bucket:

```bash
cd data/raw/sound_separation/
zip -r bird_mixit_model_checkpoints.zip bird_mixit_model_checkpoints/
```

Then we can build the docker image:

```bash
docker-compose -f docker/docker-compose.bird-mixit.yml build
docker-compose -f docker/docker-compose.bird-mixit.yml push
```

#### Usage

We can use the docker compose file to run a wrapper script, with predefined paths for volume mounting:

```bash
docker compose \
    -f docker/docker-compose.bird-mixit.yml \
    run -u $(id -u):$(id -g) \
    bird-mixit \
        python scripts/mixit_ogg_wrapper.py \
            --input /mnt/data/raw/birdclef-2022/train_audio/afrsil1/XC125458.ogg \
            --output /mnt/data/processed/birdclef-2022/mixit/afrisil1/XC125458.ogg \
            --model_name output_sources4 \
            --num_sources 4
```

We can manually write out the full command:

```bash
docker run --rm \
    -u $(id -u):$(id -g) \
    -v ${PWD}/data:/mnt/data \
    -it us-central1-docker.pkg.dev/birdclef-2023/birdclef-2023/bird-mixit:latest \
        python scripts/mixit_ogg_wrapper.py \
            --input /mnt/data/raw/birdclef-2022/train_audio/afrsil1/XC125458.ogg \
            --output /mnt/data/processed/birdclef-2022/mixit/afrisil1/XC125458.ogg \
            --model_name output_sources4 \
            --num_sources 4
```

We can also run this GPU support.

```bash
docker run --rm \
    --gpus=all \
    -u $(id -u):$(id -g) \
    -v ${PWD}/data:/mnt/data \
    -it us-central1-docker.pkg.dev/birdclef-2023/birdclef-2023/bird-mixit-gpu:latest \
        python scripts/mixit_ogg_wrapper.py \
            --input /mnt/data/raw/birdclef-2022/train_audio/afrsil1/XC125458.ogg \
            --output /mnt/data/processed/mixit/afrisil1/XC125458.ogg \
            --model_name output_sources4 \
            --num_sources 4
```

We put together a small script that will run the mixit model against all of the
files in a particular species directory, and additionally runs birdnet against
all of the resulting sound separated files.

```bash
./scripts/mixit_batch.sh chukar
python ./scripts/mixit_batch_concat.py \
    data/processed/mixit/analysis/chukar \
    data/raw/birdclef-2022 \
    data/processed/mixit/chukar_v1.parquet
```
