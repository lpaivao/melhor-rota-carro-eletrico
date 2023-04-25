FROM python:3.10.9-bullseye

WORKDIR /carro

COPY . /carro

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python","car.py"]