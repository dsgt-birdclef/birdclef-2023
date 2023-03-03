import setuptools

setuptools.setup(
    name="birdclef-2023",
    version="0.5.0",
    description="Utilities for birdclef 2023",
    author="Anthony Miyaguchi",
    author_email="acmiyaguchi@gatech.edu",
    url="https://github.com/dsgt-birdclef/birdclef-2023",
    packages=setuptools.find_packages(),
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
        "pytorch-lightning",
        'importlib-metadata>=0.12;python_version<"3.8"',
    ],
    extras_require={"dev": ["pytest", "pre-commit"]},
)
