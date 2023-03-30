from dotenv import load_dotenv
import os

load_dotenv()
BROKER_ADRESS = os.environ['BROKER_ADRESS']
PORT = os.environ['PORT']
keep_alive_interval = os.environ['keep_alive_interval']
BASE_TOPIC = os.environ['BASE_TOPIC']

