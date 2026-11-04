import asyncio
import logging
import json

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

class NameServer:

    services = {"time": ("127.0.0.1", 6001), "echo": ("127.0.0.1", 6002)}

    def __init__(self, host="127.0.0.1", port=6000):
        self.host = host
        self.port = port

    async def pubblica(self, writer, messaggio):

        messaggio = json.dumps(messaggio)
        logging.info(f"[PUBBLICAZIONE]: {messaggio}")
        try:
            writer.write(f"{messaggio}\n".encode())
            await writer.drain()
        except ConnectionError:
            logging.error("Invio fallito")

    async def esegui_comando(self, comando, writer, indirizzo):

        if comando["cmd"] == "lookup":
            if comando["service"] in self.services.keys():
                messaggio = {"status": "ok", "service": comando["service"], "host": self.services[comando["service"]][0], "port": self.services[comando["service"]][1]}
            elif comando["service"] == "":
                messaggio = {"status": "error", "message": "MISSING_DATA"}
            else:
                messaggio = {"status": "error", "message": "SERVICE_NOT_FOUND"}

            await self.pubblica(writer, messaggio)
        elif comando["cmd"] != "lookup":
            messaggio = {"status": "error", "message": "UNKNOWN_COMMAND"}
            await self.pubblica(writer, messaggio)

    async def gestisci_client(self, reader, writer):
        indirizzo = writer.get_extra_info("peername")
        logging.info(f"[CONNESSIONE] {indirizzo}")

        try:
            while True:
                dati = await reader.readline()
                if not dati:
                    break
                comando = dati.decode().strip()
                try:
                    comando = json.loads(comando)
                    logging.info(f"[RICEVUTO] {comando} da {indirizzo}")
                    await self.esegui_comando(comando, writer, indirizzo)
                except json.decoder.JSONDecodeError:
                    logging.error("JSON malformato")
                    messaggio = {"status": "error", "message": "INVALID_JSON"}
                    await self.pubblica(writer, messaggio)

        except ConnectionError:
            pass
        finally:
            logging.info(f"[DISCONNESSIONE] {indirizzo}")
            writer.close()
            await writer.wait_closed()

    async def avvia(self):
        server = await asyncio.start_server(self.gestisci_client, self.host, self.port)
        logging.info(f"[NAME_SERVER] In ascolto su {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

class TimeServer:

    def __init__(self, host="127.0.0.1", port=6001):
        self.host = host
        self.port = port

    async def pubblica(self, writer, messaggio):

        logging.info(f"[PUBBLICAZIONE]: {messaggio}")
        try:
            writer.write(f"{messaggio}\n".encode())
            await writer.drain()
        except ConnectionError:
            logging.error("Invio fallito")

    async def gestisci_client(self, reader, writer):
        indirizzo = writer.get_extra_info("peername")
        logging.info(f"[CONNESSIONE] {indirizzo}")

        try:
            while True:
                dati = await reader.readline()
                if not dati:
                    break
                comando = dati.decode().strip()
                logging.info(f"[RICEVUTO] {comando} da {indirizzo}")
                await self.esegui_comando(comando, writer, indirizzo)
        except ConnectionError:
            pass
        finally:
            logging.info(f"[DISCONNESSIONE] {indirizzo}")
            writer.close()
            await writer.wait_closed()

    async def avvia(self):
        server = await asyncio.start_server(self.gestisci_client, self.host, self.port)
        logging.info(f"[TIME_SERVER] In ascolto su {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

class EchoServer:

    def __init__(self, host="127.0.0.1", port=6002):
        self.host = host
        self.port = port

    async def pubblica(self, writer, messaggio):

        logging.info(f"[PUBBLICAZIONE]: {messaggio}")
        try:
            writer.write(f"{messaggio}\n".encode())
            await writer.drain()
        except ConnectionError:
            logging.error("Invio fallito")

    async def gestisci_client(self, reader, writer):
        indirizzo = writer.get_extra_info("peername")
        logging.info(f"[CONNESSIONE] {indirizzo}")

        try:
            while True:
                dati = await reader.readline()
                if not dati:
                    break
                comando = dati.decode().strip()
                logging.info(f"[RICEVUTO] {comando} da {indirizzo}")
                await self.esegui_comando(comando, writer, indirizzo)
        except ConnectionError:
            pass
        finally:
            logging.info(f"[DISCONNESSIONE] {indirizzo}")
            writer.close()
            await writer.wait_closed()

    async def avvia(self):
        server = await asyncio.start_server(self.gestisci_client, self.host, self.port)
        logging.info(f"[ECHO_SERVER] In ascolto su {self.host}:{self.port}")
        async with server:
            await server.serve_forever()


async def main():
    ns = NameServer()
    #ts = TimeServer()
    #es = EchoServer()

    await ns.avvia()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass