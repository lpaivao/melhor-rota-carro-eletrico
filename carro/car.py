import paho.mqtt.client as mqtt
import json
import random
import time
from geopy.distance import geodesic
from geopy.distance import distance
import topics
import threading
import os


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


os.environ['TERM'] = 'xterm'

posto = {'id_posto': 0, 'latitude': -23.5440, 'longitude': -46.6340, 'fila': 5, 'vaga': True}


class Car:
    def __init__(self, id_carro, bateria, max_distance_per_charge, melhor_posto=posto, latitude=-23.5450,
                 longitude=-46.6355, fog_prefix="fog", fog_id=1):
        # Prefixo de qual nuvem o carro está no momento
        self.fog_prefix = fog_prefix
        # ID na nevoa
        self.fog_id = fog_id
        # Dicionário com as informações do melhor posto desde a última solicitação
        self.melhor_posto = melhor_posto
        # Variável booleana para indicar se tem um processo de envio de bateria baixa acontecendo
        self.boolean_enviando_bateria = False
        # Distância máxima que o carro pode percorrer com carga máxima
        self.max_distance_per_charge = max_distance_per_charge

        # Variável de controle para controlar o carro recarregando
        self.recarregando_carro = False

        self.id_carro = id_carro
        self.latitude = latitude
        self.longitude = longitude
        self.bateria = bateria

        # Configura cliente mqtt
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Conectado ao broker MQTT")
        topico_encher_bateria = f"{topics.BATTERY_RECHARGED}/{self.id_carro}"
        self.client.subscribe(topico_encher_bateria)

    def on_message(self, client, userdata, message):
        json_payload = message.payload.decode('utf-8')
        payload = json.loads(json_payload)

        if message.topic == f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}/{self.id_carro}":
            self.boolean_enviando_bateria = False
            self.melhor_posto = payload
            """
            Logo após o carro receber a resposta do melhor posto,
            ele vai se desinscrever do tópico no formato:
            fog/{id da névoa}/better_station/{id do carro},
            pois caso seja necessário ele mudar de névoa, ele não estará inscrito
            no tópico de uma névoa antiga
            """
            self.client.unsubscribe(f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}/{self.id_carro}")

            self.ocupar_vaga_posto(self.melhor_posto)

        elif message.topic == f"{topics.BATTERY_RECHARGED}/{self.id_carro}":
            contador = 30 - self.bateria
            self.bateria = int(payload["bateria"])
            self.latitude = payload["latitude"]
            self.longitude = payload["longitude"]
            for i in range(contador, 0, -1):
                print(f"Aguarde {i} segundos, recarregando o carro no Posto {self.melhor_posto['id_posto']}...")
                time.sleep(1)
                clear_screen()
            print("Carro recarregado! Bateria em 100%")
            time.sleep(3)
            self.recarregando_carro = False

    def ocupar_vaga_posto(self, melhor_posto):
        # Faz o carro ocupar vaga do posto
        id_posto = str(melhor_posto["id_posto"])
        topico_ocupar_vaga = f"{self.fog_prefix}/{self.fog_id}/incrise_line/{id_posto}"
        payload = {
            "id_carro": self.id_carro
        }
        payload = json.dumps(payload)
        self.client.publish(topico_ocupar_vaga, payload)

    def enviar_bateria_baixa(self):
        payload = {
            "id_carro": self.id_carro,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "max_distance_per_charge": self.max_distance_per_charge
        }
        """
            Quando o carro for se inscrever para receber a resposta
            de melhor posto da névoa, o tópico vai possuir o identificador
            da névoa e o id do carro:
            fog/{id da névoa}/better_station/{id do carro}
            exemplo: fog/1/better_station/1
        """
        topic_sub = f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}/{self.id_carro}"
        self.client.subscribe(topic_sub)
        self.boolean_enviando_bateria = True
        """
            Vai fazer a publicação no tópico com o seguinte formato:
            fog/{id da névoa}/low_battery
        """
        topico_pub = f"{self.fog_prefix}/{self.fog_id}/{topics.LOW_BATTERY}"
        payload = json.dumps(payload)
        self.client.publish(topico_pub, payload)
        while self.boolean_enviando_bateria:
            # self.client.publish(topico_pub, payload)
            time.sleep(0.5)
            # print(f"Esperando resposta de melhor posto no tópico {topic_sub}...")

    # Diminui a bateria quando o carro anda
    def diminui_bateria(self, distancia):
        # self.bateria -= round(distancia / self.max_distance_per_charge * 100, 2)
        self.bateria -= 1
        clear_screen()
        print(f"Carro se moveu! Bateria = {self.bateria}%")
        print(f"Posição atual: ({self.latitude}), ({self.longitude})")
        if self.melhor_posto is not None:
            print(f"Último melhor posto calculado: Posto {self.melhor_posto['id_posto']}")

    def parar(self):
        self.client.loop_stop()
        self.client.disconnect()

    # Move o carro de acordo com as coordenadas
    def mover(self, lat, lon):
        # Preserva coordenada antiga
        coordenada_a = (self.latitude, self.latitude)
        # Atualiza coordenada
        self.latitude += lat
        self.longitude += lon
        # Calcula quantos quilômetros o carro andou
        coordenada_b = (self.latitude, self.latitude)
        distancia = distance(coordenada_a, coordenada_b).km
        # Retorna a distancia
        return distancia

    def run(self):

        try:
            while self.bateria > 0:
                # Simula o carro andando aleatoriamente as coordenadas
                lat, lon = random.uniform(-0.0005, 0.0005), random.uniform(-0.0005, 0.0005)
                distancia = round(self.mover(lat, lon), 2)

                # Diminui a vida da bateria
                self.diminui_bateria(distancia)
                """
                    Verifica se a bateria está baixa e se já não 
                    tem um processamento de envio de bateria baixa
                """
                if self.bateria < 15 and not self.boolean_enviando_bateria:
                    thread = threading.Thread(target=self.enviar_bateria_baixa)
                    thread.start()
                    self.recarregando_carro = True
                    while self.recarregando_carro:
                        time.sleep(0.5)


                time.sleep(2)
        except KeyboardInterrupt:
            self.parar()


if __name__ == '__main__':
    carro = Car(1, 17, 200)
    time.sleep(1)
    carro.run()
