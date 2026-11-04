import asyncio
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

class NameServer:

    def __init__(self, host="127.0.0.1", port=6000):
        self.host = host
        self.port = port

    async def avvia(self):
        server = await asyncio.start_server(self.gestisci_client, self.host, self.port)
        logging.info(f"[NAME_SERVER] In ascolto su {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

class TimeServer:

    def __init__(self, host="127.0.0.1", port=6001):
        self.host = host
        self.port = port

    async def avvia(self):
        server = await asyncio.start_server(self.gestisci_client, self.host, self.port)
        logging.info(f"[TIME_SERVER] In ascolto su {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

class EchoServer:

    def __init__(self, host="127.0.0.1", port=6002):
        self.host = host
        self.port = port

    async def avvia(self):
        server = await asyncio.start_server(self.gestisci_client, self.host, self.port)
        logging.info(f"[ECHO_SERVER] In ascolto su {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    NameServer = NameServer()
    try:
        asyncio.run()
    except KeyboardInterrupt:
        pass