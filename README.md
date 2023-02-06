# birdclef-2023

Code for the BirdCLEF 2023 competition with members of DS@GT.

Some code from the [birdclef-eda-f22](https://github.com/dsgt-birdclef/birdclef-eda-f22) and [birdclef-2022](https://github.com/dsgt-birdclef/birdclef-2022) repositories was used.

| namespace         | url                                        |
| ----------------- | ------------------------------------------ |
| prod (live alias) | https://birdclef-2023.dsgt-kaggle.org      |
| live              | https://birdclef-2023.live.dsgt-kaggle.org |
| next              | https://birdclef-2023.next.dsgt-kaggle.org |

## quickstart

### python

Install Python 3.7 or above.
Install dependencies using pip.

```bash
pip install pip-tools
pip install pre-commit
```

Install the pre-commit hooks.
This will ensure that all the code is formatted correctly.

```bash
pre-commit install
```

Create a new virtual environment and activate it.

```bash
# create a virtual environment in the venv/ directory
python -m venv venv

# activate on Windows
./venv/Scripts/Activate.ps1

# activate on Linux/MacOS
source venv/bin/activate
```

Then install all of the dependencies.

```bash
pip install -r requirements.txt
```

[pip-tools]: https://github.com/jazzband/pip-tools
[pre-commit]: https://pre-commit.com/

### running tests

Unit-testing helps with debugging smaller modules in a larger project.
For example, we use tests to assert that models accept data in one shape and output predictions in another shape.
We use [pytest] in this project.
Running the tests can help ensure that your environment is configured correctly.

```bash
pytest -vv tests/
```

You can select a subset of tests using the `-k` flag.

```bash
pytest -vv tests/ -k <test-name-fragment>
```

You can also exit tests early using the `-x` flag and enter a debugger on
failing tests using the `--pdb` flag.

[pytest]: https://docs.pytest.org/en/7.1.x/

### adding dependencies

This repository uses `pip-compile` to maintain dependencies.
Please add direct dependencies to `requirements.in`, rather than modifying `requirements.txt`.
After adding a dependency, run `pip-compile` to generate a new `requirements.txt` file.
The sequence looks something like:

```bash
# if you haven't installed it already via the quickstart guide
pipx install pip-tools

# add any new direct dependencies to requirements.in
pip-compile
# observe that requirements.txt has changed locally
# commit the result
```

### syncing data

Currently data is synchronized manually into a google cloud storage bucket.

```bash
gsutil -m rsync -r data/raw/ gs://birdclef-2023/data/raw/
gsutil -m rsync -r data/processed/ gs://birdclef-2023/data/processed/

# NOTE: to sync the other way, just reverse the order of the arguments
gsutil -m rsync -r gs://birdclef-2023/data/processed/ data/processed/
```
