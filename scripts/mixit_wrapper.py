import argparse
import shutil
from pathlib import Path
from subprocess import run


def cleanup_tmp():
    for p in Path("/tmp").glob("*.wav"):
        p.unlink()


def main():
    """A wrapper for the mixit parse_wav.py script.

    This takes an input file (generally an ogg file) and creates a wav file in a
    temporary location using ffmpeg. It also converts the audio back to the
    original source.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file.", required=True, type=str)
    parser.add_argument("-o", "--output", help="Output file.", required=True, type=str)
    parser.add_argument("--output_format", help="Output format.", default="ogg")
    parser.add_argument(
        "--model_name",
        type=str,
        choices=["output_sources4", "output_sources8"],
        required=True,
    )
    parser.add_argument("--sound_separation_root", type=str, default="/app")
    parser.add_argument("--model_dir", type=str, default="/app/checkpoints")
    args, other_args = parser.parse_known_args()

    if args.output_format not in ["ogg", "mp3"]:
        raise ValueError(f"Invalid output format: {args.output_format}")

    cleanup_tmp()
    input_path = Path(args.input)
    tmp_input = f"/tmp/{input_path.name.split('.')[0]}.wav"
    if input_path.suffix == ".wav":
        shutil.copyfile(input_path, tmp_input)
    else:
        run(f"ffmpeg -y -i {input_path} {tmp_input}".split())

    model_dir = f"{args.model_dir}/{args.model_name}"
    output_name = Path(args.output).name.split(".")[0]
    cmd = [
        "python3",
        f"{args.sound_separation_root}/models/tools/process_wav.py",
        "--model_dir",
        model_dir,
        "--checkpoint",
        (
            next(Path(model_dir).glob("model.ckpt-*.index"))
            .as_posix()
            .replace(".index", "")
        ),
        "--input",
        tmp_input,
        "--output",
        f"/tmp/{output_name}.wav",
        *other_args,
    ]
    print(" ".join(cmd))
    run(cmd)

    # for each of the output files, copy them into the output directory
    output_path = Path(args.output).parent
    if not output_path.exists():
        output_path.mkdir(parents=True)
    for p in Path("/tmp").glob(f"{output_name}_source*.wav"):
        if args.output_format == "ogg":
            output = output_path / p.name.replace("wav", "ogg")
            run(f"ffmpeg -y -i {p} -acodec libvorbis {output}".split())
        elif args.output_format == "mp3":
            output = output_path / p.name.replace("wav", "mp3")
            run(f"ffmpeg -y -i {p} -acodec libmp3lame -q:a 5 {output}".split())

    cleanup_tmp()


if __name__ == "__main__":
    main()
