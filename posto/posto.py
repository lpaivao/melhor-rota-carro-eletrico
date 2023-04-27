import paho.mqtt.client as client
import json
import schedule
import threading
import time
import functions


class Posto:
    def __init__(self, ID_POSTO, lat=-23.5440, lgn=-46.6340, ID_NEVOA=1, BROKER_HOST="172.16.103.3", BROKER_PORT=1884, limite_vagas=5):
        self.ID_POSTO = ID_POSTO
        self.ID_NEVOA = ID_NEVOA
        self.latitude = lat
        self.longitude = lgn
        self.fila = 0
        self.limite_vagas = limite_vagas

        self.BROKER_HOST = BROKER_HOST
        self.BROKER_PORT = BROKER_PORT
        self.client = client.Client(client_id=f"Posto {self.ID_POSTO}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_HOST, BROKER_PORT, 60)

        self.__STATUS = f'fog/{self.ID_NEVOA}/vaga_status/{self.ID_POSTO}'
        self.__INCREASE_LINE = f'fog/{self.ID_NEVOA}/increase_line/{self.ID_POSTO}'
        self.__ALOC = f'fog/{self.ID_NEVOA}/alocando_carro/{self.ID_POSTO}'

        schedule.every(0.5).minutes.do(self.subtrair_fila)
        schedule.every(0.5).minutes.do(self.publish_status)

        mqtt_thread = threading.Thread(target=self.client.loop_forever)
        mqtt_thread.start()

        # self.client.loop_forever()
        while True:
            schedule.run_pending()
            time.sleep(1)

    def on_connect(self, client, usardata, flags, rc):
        print(f"Posto {self.ID_POSTO}")
        print("Conectado")
        self.client.subscribe(self.__INCREASE_LINE)
        self.client.publish(self.__STATUS, json.dumps({
            "id_posto": self.ID_POSTO,
            "fila": self.fila,
            "conectado": True
        }))
        thread = threading.Thread(target=self.desconectar_posto)

    def on_message(self, client, data, message):
        topic = message.topic.split("/")
        msg = message.payload.decode('utf-8')
        msg = json.loads(msg)
        print(message.topic)

        if topic[2] == "increase_line":
            print(f"Entrada na fila do carro: {msg['id_carro']}")
            if self.fila < self.limite_vagas:
                self.fila += 1
                if self.fila == self.limite_vagas:
                    self.client.publish(self.__ALOC, json.dumps({
                        "id_posto": self.ID_POSTO,
                        "vaga": False
                    }))
                else:
                    self.client.publish(self.__ALOC, json.dumps({
                        "id_posto": self.ID_POSTO,
                        "vaga": True
                    }))
                id_carro = str(msg["id_carro"])
                thread = threading.Thread(
                    target=self.recarregar_bateria, args=id_carro)
                thread.start()
            else:
                print(self.fila)
                self.client.publish(self.__ALOC, json.dumps({
                    "id_posto": self.ID_POSTO,
                    "vaga": False
                }))

    def publish_status(self):
        current_time = functions.format_time()
        print(f"[{current_time}]: Estou publicando status")
        self.client.publish(self.__STATUS, json.dumps({
            "id_posto": self.ID_POSTO,
            "fila": self.fila,
            "conectado": True
        }))

    def recarregar_bateria(self, id_carro):
        print(f"Bateria do carro {id_carro} recarregada")
        topic_pub = f"car/battery_recharged/{id_carro}"
        payload = {
            "bateria": 100,
            "latitude": self.latitude,
            "longitude": self.longitude
        }
        print(topic_pub)
        payload = json.dumps(payload)
        self.client.publish(topic_pub, payload)
        self.publish_status()

    def subtrair_fila(self):
        if self.fila > 0:
            self.fila -= 1
            print(f"subtraindo fila:{self.fila}")

    def desconectar_posto(self):
        while True:
            try:
                pass
            except KeyboardInterrupt:
                self.client.publish(self.__STATUS, json.dumps({
                    "id_posto": self.ID_POSTO,
                    "fila": self.fila,
                    "conectado": False
                }))


if __name__ == '__main__':

    posto = Posto(ID_POSTO=3, ID_NEVOA=1, BROKER_HOST="172.16.103.14", BROKER_PORT=1884)
