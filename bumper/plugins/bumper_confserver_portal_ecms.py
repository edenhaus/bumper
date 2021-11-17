#!/usr/bin/env python3
import logging

from aiohttp import web

import bumper
from bumper import plugins


class portal_api_ecms(plugins.ConfServerApp):
    def __init__(self):
        self.name = "portal_api_ecms"
        self.plugin_type = "sub_api"
        self.sub_api = "portal_api"

        self.routes = [
            web.route(
                "*",
                "/ecms/app/ad/res",
                self._handle_ad_res,
                name="portal_api_ecms_ad_res",
            ),
        ]

        self.get_milli_time = (
            bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
        )

    async def _handle_ad_res(self, request):
        try:
            body = {"code": 0, "data": [], "message": "success", "success": True}

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")


plugin = portal_api_ecms()
