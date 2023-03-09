# BirdNET

## Building

We build the [BirdNET analyzer model](https://github.com/kahst/BirdNET-Analyzer), which relies on tensorflow.

```bash
docker-compose -f docker/docker-compose.birdnet.yml build
docker-compose -f docker/docker-compose.birdnet.yml push
```

## Usage

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

Note the `NUMBA_CACHE_DIR` to avoid librosa/numba cache issues (see [this stackoverflow post](https://stackoverflow.com/questions/59290386/runtimeerror-at-cannot-cache-function-shear-dense-no-locator-available-fo)).
There are also error logs that get written to the code directory within the container, and permission errors can cause some headaches.

See [2022-10-23-birdnet-exploration](https://github.com/dsgt-birdclef/birdclef-eda-f22/tree/main/users/acmiyaguchi/notebooks/2022-10-23-birdnet-exploration.ipynb) for an interactive introduction into using the docker images.

We put together a luigi script to generate analysis of all of the training data, given that training data from the kaggle competition exists under `data/raw/birdclef-2022/train_audio`.

```bash
python workflows/birdnet.py
```

See [2022-10-30-birdnet-analyze-v1](https://github.com/dsgt-birdclef/birdclef-eda-f22/tree/main/users/acmiyaguchi/notebooks/2022-10-30-birdnet-analyze-v1.ipynb) for a notebook that shows how to use the dataset.
