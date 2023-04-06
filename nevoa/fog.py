import time

import paho.mqtt.client as mqtt
from random import randint
import topics
import functions
import json

# fila = quantos carros tem na fila
# espera = tempo de espera
postos_disponiveis = {
    'Posto A': {'latitude': -23.5440, 'longitude': -46.6340, 'fila': 5, 'espera': 5},
    'Posto B': {'latitude': -23.5450, 'longitude': -46.6350, 'fila': 2, 'espera': 3},
    'Posto C': {'latitude': -23.5560, 'longitude': -46.6360, 'fila': 3, 'espera': 1}
}


class Fog:
    def __init__(self, fog_prefix, id=randint(0, 10000), broker_host='localhost', broker_port=1883,
                 nuvem_host='localhost', nuvem_port=6666, postos=postos_disponiveis):
        # Prefixo de qual nuvem o carro está no momento
        self.fog_prefix = fog_prefix
        # Dicionário de postos da névoa
        self.postos = postos

        self.id = id
        self.broker_host = broker_host
        self.broke_port = broker_port
        self.nuvem_host = nuvem_host
        self.nuvem_port = nuvem_port

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        # self.client.loop_start()
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print(f'Conectado ao Broker! Código de retorno {rc}')
        client.subscribe(f"{self.fog_prefix}/{topics.LOW_BATTERY}")
        client.subscribe(f"{self.fog_prefix}/{topics.BETTER_STATION}")

    def on_message(self, client, data, message):
        topic = message.topic.split('/')
        # Decodifica a mensagem e transforma o objeto JSON em string python
        msg = message.payload.decode()
        msg = json.loads(msg)
        print(f"mensagem recebida:{msg}")

        if topic[1] == topics.LOW_BATTERY:
            id_carro = msg["id_carro"]
            latitude = msg["latitude"]
            longitude = msg["longitude"]
            max_distance_per_charge = msg["max_distance_per_charge"]
            nome_mais_proximo, posto_mais_proximo, distancia_mais_proximo = \
                functions.calcular_posto_mais_proximo_mais_rapido(self.postos,
                                                                  latitude,
                                                                  longitude,
                                                                  max_distance_per_charge)

            # Transforma em objeto json
            payload = json.dumps(posto_mais_proximo)
            """
                Quando a névoa fizer publish para o carro com bateria baixa,
                ele vai responder no topico que contém o identificador da névoa
                e o id do carro:
                {nome da névoa}/better_station/{id do carro}
                exemplo: fog1/better_station/1
            """
            topico_pub = f"{self.fog_prefix}/{topics.BETTER_STATION}/{id_carro}"
            client.publish(topico_pub, payload)

if __name__ == '__main__':
    fog = Fog("fog1")
