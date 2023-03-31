import paho.mqtt.client as mqtt
import json
import random
import time
from geopy.distance import geodesic
from geopy.distance import distance

# fila = quantos carros tem na fila
# espera = tempo de espera
postos_disponiveis = {
    'Posto A': {'latitude': -23.5440, 'longitude': -46.6340, 'fila': 5, 'espera': 5},
    'Posto B': {'latitude': -23.5450, 'longitude': -46.6350, 'fila': 2, 'espera': 3},
    'Posto C': {'latitude': -23.5560, 'longitude': -46.6360, 'fila': 3, 'espera': 1}
}


class CarroEletrico:
    def __init__(self, id_carro, bateria, max_distance_per_charge, postos=postos_disponiveis, latitude=-23.5450, longitude=-46.6355):
        self.id_carro = id_carro
        self.latitude = latitude
        self.longitude = longitude
        self.bateria = bateria
        self.postos = postos
        # Distância máxima que o carro pode percorrer com carga máxima
        self.max_distance_per_charge = max_distance_per_charge

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

        if message.topic == "fog/postos_disponiveis":
            # posto_mais_proximo_mais_rapido = self.calcular_posto_mais_proximo_mais_rapido(self.postos)
            # posto_mais_proximo_menor_fila = self.calcular_posto_mais_proximo_menor_fila(self.postos)
            '''
            Implementar alguma lógica aqui
            '''

    def calcular_posto_mais_proximo_mais_rapido(self):
        """
        Encontra o posto de carregamento mais próximo e com o menor tempo de espera.
        """
        nome_proximo = None
        posto_proximo = None
        distancia_proxima = float("inf")

        if self.postos:
            for posto in self.postos:
                # Calcula a distância em km utilizando as latitudes e longitudes
                distancia = geodesic((self.latitude, self.longitude),
                                     (self.postos[posto]["latitude"], self.postos[posto]["longitude"])).km

                if posto_proximo is None:
                    nome_proximo = posto
                    posto_proximo = self.postos[posto]
                    distancia_proxima = distancia

                # Se a distância for menor que a distância que o carro percorre com a bateria toda carregada
                # e o tempo de espera for o menor, atualiza o posto mais próximo
                if distancia <= self.max_distance_per_charge and self.postos[posto]["espera"] < posto_proximo['espera']:
                    nome_proximo = posto
                    posto_proximo = self.postos[posto]
                    distancia_proxima = distancia

        return nome_proximo, posto_proximo, distancia_proxima

    def calcular_posto_mais_proximo_menor_fila(self):
        """
        Encontra o posto de carregamento mais próximo e com o menor tempo de espera.
        """
        nome_proximo = None
        posto_proximo = None
        distancia_proxima = float("inf")

        if self.postos:
            for posto in self.postos:
                # Calcula a distância em km utilizando as latitudes e longitudes
                distancia = geodesic((self.latitude, self.longitude),
                                     (self.postos[posto]["latitude"], self.postos[posto]["longitude"])).km

                if posto_proximo is None:
                    nome_proximo = posto
                    posto_proximo = self.postos[posto]
                    distancia_proxima = distancia

                # Se a distância for menor que a distância que o carro percorre com a bateria toda carregada
                # e a quantidade de carros na fila for a menor, atualiza o posto mais próximo
                if distancia <= self.max_distance_per_charge and self.postos[posto]["fila"] < posto_proximo['fila']:
                    nome_proximo = posto
                    posto_proximo = self.postos[posto]
                    distancia_proxima = distancia

        return nome_proximo, posto_proximo, distancia_proxima

    def receber_postos_nevoa(self):
        self.client.subscribe("fog/postos_disponiveis")
        self.enviar_bateria_baixa()
        '''
        Implementar alguma lógica aqui
        '''
    def enviar_bateria_baixa(self):
        payload = {
            "id_carro": self.id_carro,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "bateria": self.bateria
        }
        self.client.publish("carro/low_battery", json.dumps(payload))
        print(f"Aviso de bateria baixa enviado para a névoa local. Carro ID: {self.id_carro}")

    # Diminui a bateria quando o carro anda
    def diminui_bateria(self, distance):
        self.bateria -= round(distance / self.max_distance_per_charge * 100, 2)

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
                # self.mover(lat, lon)
                time.sleep(2)

                # print("Posicao -> lat = {} / long = {}".format(self.latitude, self.longitude))
                # diminui o nível da bateria de acordo com a distância percorrida
                # distancia = round(random.uniform(0.5, 1.5), 2)
                self.diminui_bateria(distancia)

                print("Distancia percorrida: {}km".format(distancia))
                print("Bateria = {}".format(round(self.bateria), 2))

                nome_mais_prox, posto_mais_prox, distancia_mais_prox = self.calcular_posto_mais_proximo_mais_rapido()
                print("Nome do posto mais proximo mais rapido = {}".format(nome_mais_prox))
                print("Posto mais proximo mais rapido = {}".format(posto_mais_prox))
                print("Distancia do posto mais proximo mais rapido = {}km".format(round(distancia_mais_prox, 2)))

                nome_mais_prox, posto_mais_prox, distancia_mais_prox = self.calcular_posto_mais_proximo_menor_fila()
                print("Nome do posto mais proximo com menos fila = {}".format(nome_mais_prox))
                print("Posto mais proximo com menos fila = {}".format(posto_mais_prox))
                print("Distancia do posto mais proximo com menos fila = {}km".format(round(distancia_mais_prox, 2)))

                # verifica se a bateria está baixa e envia mensagem para a névoa local
                if self.bateria < 15:
                    self.receber_postos_nevoa()
        except KeyboardInterrupt:
            self.parar()


if __name__ == '__main__':
    carro = CarroEletrico(1, 16, 200)
    carro.run()
