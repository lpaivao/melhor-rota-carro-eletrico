'''from flask import Flask
from car import Car
import os 
import dotenv
import time

app = Flask(__name__)

carro = Car(1, 16, 200)

time.sleep(2)

carro.run()

@app.route("/bateria")
def getBeteria():
    return carro.bateria'''