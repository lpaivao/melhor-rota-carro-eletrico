import paho.mqtt.client as client
import json, schedule, threading,time

class Posto:
    def __init__(self,ID_POSTO=0,lat=0,lgn=0,ID_NEVOA=1,BROKER_HOST="localhost",BROKER_PORT=1883 ):
        self.ID_POSTO = ID_POSTO
        self.ID_NEVOA = ID_NEVOA
        self.latitude = lat
        self.longitude = lgn
        self.fila = 0

        self.BROKER_HOST = BROKER_HOST
        self.BROKER_PORT = BROKER_PORT

        self.client = client.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_HOST, BROKER_PORT, 60)

        self.__STATUS = f'Nevoa/{self.ID_NEVOA}/Vaga_status/{self.ID_POSTO}'
        #self.__BETTER_STATION = f'Nevoa/{self.ID_NEVOA}/Better_station'
        self.__INCRISE_LINE = f'Nevoa/{self.ID_NEVOA}/Incrise_line/{self.ID_POSTO}'
        self.__ALOC = f'Nevoa/{self.ID_NEVOA}/Alocando_carro/{self.ID_POSTO}'

        schedule.every(0.5).minutes.do(self.subtrair_fila)
        schedule.every(0.5).minutes.do(self.publish_status)

        mqtt_thread = threading.Thread(target=self.client.loop_forever)
        mqtt_thread.start()

        #self.client.loop_forever()
        while True:
            schedule.run_pending()
            time.sleep(1)

    def on_connect(self,client,usardata,flags,rc):
       # self.client.subscribe(self.__BETTER_STATION)
        self.client.subscribe(self.__INCRISE_LINE)
        self.client.publish(self.__STATUS,json.dumps({
            "id_posto" : self.ID_POSTO,
            "latitude" : self.latitude,
            "longitude" : self.longitude,
            "fila" : self.fila

        }))

    def on_message(self,client,data,message):
        topic = message.topic.split("/")
        msg = message.payload.decode()

        if topic[2] == "Incrise_line":
            self.fila += 1
            print(self.fila)
            self.client.publish(self.__ALOC,json.dumps({
                "id_posto" : self.ID_POSTO,
                "vaga" : True 
            }))

    def publish_status(self):
        print("Estou publicando status")
        self.client.publish(self.__STATUS,json.dumps({
            "id_posto" : self.ID_POSTO,
            "latitude" : self.latitude,
            "longitude" : self.longitude,
            "fila" : self.fila

        }))


    def subtrair_fila(self):
        if self.fila > 0:
            self.fila -=1
            print(f"subtraindo fila:{self.fila}")


