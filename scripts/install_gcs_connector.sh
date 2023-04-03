#!/usr/bin/env bash
set -e

site_packages=$(python -c 'import site; print(site.getsitepackages()[0])')
lib_dir="${site_packages}/pyspark/jars"
cd "${lib_dir}"
wget https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar
