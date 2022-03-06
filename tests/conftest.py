import asyncio

import pytest
from amqtt.client import MQTTClient

import bumper
from bumper import MQTTServer, WebserverBinding
from tests import HOST, MQTT_PORT, WEBSERVER_PORT


@pytest.fixture
async def mqtt_server():
    mqtt_server = MQTTServer(HOST, MQTT_PORT, password_file="tests/passwd")
    await mqtt_server.start()
    bumper.mqtt_server = mqtt_server
    while not mqtt_server.state == "started":
        await asyncio.sleep(0.1)

    yield

    await mqtt_server.shutdown()


@pytest.mark.usefixtures("mqtt_server")
@pytest.fixture
async def mqtt_client():
    client = MQTTClient(
        client_id="helperbot@bumper/test",
        config={"check_hostname": False, "auto_reconnect": False},
    )

    await client.connect(f"mqtts://{HOST}:{MQTT_PORT}/", cafile=bumper.ca_cert)

    yield client

    await client.disconnect()


@pytest.fixture
async def webserver_client(aiohttp_client):
    webserver = bumper.WebServer(WebserverBinding(HOST, WEBSERVER_PORT, False))
    client = await aiohttp_client(webserver._app)

    yield client

    await client.close()
