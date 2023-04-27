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

posto = {'id_posto': 0, 'latitude': -23.5440,
         'longitude': -46.6340, 'fila': 0, 'vaga': True}


# Função que será executada se o tempo limite for atingido
def on_timeout(self):
    print("Tempo limite de resposta excedido.")


class Car:
    def __init__(self, id_carro, bateria, max_distance_per_charge, melhor_posto=posto, latitude=-23.5450,
                 longitude=-46.6355, fog_prefix="fog", fog_id=1, BROKER_HOST="localhost", BROKER_PORT=1883):
        # Prefixo de qual nuvem o carro está no momento
        self.fog_prefix = fog_prefix
        # ID na nevoa
        self.fog_id = fog_id
        # Dicionário com as informações do melhor posto desde a última solicitação
        self.melhor_posto = melhor_posto

        self.carro_pode_andar = False
        self.posto_respondeu = False
        # Distância máxima que o carro pode percorrer com carga máxima
        self.max_distance_per_charge = max_distance_per_charge

        self.id_carro = id_carro
        self.latitude = latitude
        self.longitude = longitude
        self.bateria = bateria

        # Configura cliente mqtt
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_HOST, BROKER_PORT, 60)
        # Socket para se comunicar com a nuvem
        self.server = None

        # Start
        self.client.loop_start()
        # self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Conectado ao broker MQTT")
        topico_encher_bateria = f"{topics.BATTERY_RECHARGED}/{self.id_carro}"
        self.client.subscribe(topico_encher_bateria)
        self.client.subscribe(f"cloud/{topics.FOG_CHANGE}/{self.id_carro}")
        """
            Quando o carro for se inscrever para receber a resposta
            de melhor posto da névoa, o tópico vai possuir o identificador
            da névoa e o id do carro:
            fog/{id da névoa}/better_station/{id do carro}
            exemplo: fog/1/better_station/1
        """
        self.client.subscribe(
            f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}/{self.id_carro}")

        # Teste
        # topico_ocupar_vaga = f"{self.fog_prefix}/{self.fog_id}/increase_line/0"
        # message = {"id_carro": 1}
        # self.client.publish(topico_ocupar_vaga, json.dumps(message))

    def on_message(self, client, userdata, message):
        json_payload = message.payload.decode('utf-8')
        payload = json.loads(json_payload)
        print(f"TOPICO:{message.topic}")

        # Tópico de melhor posto
        if message.topic == f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}/{self.id_carro}":
            if payload["id_posto"] == -1:
                print("Nenhum posto disponível na névoa, tentando em outra...")
                self.mudar_nevoa()
            else:
                self.melhor_posto = payload
                print(
                    f"Posto encontrado! Tentativa de ocupar vaga do posto [{self.melhor_posto['id_posto']}]...")

                self.ocupar_vaga_posto(self.melhor_posto)

        # Tópico de recarregar bateria
        elif message.topic == f"{topics.BATTERY_RECHARGED}/{self.id_carro}":
            contador = 30 - self.bateria
            # self.bateria = int(payload["bateria"])
            self.bateria = 20
            self.latitude = payload["latitude"]
            self.longitude = payload["longitude"]

            for i in range(10, 0, -1):
                print(
                    f"Aguarde {i} segundos, recarregando o carro no Posto {self.melhor_posto['id_posto']}...")
                time.sleep(1)
                # clear_screen()

            print("Carro recarregado! Bateria em 100%")
            self.carro_pode_andar = True

        # Tópico de mudança de névoa
        elif message.topic == f"cloud/{topics.FOG_CHANGE}/{self.fog_id}":
            # Desinscreve do tópico da névoa antiga de melhor posto
            try:
                self.client.unsubscribe(
                    f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}/{self.id_carro}")
            except:
                pass
            # Atualiza o id da névoa
            old_fog_id = self.fog_id
            new_fog_id = payload["fog_id"]
            self.fog_id = new_fog_id
            self.client.subscribe(f"{self.fog_prefix}/{self.fog_id}/{topics.BETTER_STATION}/{self.id_carro}")
            print(
                f"Névoa atualizada!\nNévoa antiga:[{old_fog_id}] | Névoa atual:[{self.fog_id}]")
            time.sleep(3)
            self.carro_pode_andar = True

    def mudar_nevoa(self):
        print("Carro vai mudar de névoa...")

        payload = {
            "id_carro": self.id_carro,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "max_distance_per_charge": self.max_distance_per_charge,
        }

        topic_pub = f"{self.fog_prefix}/{self.fog_id}/{topics.FOG_CHANGE}"
        payload = json.dumps(payload)

        self.client.publish(topic_pub, payload)

    def envia_bateria_baixa(self):
        print("Carro enviando bateria baixa...")
        payload = {
            "id_carro": self.id_carro,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "max_distance_per_charge": self.max_distance_per_charge
        }
        """
            Vai fazer a publicação no tópico com o seguinte formato:
            fog/{id da névoa}/low_battery
        """
        topico_pub = f"{self.fog_prefix}/{self.fog_id}/{topics.LOW_BATTERY}"
        payload = json.dumps(payload)
        self.client.publish(topico_pub, payload)

        # Inicia o temporizador
        # self.timer1 = threading.Timer(30, on_timeout)
        # self.timer1.start()

        # Tempo até o servidor responder, senão o carro envia outro aviso
        # time.sleep(60)
        # Se o carro não estiver tentando ocupar um posto depois de alguns segundos, vai enviar outro aviso de bateria baixa
        # if not self.tentando_ocupar_posto:

    def ocupar_vaga_posto(self, melhor_posto):
        self.tentando_ocupar_posto = True
        # Faz o carro ocupar vaga do posto
        id_posto = str(melhor_posto["id_posto"])
        topico_ocupar_vaga = f"{self.fog_prefix}/{self.fog_id}/increase_line/{id_posto}"
        # topico_ocupar_vaga = f"{self.fog_prefix}/{self.fog_id}/increase_line/0"
        payload = {
            "id_carro": self.id_carro
        }
        payload = json.dumps(payload)
        self.client.publish(topico_ocupar_vaga, payload)
        print(f"Mensagem de ocupar vaga publicada em {topico_ocupar_vaga}")

        # Tempo limite de resposta
        # time.sleep(5)
        # if self.tentando_ocupar_posto:
        #    print(f"Tempo de espera de resposta atingiu o limite, sem resposta do posto {id_posto}")
        #    self.encontrar_outro_posto(id_posto)
        # else:
        #    print("else")

    def encontrar_outro_posto(self, id_posto):
        print(f"Tentando encontrar outro posto...")
        payload = {
            "id_carro": self.id_carro,
            "id_posto": id_posto,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "max_distance_per_charge": self.max_distance_per_charge
        }
        """
            Vai fazer a publicação no tópico com o seguinte formato:
            fog/{id da névoa}/alt_station
        """
        topico_pub = f"{self.fog_prefix}/{self.fog_id}/{topics.ALT_STATION}"
        payload = json.dumps(payload)
        self.client.publish(topico_pub, payload)

        # Tempo máximo de espera de resposta do posto
        time.sleep(10)
        # Se o carro não estiver recarregando o carro depois de alguns segundos, o carro vai pedir de novo o posto principal
        if not self.carro_pode_andar:
            print("Tentativa de achar outro posto falhou...")

    # Diminui a bateria quando o carro anda
    def diminui_bateria(self, distancia):
        # self.bateria -= round(distancia / self.max_distance_per_charge * 100, 2)
        self.bateria -= 1
        # clear_screen()
        print(f"Carro se moveu! Bateria = {self.bateria}%")
        # print(f"Posição atual: ({self.latitude}), ({self.longitude})")

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
        distancia = round(distance(coordenada_a, coordenada_b).km, 2)

        # Diminui a vida da bateria
        self.diminui_bateria(distancia)

    def run(self):
        try:
            while self.bateria > 0:
                # Simula o carro andando aleatoriamente as coordenadas
                lat, lon = random.uniform(-0.0005,
                                          0.0005), random.uniform(-0.0005, 0.0005)
                self.mover(lat, lon)
                
                if self.bateria < 15:
                    thread = threading.Thread(
                        target=self.envia_bateria_baixa)
                    thread.start()
                    self.carro_pode_andar = False
                    while not self.carro_pode_andar:
                        time.sleep(1)

                time.sleep(3)
        except KeyboardInterrupt:
            self.parar()


if __name__ == '__main__':
    carro = Car(1, 16, 200)
    time.sleep(1)
    carro.run()
