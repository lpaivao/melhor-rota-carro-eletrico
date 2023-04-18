import asyncio
import time


class ServerProtocol(asyncio.Protocol):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.buffer = b''

    def connected_by_fognode(self, transport):
        self.transport = transport
        print(f'Connection made to {self.host}:{self.port}')

    def data_received_from_fognode(self, data):
        print(f'Received data: {data.decode()}')
        self.buffer += data

    def connection_lost(self, exc):
        print(f'Connection lost to {self.host}:{self.port}')


async def handle_client(reader, writer):
    request = None
    while request != 'quit':
        request = (await reader.read(255)).decode('utf8')
        response = str(eval(request)) + '\n'
        writer.write(response.encode('utf8'))
        await writer.drain()
    writer.close()


async def start_cloudnode_server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()


# Aqui é pra testar o servidor
async def send_data():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    writer.write(b'Hello, server!')
    await writer.drain()
    data = await reader.read(100)
    print(f'Received data: {data.decode()}')
    writer.close()
    await writer.wait_closed()


async def main():
    server_task = asyncio.create_task(start_cloudnode_server())
    await asyncio.sleep(1)
    send_task = asyncio.create_task(send_data())
    await asyncio.gather(server_task, send_task)

asyncio.run(main())
