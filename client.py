import asyncio
import logging
import json
import argparse

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )


async def ricevi(reader, writer):
    dati = await reader.readline()
    if not dati:
        if not writer.is_closing():
            logging.info("Server disconnesso.")
            writer.close()

    dati = dati.decode().strip()
    messaggio = json.loads(dati)
    logging.info(dati)
    if messaggio["status"] == "ok":
        logging.info(f"Ricezione avvenuta con successo. Host: {messaggio['host']} Port: {messaggio['port']}")
        writer.close()
        if messaggio["service"] == "time":
            logging.info("Connessione al time server")
        elif messaggio["service"] == "echo":
            logging.info("Connessione all' echo server")
    elif messaggio["status"] == "error":
        logging.error(f"Errore nella comunicazione. Error_code: {messaggio['message']}")



async def invia(writer):
    testo = '{"cmd": "lookup", "service": "time"}'
    writer.write((testo + "\n").encode())
    await writer.drain()


async def main():
    host = "127.0.0.1"

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port to connect to")
    args = parser.parse_args()

    try:
        if args.port:
            reader, writer = await asyncio.open_connection(host, int(args.port))
            logging.info("Connesso al name server.")
        else:
            logging.error("Porta non specificata")

        await asyncio.gather(ricevi(reader, writer), invia(writer))
    except ValueError:
        logging.error("La porta deve essere un numero")


asyncio.run(main())