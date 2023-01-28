FROM gcr.io/kaggle-gpu-images/python:latest

# for rebuilding the requirements.txt
RUN pip install pip-tools
