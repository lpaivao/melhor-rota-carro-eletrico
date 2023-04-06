import paho.mqtt.client as mqtt
import json
import random
import time
from geopy.distance import geodesic
from geopy.distance import distance
import topics
import threading

posto = {'latitude': -23.5440, 'longitude': -46.6340, 'fila': 5, 'espera': 5}


class Car:
    def __init__(self, fog_prefix, id_carro, bateria, max_distance_per_charge, melhor_posto=posto, latitude=-23.5450,
                 longitude=-46.6355):
        # Prefixo de qual nuvem o carro está no momento
        self.fog_prefix = fog_prefix
        # Dicionário com as informações do melhor posto desde a última solicitação
        self.melhor_posto = melhor_posto
        # Variável booleana para indicar se tem um processo de envio de bateria baixa acontecendo
        self.boolean_enviando_bateria = False
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
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Conectado ao broker MQTT")

    def on_message(self, client, userdata, message):
        json_payload = message.payload.decode('utf-8')
        payload = json.loads(json_payload)

        if message.topic == f"{self.fog_prefix}/{topics.BETTER_STATION}/{self.id_carro}":
            self.boolean_enviando_bateria = False
            self.melhor_posto = payload
            print(f"Melhor posto -> {self.melhor_posto}")
            """
            Logo após o carro receber a resposta do melhor posto,
            ele vai se desinscrever do tópico no formato:
            {nome da névoa}/better_station/{id do carro},
            pois caso seja necessário ele mudar de névoa, ele não estará inscrito
            no tópico de uma névoa antiga
            """
            self.client.unsubscribe(f"{self.fog_prefix}/{topics.BETTER_STATION}/{self.id_carro}")

    def enviar_bateria_baixa(self):
        payload = {
            "id_carro": self.id_carro,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "max_distance_per_charge": self.max_distance_per_charge
        }
        """
            Vai fazer a publicação no tópico com o seguinte formato:
            fog1/low_battery
        """
        topico_pub = f"{self.fog_prefix}/{topics.LOW_BATTERY}"
        response = json.dumps(payload)
        """
            Quando o carro for se inscrever para receber a resposta
            de melhor posto da névoa, o tópico vai possuir o identificador
            da névoa e o id do carro:
            {nome da névoa}/better_station/{id do carro}
            exemplo: fog1/better_station/1 
        """
        topic_sub = f"{self.fog_prefix}/{topics.BETTER_STATION}/{self.id_carro}"
        self.client.subscribe(topic_sub)
        self.boolean_enviando_bateria = True
        while self.boolean_enviando_bateria:
            print(f"Esperando resposta de melhor posto em {topic_sub}...")
            self.client.publish(topico_pub, response)
            time.sleep(4)

    # Diminui a bateria quando o carro anda
    def diminui_bateria(self, distancia):
        self.bateria -= round(distancia / self.max_distance_per_charge * 100, 2)
        # print(f"Bateria = {self.bateria}")

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

                time.sleep(2)
        except KeyboardInterrupt:
            self.parar()


if __name__ == '__main__':
    carro = Car("fog1", 1, 15, 200)
    time.sleep(1)
    carro.run()
