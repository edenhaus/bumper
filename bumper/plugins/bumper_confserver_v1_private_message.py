#!/usr/bin/env python3
import logging
from datetime import datetime

from aiohttp import web

import bumper
from bumper import plugins


class v1_private_message(plugins.ConfServerApp):
    def __init__(self):
        self.name = "v1_private_message"
        self.plugin_type = "sub_api"
        self.sub_api = "api_v1"

        self.routes = [
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/message/hasUnreadMsg",
                self._handle_hasUnreadMessage,
                name="v1_message_hasUnreadMsg",
            ),
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/message/getMsgList",
                self._handle_getMsgList,
                name="v1_message_getMsgList",
            ),
        ]

        self.get_milli_time = (
            bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
        )

    async def _handle_hasUnreadMessage(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": "N",
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")

    async def _handle_getMsgList(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {"hasNextPage": 0, "items": []},
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")


plugin = v1_private_message()
