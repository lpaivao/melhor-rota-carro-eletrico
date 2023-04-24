FROM python:3.10.9-bullseye

WORKDIR /nevoa

COPY . /nevoa

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 9090

CMD ["python","fog.py"]