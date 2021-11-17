#!/usr/bin/env python3
import json
import logging
from datetime import datetime

from aiohttp import web

import bumper
from bumper import plugins


class v1_private_common(plugins.ConfServerApp):
    def __init__(self):
        self.name = "v1_private_common"
        self.plugin_type = "sub_api"
        self.sub_api = "api_v1"

        self.routes = [
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/checkAPPVersion",
                self._handle_checkAPPVersion,
                name="v1_common_checkAppVersion",
            ),
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/checkVersion",
                self._handle_checkVersion,
                name="v1_common_checkVersion",
            ),
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/uploadDeviceInfo",
                self._handle_uploadDeviceInfo,
                name="v1_common_uploadDeviceInfo",
            ),
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getSystemReminder",
                self._handle_getSystemReminder,
                name="v1_common_getSystemReminder",
            ),
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getConfig",
                self._handle_getConfig,
                name="v1_common_getConfig",
            ),
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getAreas",
                self._handle_getAreas,
                name="v1_common_getAreas",
            ),
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getAgreementURLBatch",
                self._handle_getAgreementURLBatch,
                name="v1_common_getAgreementURLBatch",
            ),
            web.route(
                "*",
                "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getTimestamp",
                self._handle_getTimestamp,
                name="v1_common_getTimestamp",
            ),
        ]

        self.get_milli_time = (
            bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
        )

    async def _handle_checkVersion(self, request):
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "c": None,
                    "img": None,
                    "r": 0,
                    "t": None,
                    "u": None,
                    "ut": 0,
                    "v": None,
                },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")

    async def _handle_checkAPPVersion(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "c": None,
                    "downPageUrl": None,
                    "img": None,
                    "nextAlertTime": None,
                    "r": 0,
                    "t": None,
                    "u": None,
                    "ut": 0,
                    "v": None,
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")

    async def _handle_uploadDeviceInfo(self, request):  # EcoVacs Home
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

    async def _handle_getSystemReminder(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "iosGradeTime": {"iodGradeFlag": "N"},
                    "openNotification": {
                        "openNotificationContent": None,
                        "openNotificationFlag": "N",
                        "openNotificationTitle": None,
                    },
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")

    async def _handle_getConfig(self, request):
        try:
            data = []
            for key in request.query["keys"].split(","):
                data.append({"key": key, "value": "Y"})

            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": data,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")

    async def _handle_getAreas(self, request):
        try:
            with open("bumper_confserver_v1_private_common_area.json") as json_file:
                body = {
                    "code": bumper.RETURN_API_SUCCESS,
                    "data": json.load(json_file),
                    "msg": "操作成功",
                    "success": True,
                    "time": self.get_milli_time(datetime.utcnow().timestamp()),
                }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")

    async def _handle_getAgreementURLBatch(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": [
                    {
                        "acceptTime": None,
                        "force": None,
                        "id": "20180804040641_7d746faf18b8cb22a50d145598fe4c90",
                        "type": "USER",
                        "url": "https://gl-eu-wap.ecovacs.com/content/agreement?id=20180804040641_7d746faf18b8cb22a50d145598fe4c90&language=EN",
                        "version": "1.03",
                    },
                    {
                        "acceptTime": None,
                        "force": None,
                        "id": "20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac",
                        "type": "PRIVACY",
                        "url": "https://gl-eu-wap.ecovacs.com/content/agreement?id=20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac&language=EN",
                        "version": "1.03",
                    },
                ],
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")

    async def _handle_getTimestamp(self, request):  # EcoVacs Home
        try:
            time = self.get_milli_time(datetime.utcnow().timestamp())
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {"timestamp": time},
                "msg": "操作成功",
                "success": True,
                "time": time,
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception(f"{e}")


plugin = v1_private_common()
