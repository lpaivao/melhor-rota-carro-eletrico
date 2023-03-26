FROM python:3.11-slim-buster

WORKDIR /flask
COPY . /flask
CMD ["python3","Flask.py"]