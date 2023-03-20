#!/usr/bin/env bash
set -eo pipefail

gpu_enabled=${GPU_ENABLED:-0}
n_threads=${N_THREADS:-8}

species=${1:?Please provide a species name.}
birdclef_name=${2:-birdclef-2023}


cd "$(dirname "$0")/.."
raw_prefix=data/raw/${birdclef_name}/train_audio
processed_prefix=data/processed/${birdclef_name}/mixit/analysis
logs_file=data/processed/${birdclef_name}/mixit/analysis/batch_analysis_${species}.log

gsutil -m rsync -r \
    gs://birdclef-2023/${raw_prefix}/${species}/ \
    ${raw_prefix}/${species}/

mkdir -p $(dirname ${logs_file})

if [ -f "$logs_file" ]; then
    rm "$logs_file"
fi

for path in ${raw_prefix}/${species}/*.ogg; do
    echo "$(date --iso-8601=seconds) Processing ${path}" | tee -a ${logs_file}
    audio_file=$(basename $path)
    docker run --rm \
        $(if [[ ! $gpu_enabled -eq 0 ]]; then echo "--gpus=all"; fi) \
        -v ${PWD}/data:/mnt/data \
        -it us-central1-docker.pkg.dev/birdclef-2023/birdclef-2023/bird-mixit-gpu:latest \
        python scripts/mixit_ogg_wrapper.py \
        --input /mnt/${path} \
        --output /mnt/${processed_prefix}/${species}/${audio_file} \
        --model_name output_sources4 \
        --num_sources 4 | tee -a ${logs_file}
done
