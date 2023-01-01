from argparse import ArgumentParser, Namespace
from multiprocessing import Pool
from pathlib import Path

import librosa
import pandas as pd
from tqdm import tqdm
import os


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("birdclef_root", type=str, help="BirdCLEF root directory.")
    parser.add_argument("output", type=str, help="Output file (parquet)")
    parser.add_argument(
        "--parallelism",
        type=int,
        default=os.cpu_count(),
        help="Number of parallel processes to use.",
    )
    return parser.parse_args()


def read_path(path: Path) -> dict:
    y, sr = librosa.load(path)
    duration = librosa.get_duration(y=y, sr=sr)
    return dict(filename="/".join(path.parts[-2:]), duration=duration)


def main():
    args = parse_args()
    birdclef_root = Path(args.birdclef_root)
    paths = sorted(birdclef_root.glob("train_audio/**/*.ogg"))
    with Pool(args.parallelism) as pool:
        res = list(tqdm(pool.imap(read_path, paths), total=len(paths)))

    df = pd.DataFrame(res)
    print(df.head())
    # ensure the output directory exists
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.output)


if __name__ == "__main__":
    main()
