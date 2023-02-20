# Bird MixIT

## Building

Building the image is requires a bit more setup.
We need to download the model checkpoints [as per the repository instructions](https://github.com/google-research/sound-separation/tree/master/models/bird_mixit):

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

## Usage

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

We put together a small script that will run the mixit model against all of the files in a particular species directory, and additionally runs birdnet against all of the resulting sound separated files.

```bash
./scripts/mixit_batch.sh chukar
python ./scripts/mixit_batch_concat.py \
    data/processed/mixit/analysis/chukar \
    data/raw/birdclef-2022 \
    data/processed/mixit/chukar_v1.parquet
```
