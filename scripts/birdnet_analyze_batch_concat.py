from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def read_path(path, lookup=lambda x: x):
    df = pd.read_csv(path)
    name = path.name.split(".")[0]
    df["filename"] = f"{path.parent.name}/{name}.ogg"
    df["birdnet_label"] = df["Common name"].apply(lambda x: lookup(x, "unknown"))
    df["birdnet_common_name"] = df["Common name"]
    return df


def main():
    parser = ArgumentParser()
    parser.add_argument("input", type=str, help="Input directory.")
    parser.add_argument(
        "birdclef_2022_root", type=str, help="BirdCLEF-2022 root directory."
    )
    parser.add_argument("output", type=str, help="Output file (parquet)")
    parser.add_argument("--parallelism", type=int, default=8)
    args = parser.parse_args()

    root = Path(args.input)
    birdclef_root = Path(args.birdclef_2022_root)
    taxonomy_df = pd.read_csv(birdclef_root / "eBird_Taxonomy_v2021.csv")
    common_to_code = dict(
        list(zip(taxonomy_df["PRIMARY_COM_NAME"], taxonomy_df["SPECIES_CODE"]))
    )

    paths = sorted(root.glob("**/*.csv"))

    res = []
    with Pool(args.parallelism) as pool:
        res = list(
            tqdm(
                pool.imap(partial(read_path, lookup=common_to_code.get), paths),
                total=len(paths),
            )
        )

    df = pd.concat(res).rename(
        columns={
            "Start (s)": "start_sec",
            "End (s)": "end_sec",
            "Confidence": "confidence",
        }
    )[
        [
            "start_sec",
            "end_sec",
            "confidence",
            "birdnet_label",
            "birdnet_common_name",
            "filename",
        ]
    ]
    df.to_parquet(args.output)


if __name__ == "__main__":
    main()
