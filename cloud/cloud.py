from flask import Flask, request, jsonify
from flask_mqtt import Mqtt

fogs = {}
command_queue = {}

"""
Topics:
*The default scheme is:
    fog{id}/car/#
    fog{id}/station/#

examples:
-fog1/car/low-battery (The publisher is a car)
-fog1/car/posix (The publisher is a car)
-fog1/station/queue (The publisher is a station)
-fog1/station/better-local (Cars are the subscribers)
-fog1/carro/fog-state (Cars are the subscribers)
"""


app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = '' 
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

topic = '/flask/mqtt'

mqtt_client = Mqtt(app)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(topic) 
    else:
        print('Bad connection. Code:', rc)
        
@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    """
    topic = message.topic.split('/')
    payload = message.payload.decode('utf-8')
    """
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))

@app.route('/publish', methods=['POST'])
def publish_message():
    request_data = request.get_json()
    publish_result = mqtt_client.publish(request_data['topic'], request_data['msg'])
    return jsonify({'code': publish_result[0]})

@app.route("/")
def hello():
    return jsonify({"message": "Hello, World!",
                    "error": False
                    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=65136)
    