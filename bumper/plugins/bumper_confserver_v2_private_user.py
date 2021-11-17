#!/usr/bin/env python3
import asyncio
import logging
from datetime import datetime, timedelta

from aiohttp import web

import bumper
from bumper import plugins
from bumper.models import *


class v2_private_user(plugins.ConfServerApp):
    def __init__(self):

        self.name = "v2_private_user"
        self.plugin_type = "sub_api"
        self.sub_api = "api_v2"

        authhandler = bumper.ConfServer.ConfServer_AuthHandler()
        self.routes = [
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkLogin",
                authhandler.login,
                name="v2_user_checkLogin",
            ),
        ]

        self.get_milli_time = (
            bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
        )


plugin = v2_private_user()
