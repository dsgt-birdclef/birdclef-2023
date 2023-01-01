from argparse import ArgumentParser
from multiprocessing import Pool
from pathlib import Path

import librosa
import pandas as pd
from tqdm import tqdm


def read_path(path):
    y, sr = librosa.load(path)
    duration = librosa.get_duration(y=y, sr=sr)
    return dict(filename="/".join(path.parts[-2:]), duration=duration)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "birdclef_2022_root", type=str, help="BirdCLEF-2022 root directory."
    )
    parser.add_argument("output", type=str, help="Output file (parquet)")
    parser.add_argument("--parallelism", type=int, default=8)
    args = parser.parse_args()

    birdclef_root = Path(args.birdclef_2022_root)

    paths = sorted(birdclef_root.glob("train_audio/**/*.ogg"))

    res = []
    with Pool(args.parallelism) as pool:
        res = list(tqdm(pool.imap(read_path, paths), total=len(paths)))

    df = pd.DataFrame(res)
    print(df.head())
    df.to_parquet(args.output)


if __name__ == "__main__":
    main()
