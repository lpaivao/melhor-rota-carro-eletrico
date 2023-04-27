FROM python:3.11-alpine

COPY . /car

WORKDIR /car

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python","car.py"]