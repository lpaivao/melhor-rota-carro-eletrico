import json
import time
from flask import Flask
from flask_restful import Resource, Api
import socket
import threading
from geopy import Point
import paho.mqtt.client as mqtt
import functions

#app = Flask(__name__)
#api = Api(app)


#class Hello(Resource):
#    def get(self):
#        return {'hello': 'world'}


#api.add_resource(Hello, '/')


nevoas_var = {
    "0": {"fog_id": 0, "ponto_central": Point(-23.5450, -46.6350), "conectado": False},
    "1": {"fog_id": 1, "ponto_central": Point(-23.5600, -46.6600), "conectado": False},
    "2": {"fog_id": 2, "ponto_central": Point(-23.5480, -46.6380), "conectado": False}
}


class Cloud:
    def __init__(self, id, host="localhost", port=8000, broker_host="172.16.103.3", broker_port=1884, nevoas=nevoas_var):
        self.id = id
        self.nevoas = nevoas

        # Conexão MQTT
        self.client = mqtt.Client(client_id=f"Cloud {self.id}")
        self.client.on_connect = self.on_connect

        try:
            self.client.connect(broker_host, broker_port, 60)
        except ConnectionRefusedError as e:
            print(e)
            print("Não foi possível conectar ao Broker MQTT")

        # Conexão sock
        self.host = host
        self.port = port

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind((self.host, self.port))
            self.s.listen()
            print(f"Socket escutando em {self.host}:{self.port}")
        except Exception as e:
            print(e)
            print(f"Não foi possível conectar ao socket em {self.host}:{self.port}")

        self.sentinelthread = threading.Thread(
            target=self._handle_conn, args=[self.s])
        self.sentinelthread.start()

        self._fognodes = []
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print(f'Conectado ao Broker! Código de retorno {rc}')
        topic_sub = f"cloud/fog_connect"
        self.client.subscribe(topic_sub)

    def _handle_conn(self, socket):
        while True:
            conn, addr = socket.accept()
            self._fognodes.append(conn)
            thread = threading.Thread(
                target=self._handle_fognode, args=[conn, addr])
            thread.start()

    def _handle_fognode(self, connection, address):
        with connection:
            # Aqui ocorre o processo de trocar o carro de nó
            print("A new connection was made!")
            print(connection)
            while True:
                try:
                    data = connection.recv(1024)
                    if not data:
                        break

                    # Decodifica a mensagem
                    message = data.decode("utf-8")
                    print(message)
                    message = json.loads(message)
                    fog_id = message["fog_id"]

                    if "conectado" in message:
                        self.nevoas[fog_id]["conectado"] = message["conectado"]
                    else:
                        # Desmembra as informações
                        id_carro = message["id_carro"]
                        latitude = message["latitude"]
                        longitude = message["longitude"]
                        max_distance_per_charge = message["max_distance_per_charge"]

                        # Verifica a névoa nova
                        nova_nevoa_id = functions.calcula_nevoa_proxima(fog_id, latitude, longitude,
                                                                        max_distance_per_charge, self.nevoas)

                        # Constrói a resposta
                        response = {
                            "fog_id": nova_nevoa_id
                        }
                        response = json.dumps(response)

                        # Tópico para enviar a mensagem
                        topic_pub = f"cloud/fog_change/{id_carro}"
                        # Envia mensagem
                        print(
                            f"Mudando carro {id_carro} da nevoa {fog_id} para a nevoa {nova_nevoa_id}")
                        self.client.publish(topic_pub, response)

                except socket.error:
                    print("Client disconnected")
                    break

            self._fognodes.remove(connection)
            connection.close()
        threading.current_thread().join()


if __name__ == '__main__':
    my_cloud = Cloud(id=1, host="localhost", port=8000, broker_host="172.16.103.14", broker_port=1883)
    #app.run(port=5001)
