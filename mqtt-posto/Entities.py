import paho.mqtt.client as mqtt
import json
import Constantes as Const
import queue


class Posto:
    def __init__(self):
        self.fila = queue.Queue()  # Fila de carros no posto


class MQTTConn:
    def __init__(self, host=Const.BROKER, port=Const.PORT_BROKER):
        self.host = host
        self.port = port
        self.client = mqtt.Client()

    def connect(self):
        self.client.connect(self.host, self.port)

    def desconnect(self):
        self.client.disconnect()

    def publish(self, topic, mensagem, qos=0, retain=False):
        self.client.publish(topic, payload=mensagem, qos=qos, retain=retain)

    def subscribe(self, topic, on_message_callback=None, qos=0):
        if on_message_callback:
            self.client.on_message = on_message_callback

        self.client.subscribe(topic, qos)
        self.client.loop_start()

    def set_callback(self, on_message_callback):
        self.client.on_message = on_message_callback
