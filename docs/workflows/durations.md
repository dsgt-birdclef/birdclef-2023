# durations

It turns out that it's valuable to have the durations of the training audio in our metadata.
The following script will generate a parquet file that we can use to find this information as a preprocessing step.

```bash
python workflows/train_durations.py
gsutil -m cp data/processed/train_durations.parquet gs://birdclef-2023/data/processed/birdclef-2023/train_durations.parquet
```
