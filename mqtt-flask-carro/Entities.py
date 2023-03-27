import paho.mqtt.client as mqtt
import json
import Constantes as Const
import queue


class CarroEletrico:
    def __init__(self, placa, x, y):
        self.placa = placa
        self.x = x
        self.y = y
        self.bateria = 100

    def mover_para(self, x, y):
        if self.nivel_bateria > 0:
            self.x = x
            self.y = y
            self.bateria -= 1
            print("Carro movido para as coordenadas ({}, {})".format(x, y))
        else:
            print("Nível de bateria insuficiente para mover o carro.")

    def recarregar_bateria(self):
        self.bateria = 100
        print("Bateria recarregada.")


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
