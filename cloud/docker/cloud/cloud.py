from flask import Flask, request, jsonify
import socket
import threading

app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!",
                    "error": False
                    })


class Cloud:
    def __init__(self, host, port):
        self._host = host
        self._port = port

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.s.listen()

        self.sentinelthread = threading.Thread(
            target=self._handle_conn, args=[self.s])
        self.sentinelthread.start()

        self._fognodes = []

        # Colocar uma queue de verdade (se tiver de usar uma queue!). Pode até ser priority(o comando a ser executado mais rápido é o que tem o carro com menor bateria)
        self._command_queue = {}

    def _handle_conn(self, socket):
        while True:
            conn, addr = socket.accept()
            self._fognodes.append(conn)
            print(len(self._fognodes))
            thread = threading.Thread(
                target=self._handle_fognode, args=[conn, addr])
            thread.start()

    def _handle_fognode(self, connection, address):

        with connection:
            print(threading.current_thread().name)

            # Fazer aqui o processo de trocar o carro de nó
            while True:
                try:
                    data = connection.recv(1024)
                    if not data:
                        break

                    message = data.decode('utf-8').split('\r\n')[0]

                    if message == "!DISCONNECT":
                        connection.close()
                        self._fognodes.pop()
                        break

                    connection.sendall(data)
                except socket.error:
                    print("Client disconnected")
                    break
            self._fognodes.remove(connection)
            connection.close()
            threading.current_thread().join()

    def _on_node_message(self):
        pass

    def __del__(self):
        self.sentinelthread.join()


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 65136
    my_cloud = Cloud(HOST, PORT)
    print(f"The cloud is listening on: ({HOST}:{PORT})")
