import time
import paho.mqtt.client as mqtt
from random import randint
import topics
import functions
import json

# fila = quantos carros tem na fila
# espera = tempo de espera
postos_disponiveis = {
    '0': {'id_posto': 0, 'latitude': -23.5440, 'longitude': -46.6340, 'fila': 0, 'vaga': True},
    '1': {'id_posto': 1, 'latitude': -23.5450, 'longitude': -46.6350, 'fila': 2, 'vaga': True},
    '2': {'id_posto': 2, 'latitude': -23.5560, 'longitude': -46.6360, 'fila': 3, 'vaga': True}
}


class Fog:
    def __init__(self, fog_prefix="fog", fog_id=1, postos=postos_disponiveis):
        # Prefixo de qual nuvem o carro está no momento
        self.fog_prefix = fog_prefix
        # ID na nevoa
        self.fog_id = fog_id
        # Dicionário de postos da névoa
        self.postos = postos
        # Ponto central entre todos os postos
        self.ponto_central = None

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        # self.client.loop_start()
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print(f'Conectado ao Broker! Código de retorno {rc}')
        client.subscribe(f"{self.fog_prefix}/{self.fog_id}/{topics.LOW_BATTERY}")
        client.subscribe(f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}")
        client.subscribe(f"{self.fog_prefix}/{self.fog_id}/{topics.ALT_STATION}")

        client.subscribe(f"{self.fog_prefix}/{self.fog_id}/{topics.FOG_CHANGE}")
        client.subscribe(f"{self.fog_prefix}/{self.fog_id}/{topics.CLOUD_RESPONSE_FOG}")
        self.ponto_central = functions.calcular_ponto_central(self.postos)
        print(f"A localização central é: {self.ponto_central.latitude}, {self.ponto_central.longitude}")
        self.subscribe_all_stations()

    def on_message(self, client, data, message):
        topic = message.topic.split('/')
        # Decodifica a mensagem e transforma o objeto JSON em string python
        msg = message.payload.decode()
        msg = json.loads(msg)
        # print(message.topic)
        # print(f"mensagem recebida:{msg}")

        if topic[0] == str(self.fog_prefix):

            if topic[1] == str(self.fog_id):

                if topic[2] == "vaga_status":
                    id_posto = str(msg["id_posto"])
                    fila = msg["fila"]
                    self.postos[id_posto]["fila"] = fila

                elif topic[2] == "alocando_carro":
                    id_posto = str(msg["id_posto"])
                    vaga = msg["vaga"]
                    self.postos[id_posto]["vaga"] = vaga
                    self.postos[id_posto]["vaga"] = vaga

                elif topic[2] == topics.LOW_BATTERY:
                    id_carro = msg["id_carro"]
                    latitude = msg["latitude"]
                    longitude = msg["longitude"]
                    max_distance_per_charge = msg["max_distance_per_charge"]
                    nome_mais_proximo, posto_mais_proximo, distancia_mais_proximo = \
                        functions.calcular_posto_mais_proximo_menor_fila(self.postos,
                                                                         latitude,
                                                                         longitude,
                                                                         max_distance_per_charge)

                    # Transforma em objeto json
                    payload = json.dumps(posto_mais_proximo)
                    """
                        Quando a névoa fizer publish para o carro com bateria baixa,
                        ele vai responder no topico que contém o identificador da névoa
                        e o id do carro:
                        fog/{id da névoa}/better_station/{id do carro}
                        exemplo: fog/1/better_station/1
                    """
                    topico_pub = f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}/{id_carro}"
                    client.publish(topico_pub, payload)

                elif topic[2] == topics.ALT_STATION:
                    id_carro = msg["id_carro"]
                    id_posto = msg["id_posto"]
                    latitude = msg["latitude"]
                    longitude = msg["longitude"]
                    max_distance_per_charge = msg["max_distance_per_charge"]
                    posto_disponivel = \
                        functions.calcular_posto_disponivel(self.postos,
                                                            id_posto,
                                                            latitude,
                                                            longitude,
                                                            max_distance_per_charge)

                    # Transforma em objeto json
                    payload = json.dumps(posto_disponivel)
                    """
                        Quando a névoa fizer publish para o carro com bateria baixa,
                        ele vai responder no topico que contém o identificador da névoa
                        e o id do carro:
                        fog/{id da névoa}/better_station/{id do carro}
                        exemplo: fog/1/better_station/1
                    """
                    topico_pub = f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}/{id_carro}"
                    client.publish(topico_pub, payload)

                elif topic[2] == topics.FOG_CHANGE:
                    id_carro = msg["id_carro"]
                    latitude = msg["latitude"]
                    longitude = msg["longitude"]
                    max_distance_per_charge = msg["max_distance_per_charge"]

                    payload = {
                        "id_carro": id_carro,
                        "latitude": latitude,
                        "longitude": longitude,
                        "max_distance_per_charge": max_distance_per_charge,
                        "fog_id": self.fog_id,
                        "ponto_central": self.ponto_central
                    }

                    payload = json.dumps(payload)
                    topic_pub = f"cloud/{topics.FOG_CHANGE}"
                    self.client.publish(topic_pub, payload)

                elif topic[2] == topics.CLOUD_RESPONSE_FOG:
                    id_carro = msg["id_carro"]
                    new_fog_id = msg["new_fog_id"]
                    payload = {
                        "id_carro": id_carro,
                        "new_fog_id": new_fog_id,
                    }

                    payload = json.dumps(payload)
                    topic_pub = f"{self.fog_prefix}/{self.fog_id}/{topics.FOG_CHANGE}/{self.fog_id}"
                    self.client.publish(topic_pub, payload)

    def subscribe_all_stations(self):
        for posto in self.postos:
            self.client.subscribe(f'{self.fog_prefix}/{self.fog_id}/vaga_status/{self.postos[posto]["id_posto"]}')
            # self.client.subscribe(f'{self.fog_prefix}/{self.fog_id}/incrise_line/{self.postos[posto]["id_posto"]}')
            self.client.subscribe(f'{self.fog_prefix}/{self.fog_id}/alocando_carro/{self.postos[posto]["id_posto"]}')

        print("Inscrito em todos os postos")


if __name__ == '__main__':
    fog = Fog()
