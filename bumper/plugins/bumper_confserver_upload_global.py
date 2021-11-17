#!/usr/bin/env python3
import logging
import os

from aiohttp import web

import bumper
from bumper import plugins


class upload_global(plugins.ConfServerApp):
    def __init__(self):
        self.name = "upload_global"
        self.plugin_type = "sub_api"
        self.sub_api = "upload_api"

        self.routes = [
            web.route(
                "*",
                "/global/{year}/{month}/{day}/{fileid}",
                self._handle_upload_global_file,
                name="upload_global_getFile",
            ),
        ]

        self.get_milli_time = (
            bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
        )

    async def _handle_upload_global_file(self, request):
        try:
            return web.FileResponse(
                os.path.join(
                    bumper.bumper_dir, "bumper", "web", "images", "robotvac_image.jpg"
                )
            )

        except Exception as e:
            logging.exception(f"{e}")


plugin = upload_global()
