import Entities
import Topicos

# Chave = ID do posto
# Valor = Objeto Posto de Entities.py
postos_dict = {}
# Chave = ID do posto
# Valor = Conexão MQTT do posto
postos_mqtt = {}


def criar_posto(id):
    if id not in postos_dict.keys():
        postos_dict[id] = Entities.Posto
        postos_mqtt[id] = Entities.MQTTConn
        mqtt_conn = postos_mqtt[id]
        subscribe_posto(mqtt_conn)
    else:
        print("Posto já registrado\n")


# Faz o posto escutar o tópico de baterias baixas
def subscribe_posto(mqtt_conn):
    mqtt_conn.connect()
    mqtt_conn.subscribe(Topicos.BATERIA_BAIXA, qos=1)
    mqtt_conn.set_callback(on_message_callback())


def on_message_callback(client, userdata, message):
    print(f"Nova mensagem recebida no tópico {message.topic}: {message.payload}")
