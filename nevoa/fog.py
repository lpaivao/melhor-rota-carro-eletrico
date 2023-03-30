import paho.mqtt.client as mqtt
from random import randint

class Fog:
    def __init__(self,topic_prefix,id= randint(0,1000000000),broker_host='localhost',broker_port='1883',nuvem_host='localhost',nuvem_port=6666):
        self.id = id
        self.broker_host = broker_host
        self.broke_port = broker_port
        self.nuvem_host= nuvem_host
        self.nuvem_port = nuvem_port
        self.TOPIC_PREFIX = topic_prefix
        

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self._on_message

    def on_connect(self,client,userdata,flags,rc):
        print(f'Conectado ao Broker! Código de retorno {rc}')
        client.subscribe(self.TOPIC_PREFIX + '/carro/#')
        client.subscribe(self.TOPIC_PREFIX + '/posto/#')

    def _on_message(self,client,data,message):
        topic = message.topic.split('/')
        msg = message.playlod

        if topic[0] == 'carro':
            if topic[1] =="low_batery":
                pass
            elif topic[1]=='posix':
                pass
            else:
                pass
                
        elif topic[0] =='posto':
            pass
        else:
            pass

        


