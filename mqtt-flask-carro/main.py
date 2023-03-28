from flask import Flask, request
from flask_mqtt import Mqtt
from dotenv import load_dotenv
import entities as Ent
import json,os

app = Flask(__name__)

load_dotenv()

#flask constantes


app.config['MQTT_BROKER_URL'] = os.environ['HOST_BROKER']
app.config['MQTT_BROKER_PORT'] = int(os.environ['PORT_BROKER'])
app.config['MQTT_USERNAME'] =''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLE'] = False

mqtt = Mqtt(app)



# Chave = placa do carro
# Valor = objeto CarroEletrico do arquivo Entities.py
carros_dict = {}


@app.route('/bateria')
def estado_bateria():
    placa = request.args.get('placa')
    if placa in carros_dict.keys():
        response = "Bateria:{}% ".format(str(carros_dict[placa].bateria))
        return response

@mqtt.on_connect()
def handle_connection(client,userdata,flags,rc):
    mqtt.subscribe('teste/teste')


@mqtt.on_message()
def handle_mqtt_menssage(client,userdata,message):
    data = dict(topic = message.topic, paylod=message.payload.decode())
    print(data)

if __name__ == '__main__':
    app.run()
