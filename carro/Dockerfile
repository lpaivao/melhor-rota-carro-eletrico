FROM python:3-alpine

COPY . /car

WORKDIR /car

RUN pip install -r requirements.txt

EXPOSE 8080/tcp

CMD ["python","car.py"]