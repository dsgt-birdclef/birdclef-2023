import json
from pathlib import Path

if __name__ == "__main__":
    root = Path(__file__).parent.parent / "data/processed/mixit/analysis"
    paths = list(root.glob("*/*.ogg"))
    # group each audio file by their prefix
    res = {}
    for path in paths:
        prefix = path.name.split("_")[0]
        if prefix not in res:
            res[prefix] = []
        res[prefix].append(path.relative_to(root).as_posix())

    base_url = (
        "https://storage.googleapis.com/birdclef-eda-f22/data/processed/mixit/analysis"
    )

    # generate a json file for the listing
    (root.parent / "listing.json").write_text(
        json.dumps(dict(base_url=base_url, files=res), indent=2)
    )
