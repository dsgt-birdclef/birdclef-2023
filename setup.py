import setuptools

setuptools.setup(
    name="birdclef-2023",
    version="0.1.0",
    description="Utilities for birdclef 2023",
    author="Anthony Miyaguchi",
    author_email="acmiyaguchi@gatech.edu",
    url="https://github.com/dsgt-birdclef/birdclef-2023",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "librosa",
        "soundfile",
        "click",
        "tqdm",
        "pyarrow",
        "torch",
        "pyspark",
        "nnAudio",
        "pytorch-lightning",
        "torch-audiomentations",
        "torch-summary",
        "audiomentations",
        'importlib-metadata>=0.12;python_version<"3.8"',
    ],
)
