import paho.mqtt.client as mqtt

def callback():
    print("yes")

if __name__ == '__main__':
    client = mqtt.Client()
    client.connect('127.0.0.1', port=1883, keepalive=60, bind_address="")
    client.publish('/flask/mqtt', payload="Teste", qos=0, retain=False)