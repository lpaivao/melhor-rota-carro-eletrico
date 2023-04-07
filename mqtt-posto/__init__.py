from flask import Flask
from flask_mqtt import Mqtt
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = os.getenv('MQTT_BROKER_URL')  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = int(os.getenv('MQTT_BROKER_PORT'))  # default port for non-tls connection
app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = int(os.getenv('MQTT_KEEPALIVE'))  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = bool(os.getenv('MQTT_TLS_ENABLED'))  # set TLS to disabled for testing purposes

mqtt = Mqtt(app)

@mqtt.on_connect()
def handle_connect():
    pass

