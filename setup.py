import setuptools

setuptools.setup(
    name="birdclef-2023",
    version="0.9.0",
    description="Utilities for birdclef 2023",
    author="Anthony Miyaguchi",
    author_email="acmiyaguchi@gatech.edu",
    url="https://github.com/dsgt-birdclef/birdclef-2023",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "networkx",
        "pyspark",
        "scikit-learn",
        "umap-learn",
        "pynndescent",
        "librosa",
        "soundfile",
        "click",
        "tqdm",
        "pyarrow",
        "tensorflow",
        "torch",
        "pytorch-lightning",
        'importlib-metadata>=0.12;python_version<"3.8"',
    ],
    extras_require={
        "dev": [
            "pytest",
            "pre-commit",
            "jupyterlab",
            "nb_black @ git+https://github.com/dnanhkhoa/nb_black.git@be0c810503867abc4a5e9d05ba75a16fce57dfee",
        ],
        "workflow": [
            "luigi",
            "docker",
            "google-cloud-batch",
            "google-cloud-storage",
            "google-api-python-client",
            "httplib2",
            "google-auth",
            "pydub",
        ],
        "onnx": [
            "tf2onnx",
            "onnx",
            "onnxruntime",
        ],
    },
)
