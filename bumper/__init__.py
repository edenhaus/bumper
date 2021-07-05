#!/usr/bin/env python3
import asyncio
import importlib
import pkgutil
import socket
import sys
from typing import Optional

from bumper.confserver import ConfServer
from bumper.db import *
from bumper.models import *
from bumper.mqttserver import MQTTServer, MQTTHelperBot
from bumper.util import get_logger, log_to_stdout
from bumper.xmppserver import XMPPServer


def strtobool(strbool):
    if str(strbool).lower() in ["true", "1", "t", "y", "on", "yes"]:
        return True
    else:
        return False


# os.environ['PYTHONASYNCIODEBUG'] = '1' # Uncomment to enable ASYNCIODEBUG
bumper_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# Set defaults from environment variables first
# Folders
if not log_to_stdout:
    logs_dir = os.environ.get("BUMPER_LOGS") or os.path.join(bumper_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)  # Ensure logs directory exists or create
data_dir = os.environ.get("BUMPER_DATA") or os.path.join(bumper_dir, "data")
os.makedirs(data_dir, exist_ok=True)  # Ensure data directory exists or create
certs_dir = os.environ.get("BUMPER_CERTS") or os.path.join(bumper_dir, "certs")
os.makedirs(certs_dir, exist_ok=True)  # Ensure data directory exists or create

# Certs
ca_cert = os.environ.get("BUMPER_CA") or os.path.join(certs_dir, "ca.crt")
server_cert = os.environ.get("BUMPER_CERT") or os.path.join(certs_dir, "bumper.crt")
server_key = os.environ.get("BUMPER_KEY") or os.path.join(certs_dir, "bumper.key")

# Listeners
bumper_listen = os.environ.get("BUMPER_LISTEN") or socket.gethostbyname(
    socket.gethostname()
)

bumper_announce_ip = os.environ.get("BUMPER_ANNOUNCE_IP") or bumper_listen

# Other
bumper_debug = strtobool(os.environ.get("BUMPER_DEBUG")) or False
use_auth = False
token_validity_seconds = 3600  # 1 hour
oauth_validity_days = 15
db = None
bumper_proxy_mode = strtobool(os.environ.get("BUMPER_PROXY_MODE")) or False

mqtt_server: Optional[MQTTServer] = None
mqtt_helperbot: Optional[MQTTHelperBot] = None
conf_server: Optional[ConfServer] = None
conf_server_2: Optional[ConfServer] = None
xmpp_server: Optional[XMPPServer] = None

# Plugins
sys.path.append(os.path.join(bumper_dir, "bumper", "plugins"))
sys.path.append(os.path.join(data_dir, "plugins"))

discovered_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg in pkgutil.iter_modules()
    if name.startswith('bumper_')
}

shutting_down = False

bumperlog = get_logger("bumper")
logging.getLogger("asyncio").setLevel(logging.CRITICAL + 1)  # Ignore this logger
proxymodelog =  get_logger("proxymode")

# iptables -A PREROUTING -t nat -i wlp0s20f3 -p tcp --dport 443 -j REDIRECT --to-port 8883
mqtt_listen_port = 8883
conf1_listen_port = 443
conf2_listen_port = 8007
xmpp_listen_port = 5223


async def start():
    #config_proxyMode_deleteTable() #delete existing proxymode table

    #Reset xmpp/mqtt to false in database for bots and clients
    bot_reset_connectionStatus()
    client_reset_connectionStatus()

    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()

    if bumper_debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s",
        )
        loop.set_debug(True)  # Set asyncio loop to debug
        # logging.getLogger("asyncio").setLevel(logging.DEBUG)  # Show debug asyncio logs (disabled in init, uncomment for debugging asyncio)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s",
        )

    if not bumper_listen:
        bumperlog.fatal("No listen address configured")
        return

    if not (
            os.path.exists(ca_cert)
            and os.path.exists(server_cert)
            and os.path.exists(server_key)
    ):
        bumperlog.fatal("Certificate(s) don't exist at paths specified")
        return

    bumperlog.info("Starting Bumper")
    global mqtt_server
    mqtt_server = MQTTServer((bumper_listen, mqtt_listen_port))
    global mqtt_helperbot
    mqtt_helperbot = MQTTHelperBot((bumper_listen, mqtt_listen_port))
    global conf_server
    conf_server = ConfServer((bumper_listen, conf1_listen_port), usessl=True)
    global conf_server_2
    conf_server_2 = ConfServer((bumper_listen, conf2_listen_port), usessl=False)
    global xmpp_server
    xmpp_server = XMPPServer((bumper_listen, xmpp_listen_port))

    # Start MQTT Server
    # await start otherwise we get an error connecting the helper bot
    await asyncio.create_task(mqtt_server.broker_coro())

    await asyncio.sleep(0.5) #Wait half a sec for broker to start

    # Start MQTT Helperbot
    asyncio.create_task(mqtt_helperbot.start_helper_bot())

    # Start XMPP Server
    asyncio.create_task(xmpp_server.start_async_server())

    # Wait for helperbot to connect first
    while mqtt_helperbot.Client is None:
        await asyncio.sleep(0.1)

    while not mqtt_helperbot.Client.session.transitions.state == "connected":
        await asyncio.sleep(0.1)

    # Start web servers
    if bumper_proxy_mode:
        bumperlog.info("Proxy Mode Enabled")
        if config_proxyMode_countEntries() == 0: # check if proxymode servers are entered
            bumperlog.info("Proxy Mode - No Servers, Loading Defaults (US)")
            config_proxyMode_defaults() # set defaults if 0

        configproxy = config_proxyMode_getall()
        cntentries = len(configproxy)
        proxymodelog.info(f"Loaded {cntentries} entries from proxyconfig")
        for entry in configproxy:
            proxymodelog.info(f"Config Entry {entry}")

        conf_server.confserver_proxy_app()
    else:
        conf_server.confserver_app()

    asyncio.create_task(conf_server.start_site(conf_server.app, address=bumper_listen, port=conf1_listen_port, usessl=True))
    asyncio.create_task(conf_server.start_site(conf_server.app, address=bumper_listen, port=conf2_listen_port, usessl=False))

    # Start maintenance
    while not shutting_down:
        asyncio.create_task(maintenance())
        await asyncio.sleep(5)


async def maintenance():
    revoke_expired_tokens()
    revoke_expired_oauths()


async def shutdown():
    try:
        bumperlog.info("Shutting down")

        await conf_server.stop_server()
        await conf_server_2.stop_server()
        if mqtt_server.broker.transitions.state == "started":
            await mqtt_server.broker.shutdown()
        elif mqtt_server.broker.transitions.state == "starting":
            while mqtt_server.broker.transitions.state == "starting":
                await asyncio.sleep(0.1)
            if mqtt_server.broker.transitions.state == "started":
                await mqtt_server.broker.shutdown()
                await mqtt_helperbot.Client.disconnect()
        if xmpp_server.server:
            if xmpp_server.server._serving:
                xmpp_server.server.close()
            await xmpp_server.server.wait_closed()
        global shutting_down
        shutting_down = True

    except asyncio.CancelledError:
        bumperlog.info("Coroutine canceled")

    except Exception as e:
        bumperlog.info("Exception: {}".format(e))

    finally:
        bumperlog.info("Shutdown complete")


def main(argv=None):
    import argparse

    global bumper_debug
    global bumper_listen
    global bumper_announce_ip
    if not argv:
        argv = sys.argv[1:]  # Set argv to argv[1:] if not passed into main
    try:

        if not (
                os.path.exists(ca_cert)
                and os.path.exists(server_cert)
                and os.path.exists(server_key)
        ):
            msg = "No certs found! Please generate them (More infos in the docs)"
            bumperlog.fatal(msg)
            sys.exit(msg)

        if not (
                os.path.exists(os.path.join(data_dir, "passwd"))
        ):
            with open(os.path.join(data_dir, "passwd"), 'w'): pass

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--listen", type=str, default=None, help="start serving on address"
        )
        parser.add_argument(
            "--announce",
            type=str,
            default=None,
            help="announce address to bots on checkin",
        )
        parser.add_argument("--debug", action="store_true", help="enable debug logs")
        parser.add_argument("--proxy-mode", action="store_true", help="enable proxy mode")

        args = parser.parse_args(args=argv)

        if args.debug:
            bumper_debug = True

        if args.proxy_mode:
            global bumper_proxy_mode
            bumper_proxy_mode = True

        if args.listen:
            bumper_listen = args.listen

        if args.announce:
            bumper_announce_ip = args.announce

        asyncio.run(start())

    except KeyboardInterrupt:
        bumperlog.info("Keyboard Interrupt!")
        pass

    except Exception as e:
        bumperlog.exception(e)
        pass

    finally:
        asyncio.run(shutdown())
