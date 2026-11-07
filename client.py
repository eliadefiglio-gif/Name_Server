import asyncio
import logging
import json
import argparse
from enum import nonmember

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

class Client:
    def __init__(self, ns_host, ns_port):
        self.ns_host = ns_host
        self.ns_port = ns_port
        self.reader = None
        self.writer = None


    async def connetti(self, host, port):
        logging.info(f"Connessione a {host}:{port}")
        self.reader, self.writer = await asyncio.open_connection(host, port)

    async def disconnetti(self):
        if self.writer and not self.writer.is_closing():
            logging.info("Disconnessione dal server corrente")
            self.writer.close()
            await self.writer.wait_closed()
        self.reader = None
        self.writer = None

    async def servizio(self):
        logging.info("Interfaccia comandi avviata. Digita 'QUIT' per uscire.")

        while True:
            testo = await asyncio.to_thread(input)
            if testo == "QUIT" or self.writer.is_closing():
                break

            comando = {"cmd": testo}
            self.writer.write(f"{json.dumps(comando)}\n".encode())
            await self.writer.drain()

            messaggio = await self.reader.readline()

            if not messaggio:
                logging.warning("Il server ha chiuso la connessione.")
                break

            messaggio = json.loads(messaggio.decode().strip())
            if messaggio["status"] == "ok":
                logging.info(messaggio["time"])
            elif messaggio["status"] == "error":
                logging.error(f"Errore nella comunicazione. Error_code: {messaggio['message']}")

    async def ottieni_servizio(self, service):
        await self.connetti(self.ns_host, self.ns_port)

        comando = {"cmd": "lookup", "service": service}
        self.writer.write(f"{json.dumps(comando)}\n".encode())
        await self.writer.drain()

        dati = await self.reader.readline()
        await self.disconnetti()

        if not dati:
            logging.error("Errore nella comunicazione col name server")

        dati = dati.decode().strip()
        messaggio = json.loads(dati)
        if messaggio["status"] == "ok":
            logging.info(f"Ricezione avvenuta con successo. Host: {messaggio['host']} Port: {messaggio['port']}")
        elif messaggio["status"] == "error":
            logging.error(f"Errore nella comunicazione. Error_code: {messaggio['message']}")

        return messaggio

    async def avvia(self, service):
        try:
            servizio = await self.ottieni_servizio(service)
            host_servizio = servizio["host"]
            port_servizio = servizio["port"]

            await self.connetti(host_servizio, port_servizio)
            logging.info(f"Connessione avviata col servizio {service}")

            await self.servizio()

        except Exception as e:
            logging.error("Errore nel recuperare il servizio")
        finally:
            await self.disconnetti()
            logging.info("Server disconnesso.")

async def main():
    host = "127.0.0.1"

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", required=True, type=int, help="Port to connect to")
    parser.add_argument("-s", "--service", required=True, help="Service needed")
    args = parser.parse_args()

    client = Client(host, args.port)
    await client.avvia(service=args.service)


asyncio.run(main())