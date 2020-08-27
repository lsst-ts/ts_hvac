import asyncio
import signal
import time

from gmqtt import Client as MQTTClient

STOP = asyncio.Event()


def on_connect(client, flags, rc, properties):
    print("Connected")
    client.subscribe("LSST/PISO02/#", qos=0)


async def on_message(client, topic, payload, qos, properties):
    print(f"RECV MSG:{topic}:{payload}")
    return 0


def on_disconnect(client, packet, exc=None):
    print("Disconnected")


def on_subscribe(client, mid, qos):
    print("SUBSCRIBED")


def ask_exit(*args):
    STOP.set()


async def main(broker_host):
    client = MQTTClient("client-id")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    await client.connect(broker_host, version=5)

    client.publish("TEST/TIME", str(time.time()), qos=1)

    await STOP.wait()
    await client.disconnect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    host = "139.229.178.1"

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main(host))
