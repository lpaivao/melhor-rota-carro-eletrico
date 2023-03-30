import paho.mqtt.client as mqtt

class Cloud:
    def __init__(self,topic_prefix='cloud',broker_host='localhost',broker_port=1883):
        self.broker_host = broker_host
        self.port = broker_port

        self.cliente = mqtt.Client()

    
    def on_connect(self,cliente,userdata,flags,rc):
        if rc==0:
            print('Conexão Estabelecida com sucesso!')
        else:
            print('Falha na conexão')

    def on_menssage(self,cliente,userdata,mensage):
        print('Mensagem recebida!')
        topic = mensage.topic.split('/')
        payload = mensage.payload
        

        
        