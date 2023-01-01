#!/usr/bin/env bash
set -eo pipefail

n_threads=${N_THREADS:-8}

species=${1:?Please provide a species name.}

cd "$(dirname "$0")/.."
raw_prefix=data/raw/birdclef-2022/train_audio
processed_prefix=data/processed/mixit/analysis
logs_file=data/processed/mixit/analysis/batch_analysis_${species}.log

mkdir -p $(dirname ${logs_file})

if [ -f "$logs_file" ]; then
    rm "$logs_file"
fi

for path in ${raw_prefix}/${species}/*.ogg; do
    echo "$(date --iso-8601=seconds) Processing ${path}" | tee -a ${logs_file}
    audio_file=$(basename $path)
    docker run --rm \
        --gpus=all \
        -v ${PWD}/data:/mnt/data \
        -it us-central1-docker.pkg.dev/birdclef-eda-f22/birdclef-eda-f22/bird-mixit-gpu:latest \
        python scripts/mixit_ogg_wrapper.py \
        --input /mnt/${path} \
        --output /mnt/${processed_prefix}/${species}/${audio_file} \
        --model_name output_sources4 \
        --num_sources 4 | tee -a ${logs_file}
done

# now run birdnet on the output of mixit
docker run --rm \
    -v ${PWD}/data:/mnt/data \
    -it us-central1-docker.pkg.dev/birdclef-eda-f22/birdclef-eda-f22/birdnet:latest \
    analyze.py \
    --i /mnt/${processed_prefix}/${species} \
    --o /mnt/${processed_prefix}/${species} \
    --threads ${n_threads} \
    --rtype csv | tee -a ${logs_file}
