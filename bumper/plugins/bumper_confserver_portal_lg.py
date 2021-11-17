#!/usr/bin/env python3
import json
import logging
import random
import string
import xml.etree.ElementTree as ET

from aiohttp import web

import bumper
from bumper import plugins


class portal_api_lg(plugins.ConfServerApp):
    def __init__(self):
        self.name = "portal_api_lg"
        self.plugin_type = "sub_api"
        self.sub_api = "portal_api"

        self.routes = [
            web.route("*", "/lg/log.do", self._handle_lg_log, name="portal_api_lg_log"),
        ]

        self.get_milli_time = (
            bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
        )

    async def _handle_lg_log(self, request):  # EcoVacs Home
        randomid = "".join(random.sample(string.ascii_letters, 6))

        try:
            json_body = json.loads(await request.text())

            did = json_body["did"]

            botdetails = bumper.bot_get(did)
            if botdetails:
                if "cmdName" not in json_body:
                    if "td" in json_body:
                        json_body["cmdName"] = json_body["td"]

                if "toId" not in json_body:
                    json_body["toId"] = did

                if "toType" not in json_body:
                    json_body["toType"] = botdetails["class"]

                if "toRes" not in json_body:
                    json_body["toRes"] = botdetails["resource"]

                if "payloadType" not in json_body:
                    json_body["payloadType"] = "x"

                if "payload" not in json_body:
                    # json_body["payload"] = ""
                    if json_body["td"] == "GetCleanLogs":
                        json_body["td"] = "q"
                        json_body["payload"] = '<ctl count="30"/>'

            if did != "":
                bot = bumper.bot_get(did)
                if bot["company"] == "eco-ng":
                    retcmd = await bumper.mqtt_helperbot.send_command(
                        json_body, randomid
                    )
                    body = retcmd
                    logging.debug(f"Send Bot - {json_body}")
                    logging.debug(f"Bot Response - {body}")
                    logs = []
                    logsroot = ET.fromstring(retcmd["resp"])
                    if logsroot.attrib["ret"] == "ok":
                        cleanlogs = logsroot.getchildren()
                        for log in cleanlogs:
                            cleanlog = {
                                "ts": log.attrib["s"],
                                "area": log.attrib["a"],
                                "last": log.attrib["l"],
                                "cleanType": log.attrib["t"],
                                # imageUrl allows for providing images of cleanings, something to look into later
                                # "imageUrl": "https://localhost:8007",
                            }
                            logs.append(cleanlog)
                        body = {
                            "ret": "ok",
                            "logs": logs,
                        }

                    else:
                        body = {"ret": "ok", "logs": []}

                    logging.debug(f"lg logs return: {json.dumps(body)}")
                    return web.json_response(body)
                else:
                    # No response, send error back
                    logging.error(
                        "No bots with DID: {} connected to MQTT".format(
                            json_body["toId"]
                        )
                    )

        except Exception as e:
            logging.exception(f"{e}")

        body = {"id": randomid, "errno": bumper.ERR_COMMON, "ret": "fail"}
        return web.json_response(body)


plugin = portal_api_lg()
