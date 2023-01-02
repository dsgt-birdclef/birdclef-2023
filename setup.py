import setuptools

setuptools.setup(
    name="birdclef-2023",
    version="0.1.0",
    description="Utilities for birdclef 2023",
    author="Anthony Miyaguchi",
    author_email="acmiyaguchi@gatech.edu",
    url="https://github.com/dsgt-birdclef/birdclef-2023",
    packages=["birdclef"],
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "pyspark",
        "scikit-learn",
        "umap-learn",
        "pynndescent",
        "librosa",
        "soundfile",
        "click",
        "tqdm",
        "pyarrow",
        "torch",
        "nnAudio",
        "pytorch-lightning",
        "torch-audiomentations",
        "torch-summary",
        "audiomentations",
        'importlib-metadata>=0.12;python_version<"3.8"',
    ],
)
