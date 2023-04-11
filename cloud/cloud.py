from flask import Flask, request, jsonify
from flask_mqtt import Mqtt
import paho.mqtt.client as mqtt
import random
import json
import topics
import threading

app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!",
                    "error": False
                    })


class Cloud:
    def __init__(self, host, port, timeout):
        self.fog_prefix = "fog"
        self._host = host
        self._port = port
        self._fognodes = {}
        # Colocar uma queue de verdade (se tiver de usar uma queue!). Pode até ser priority(o comando a ser executado mais rapudo é o que tem o carro com menor bateria)
        self._command_queue = {}
        self._id = random.randint(1, 10)
        self._broker_connection = mqtt.Client(str(self._id), False)
        self._broker_connection.on_message = self._on_node_message

        connection_thread = threading.Thread(
            target=self._connect_to_brocker, args=[self._broker_connection, self._host, self._port, timeout])
        connection_thread.start()

    # fog/fog_id/fog_change
    # fog/fog_id/response_fog_change
    def _connect_to_brocker(self, client, host, port, timeout):
        client.connect(host, port, timeout)
        print('Connected successfully')
        client.subscribe(
            f"{self.fog_prefix}/{topics.FOG_CHANGE}")
        client.subscribe(
            f"{self.fog_prefix}/{topics.CLOUD_RESPONSE_FOG}")
        client.loop_forever()

    def _on_node_message(self, station, message):
        topic = message.topic.split('/')
        msg = message.payload.decode()
        msg = json.loads(msg)

        """
        Uma garantia de segurança
        """
        if topic[0] == str(self.fog_prefix):
            node_id = topic[1]
            if topic[2] == topics.FOG_CHANGE:
                id_carro = msg["id_carro"]
                latitude = msg["latitude"]
                longitude = msg["longitude"]
                max_distance_per_charge = msg["max_distance_per_charge"]


if __name__ == '__main__':
    try:
        my_cloud = Cloud("localhost", 1883, 60)
        # api = threading.Thread(target=app.run)
        # api.start()
    except KeyboardInterrupt:
        print("Ending Application...")
    finally:
        # api.join()
        pass
