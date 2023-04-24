import json
import argparse
from flask import Flask, jsonify
import socket
import threading
from geopy import Point
import paho.mqtt.client as mqtt
import functions

app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!",
                    "error": False
                    })


nevoas_var = {
    "0": {"fog_id": 0, "ponto_central": Point(-23.5450, -46.6350), "conectado": False},
    "1": {"fog_id": 1, "ponto_central": Point(-23.5600, -46.6600), "conectado": False},
    "2": {"fog_id": 2, "ponto_central": Point(-23.5480, -46.6380), "conectado": False}
}


class Cloud:
    def __init__(self, id, host, port, nevoas=nevoas_var):
        self.id = id
        self.nevoas = nevoas

        # Conexão MQTT
        self.client = mqtt.Client(client_id=f"Cloud {self.id}")
        self.client.on_connect = self.on_connect

        try:
            self.client.connect('127.0.0.1', 1883, 60)
        except ConnectionRefusedError as e:
            print(e)
            print("Não foi possível conectar ao Broker MQTT")

        # Conexão sock
        self.host = host
        self.port = port

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))
        self.s.listen()

        self.sentinelthread = threading.Thread(
            target=self._handle_conn, args=[self.s])
        self.sentinelthread.start()

        self._fognodes = []

        # Colocar uma queue de verdade (se tiver de usar uma queue!). Pode até ser priority(o comando a ser executado mais rápido é o que tem o carro com menor bateria)
        self._command_queue = {}

        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print(f'Conectado ao Broker! Código de retorno {rc}')
        topic_sub = f"cloud/fog_connect"
        self.client.subscribe(topic_sub)

    def _handle_conn(self, socket):
        while True:
            conn, addr = socket.accept()
            self._fognodes.append(conn)
            print(len(self._fognodes))
            thread = threading.Thread(
                target=self._handle_fognode, args=[conn, addr])
            thread.start()

    def _handle_fognode(self, connection, address):
        with connection:
            print(threading.current_thread().name)

            # Fazer aqui o processo de trocar o carro de nó
            while True:
                try:
                    data = connection.recv(1024)
                    if not data:
                        break

                    # Decodifica a mensagem
                    message = data.decode("utf-8")
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

    def _on_node_message(self):
        pass


if __name__ == '__main__':
    """
    client = docker.from_env()
    container = client.containers.get('my-container')
    network = client.networks.get('my-network')
    container_ip = network.attrs['Containers'][container.id]['IPv4Address']
    """

    """
    print(f"The IP address of container {container.name} on network {network.name} is {container_ip}")
    parser = argparse.ArgumentParser(
        description='TEC502:PBL2:2023.1 - Sets up the network config of the cloud')
    parser.add_argument('--ip', help='IP address', required=True)
    parser.add_argument('--port', metavar='PORT', type=int, default=8000,
                        help='TCP port (default 8000)', required=True)
    parser.add_argument(
        '--mosquitto_ip', help='Mosquitto IP address', required=True)
    parser.add_argument('--mosquitto_port', metavar='MOSQUITTO_PORT', type=int, default=1883,
                        help='Mosquitto port (default 1883)', required=True)
    args = parser.parse_args()

    HOST = args.ip
    PORT = args.port    
    
    """
    HOST = '127.0.0.1'
    PORT = 8000
    print(f"The cloud is listening on: ({HOST}:{PORT})")
    my_cloud = Cloud(1, HOST, PORT)
