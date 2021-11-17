#!/usr/bin/env python3
import logging
from datetime import datetime

from aiohttp import web

import bumper
from bumper import plugins


class v1_private_ad(plugins.ConfServerApp):
    def __init__(self):
        self.name = "v1_private_ad"
        self.plugin_type = "sub_api"
        self.sub_api = "api_v1"

        self.routes = [
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/ad/getAdByPositionType",
                self._handle_getAdByPositionType,
                name="v1_ad_getAdByPositionType",
            ),
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/ad/getBootScreen",
                self._handle_getBootScreen,
                name="v1_ad_getBootScreen",
            ),
        ]

        self.get_milli_time = (
            bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
        )

    async def _handle_getAdByPositionType(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": None,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")

    async def _handle_getBootScreen(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": None,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")


plugin = v1_private_ad()
