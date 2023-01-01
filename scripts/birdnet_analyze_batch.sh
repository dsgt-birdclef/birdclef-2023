#!/usr/bin/env bash

set -eo pipefail

n_threads=${N_THREADS:-8}

cd "$(dirname "$0")/.."

raw_prefix=data/raw/birdclef-2022/train_audio
processed_prefix=data/processed/birdnet/analysis
logs_file=data/processed/birdnet/batch_analysis.log

if [ -f "$logs_file" ]; then
    rm "$logs_file"
fi

for path in ${raw_prefix}/*; do
    species=$(basename $path)
    docker run --rm \
        -v ${PWD}/data:/mnt/data \
        -e NUMBA_CACHE_DIR=/tmp \
        -it us-central1-docker.pkg.dev/birdclef-eda-f22/birdclef-eda-f22/birdnet:latest \
        analyze.py \
        --i /mnt/${path} \
        --o /mnt/${processed_prefix}/${species} \
        --threads ${n_threads} \
        --rtype csv | tee -a ${logs_file}
done

echo "run: sudo chown -R $(id -u):$(id -g) ${processed_prefix}"
