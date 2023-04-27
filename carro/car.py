import paho.mqtt.client as mqtt
import json
import random
import time
from geopy.distance import geodesic
from geopy.distance import distance
import topics
import threading
import os
import socket
from http.server import BaseHTTPRequestHandler,HTTPServer
from http_server import RequestHandler

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


os.environ['TERM'] = 'xterm'

posto = {'id_posto': 0, 'latitude': -23.5440,
         'longitude': -46.6340, 'fila': 0, 'vaga': True}


# Função que será executada se o tempo limite for atingido
def on_timeout(self):
    print("Tempo limite de resposta excedido.")


class Car():
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self,car_instance,*args,**kwargs):
            self.car = car_instance
            super().__init__(*args,**kwargs)
        def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Amg,estou funcionando')
                elif self.path == '/bateria':
                    self.send_response(200)
                    content = f'<html><body><h1>Bateria Level: {self.car.bateria}!</h1></body></html>'
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                
                elif self.path == '/betterStation':
                    self.send_response(200)
                    content = f'<html><body><h1>Melhor Posto: {self.car.melhor_posto}!</h1></body></html>'
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                else:
                    self.send_error(404)
                    
    def __init__(self, id_carro, bateria, max_distance_per_charge, host="localhost",broker_host="172.16.103.3",broker_port=1884, melhor_posto=posto, latitude=-23.5450,
                 longitude=-46.6355, fog_prefix="fog", fog_id=1):
        # Prefixo de qual nuvem o carro está no momento
        self.fog_prefix = fog_prefix
        # ID na nevoa
        self.fog_id = fog_id
        # Dicionário com as informações do melhor posto desde a última solicitação
        self.melhor_posto = melhor_posto

        #tcp
        '''
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__run_server = True
        self.server_socket.bind(("localhost",8035))
        self.server_socket.listen()'''

        #self.http_server = HTTPServer(('localhost',8080),self.RequestHandler)
        #self.http_server = HTTPServer((host, 8080), lambda *args, **kwargs: self.RequestHandler(self, *args, **kwargs))

        self.tcp_look = threading.Lock()
        self.mqtt_look = threading.Lock()

        self.carro_pode_andar = False
        self.posto_respondeu = False
        self.timer1 = None
        self.timer2 = None
        self.timer3 = None
        # Distância máxima que o carro pode percorrer com carga máxima
        self.max_distance_per_charge = max_distance_per_charge

        self.id_carro = id_carro
        self.latitude = latitude
        self.longitude = longitude
        self.bateria = bateria

        # Configura cliente mqtt
        self.client = mqtt.Client(client_id=f"Carro {self.id_carro}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker_host, broker_port, 60)
        
        
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

    def on_message(self, client, userdata, message):
        json_payload = message.payload.decode('utf-8')
        payload = json.loads(json_payload)

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

    def ocupar_vaga_posto(self, melhor_posto):
        self.tentando_ocupar_posto = True
        # Faz o carro ocupar vaga do posto
        id_posto = str(melhor_posto["id_posto"])
        topico_ocupar_vaga = f"{self.fog_prefix}/{self.fog_id}/increase_line/{id_posto}"
        payload = {
            "id_carro": self.id_carro
        }
        payload = json.dumps(payload)
        self.client.publish(topico_ocupar_vaga, payload)
        print(f"Mensagem de ocupar vaga publicada em {topico_ocupar_vaga}")

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
    
    '''
    def start_tcp(self):
        with self.tcp_look:
            while self.__run_server:
                conex, addr = self.server_socket.accept()
                print(f'Conectado de {addr}')
                thread = threading.Thread(target= self.handle_connection, args=(conex, addr))
                thread.start()
        
    def handle_connection(self,conex,addr):
        print(conex)
        request = conex.recv(1024).decode()
        print(repr(request))
        response = 'HTTP/1.1 404 Not Found\r\nContent-Length: 9\r\n\r\nNot found'
        if request:
            method, path, *restante = request.split(' ')
        
            if path == '/' and method=='GET':
                response = f'HTTP/1.1 200 OK\r\nContent-Length: 9\r\n\r\nOla Mundo'

            elif method== 'GET' and path == '/bateria':
                print('Entrei')
                response = f'HTTP/1.1 200 ok\r\nContent-Length: 20\r\n\r\n{self.bateria}'
                conex.sendall(response.encode())
                conex.close()
                '''

    def run(self):
       # with self.mqtt_look:
        while self.bateria > 0:
            # Simula o carro andando aleatoriamente as coordenadas
            lat, lon = random.uniform(-0.0005,
                                    0.0005), random.uniform(-0.0005, 0.0005)
            self.mover(lat, lon)
            """
                Verifica se a bateria está baixa e se já não 
                tem um processamento de envio de bateria baixa
            """
            if self.bateria < 15:
                #self.envia_bateria_baixa()
                thread = threading.Thread(
                    target=self.envia_bateria_baixa)
                thread.start()
                self.carro_pode_andar = False
                while not self.carro_pode_andar:
                    time.sleep(1)

            time.sleep(3)
    def start(self):
        self.http_server.serve_forever()

    def stop(self):
         self.http_server.shutdown()
        
    def drive(self):
        thread_tcp = threading.Thread(target=self.start)
        thread_tcp.start()

        thread_mqtt = threading.Thread(target=self.run)
        thread_mqtt.start()

        #thread_mqtt.join()
        #thread_tcp.join()
            
            

if __name__ == '__main__':
    
    carro = Car(id_carro=1, fog_id=0, bateria=20, max_distance_per_charge=200, broker_host="172.16.103.14", broker_port=1883)
    carro.drive()
    