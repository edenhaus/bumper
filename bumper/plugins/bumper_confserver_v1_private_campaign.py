#!/usr/bin/env python3
import logging
from datetime import datetime, timedelta

from aiohttp import web

import bumper
from bumper import plugins


class v1_private_campaign(plugins.ConfServerApp):
    def __init__(self):
        self.name = "v1_private_campaign"
        self.plugin_type = "sub_api"
        self.sub_api = "api_v1"

        self.routes = [
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/campaign/homePageAlert",
                self._handle_homePageAlert,
                name="v1_campaign_homePageAlert",
            ),
        ]

        self.get_milli_time = (
            bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
        )

    async def _handle_homePageAlert(self, request):
        try:
            nextAlert = self.get_milli_time(
                (datetime.now() + timedelta(hours=12)).timestamp()
            )

            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "clickSchemeUrl": None,
                    "clickWebUrl": None,
                    "hasCampaign": "N",
                    "imageUrl": None,
                    "nextAlertTime": nextAlert,
                    "serverTime": self.get_milli_time(datetime.utcnow().timestamp()),
                },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")


plugin = v1_private_campaign()
