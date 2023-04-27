import socket
import datetime

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(("172.16.103.14", 8000))
    current_time = datetime.datetime.now()
    print(
        f"[{current_time}] - Connected to cloud no endereço ({'172.16.103.14'}:{8000})")
except Exception as e:
    print(e)