"""Models module."""
import uuid
from datetime import datetime, timedelta
from typing import Any

import bumper
from bumper.util import convert_to_millis


class VacBotDevice:
    """Vacuum device."""

    def __init__(
        self,
        did: str = "",
        vac_bot_device_class: str = "",
        resource: str = "",
        name: str = "",
        nick: str = "",
        company: str = "",
        **kwargs: Any,
    ):
        self.vac_bot_device_class = vac_bot_device_class or kwargs.get("class", "")
        self.company = company
        self.did = did
        self.name = name
        self.nick = nick
        self.resource = resource
        self.mqtt_connection = False
        self.xmpp_connection = False

    def asdict(self) -> dict[str, str | bool]:
        """Convert to dict."""
        return {
            "class": self.vac_bot_device_class,
            "company": self.company,
            "did": self.did,
            "name": self.name,
            "nick": self.nick,
            "resource": self.resource,
            "mqtt_connection": self.mqtt_connection,
            "xmpp_connection": self.xmpp_connection,
        }


class BumperUser:
    """Bumper user."""

    def __init__(self, userid: str = ""):
        self.userid = userid
        self.devices: list[str] = []
        self.bots: list[str] = []

    def asdict(self) -> dict[str, Any]:
        """Convert to dict."""
        return {"userid": self.userid, "devices": self.devices, "bots": self.bots}


class GlobalVacBotDevice(VacBotDevice):
    """Global vacuum device."""

    UILogicId = ""
    ota = True
    updateInfo = {"changeLog": "", "needUpdate": False}
    icon = ""
    deviceName = ""


class VacBotClient:
    """Vacuum client."""

    def __init__(self, userid: str = "", realm: str = "", token: str = ""):
        self.userid = userid
        self.realm = realm
        self.resource = token
        self.mqtt_connection = False
        self.xmpp_connection = False

    def asdict(self) -> dict[str, Any]:
        """Convert to dict."""
        return {
            "userid": self.userid,
            "realm": self.realm,
            "resource": self.resource,
            "mqtt_connection": self.mqtt_connection,
            "xmpp_connection": self.xmpp_connection,
        }


class OAuth:
    """Oauth."""

    access_token = ""
    expire_at = ""
    refresh_token = ""
    userId = ""

    def __init__(self, **entries: str):
        self.__dict__.update(entries)

    @classmethod
    def create_new(cls, userId: str) -> "OAuth":
        """Create new."""
        oauth = OAuth()
        oauth.userId = userId
        oauth.access_token = uuid.uuid4().hex
        oauth.expire_at = (
            f"{datetime.utcnow() + timedelta(days=bumper.oauth_validity_days)}"
        )
        oauth.refresh_token = uuid.uuid4().hex
        return oauth

    def toDB(self) -> dict:
        """Convert for db."""
        return self.__dict__

    def toResponse(self) -> dict:
        """Convert to response."""
        data = self.__dict__
        data["expire_at"] = convert_to_millis(
            datetime.fromisoformat(self.expire_at).timestamp()
        )
        return data


RETURN_API_SUCCESS = "0000"
ERR_ACTIVATE_TOKEN_TIMEOUT = "1006"
ERR_COMMON = "0001"
ERR_DEFAULT = "9000"
ERR_EMAIL_NON_EXIST = "1002"
ERR_EMAIL_SEND_TIME_LIMIT = "1011"
ERR_EMAIL_USED = "1001"
ERR_INTERFACE_AUTH = "0002"
ERR_PARAM_INVALID = "0003"
ERR_PWD_WRONG = "1005"
ERR_RESET_PWD_TOKEN_TIMEOUT = "1007"
ERR_TIMESTAMP_INVALID = "0005"
ERR_TOKEN_INVALID = "0004"
ERR_USER_DISABLE = "1004"
ERR_USER_NOT_ACTIVATED = "1003"
ERR_WRONG_COMFIRM_PWD = "10010"
ERR_WRONG_EMAIL_ADDRESS = "1008"
ERR_WRONG_PWD_FROMATE = "1009"

API_ERRORS = {
    RETURN_API_SUCCESS: "0000",
    ERR_ACTIVATE_TOKEN_TIMEOUT: "1006",
    ERR_COMMON: "0001",
    ERR_DEFAULT: "9000",
    ERR_EMAIL_NON_EXIST: "1002",
    ERR_EMAIL_SEND_TIME_LIMIT: "1011",
    ERR_EMAIL_USED: "1001",
    ERR_INTERFACE_AUTH: "0002",
    ERR_PARAM_INVALID: "0003",
    ERR_PWD_WRONG: "1005",
    ERR_RESET_PWD_TOKEN_TIMEOUT: "1007",
    ERR_TIMESTAMP_INVALID: "0005",
    ERR_TOKEN_INVALID: "0004",
    ERR_USER_DISABLE: "1004",
    ERR_USER_NOT_ACTIVATED: "1003",
    ERR_WRONG_COMFIRM_PWD: "10010",
    ERR_WRONG_EMAIL_ADDRESS: "1008",
    ERR_WRONG_PWD_FROMATE: "1009",
}
