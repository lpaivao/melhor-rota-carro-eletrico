FROM python:3.10.9-bullseye

WORKDIR /car

COPY . /car

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8080/tcp

CMD ["python","car.py"]