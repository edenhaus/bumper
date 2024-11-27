"""Database module."""
import os
from datetime import datetime, timedelta
from typing import Any

from tinydb import Query, TinyDB
from tinydb.table import Document

import bumper
from bumper.models import BumperUser, OAuth, VacBotClient, VacBotDevice

from .util import get_logger

_LOGGER = get_logger("db")


def _db_file() -> str:
    return os.environ.get("DB_FILE") or _os_db_path()


def _os_db_path() -> str:  # createdir=True):
    return os.path.join(bumper.data_dir, "bumper.db")


def _db_get() -> TinyDB:
    # Will create the database if it doesn't exist
    db = TinyDB(_db_file())

    # Will create the tables if they don't exist
    db.table("users", cache_size=0)
    db.table("clients", cache_size=0)
    db.table("bots", cache_size=0)
    db.table("tokens", cache_size=0)
    db.table("oauth", cache_size=0)

    return db


def user_add(userid: str) -> None:
    """Add user."""
    newuser = BumperUser()
    newuser.userid = userid

    user = user_get(userid)
    if not user:
        _LOGGER.info(f"Adding new user with userid: {newuser.userid}")
        _user_full_upsert(newuser.asdict())


def user_get(userid: str) -> None | Document:
    """Get user."""
    users = _db_get().table("users")
    User = Query()
    return users.get(User.userid == userid)


def user_by_device_id(deviceid: str) -> None | Document:
    """Get user by device id."""
    users = _db_get().table("users")
    User = Query()
    return users.get(User.devices.any([deviceid]))


def _user_full_upsert(user: dict[str, Any]) -> None:
    opendb = _db_get()
    with opendb:
        users = opendb.table("users")
        User = Query()
        users.upsert(user, User.did == user["userid"])


def user_add_device(userid: str, devid: str) -> None:
    """Add device to user."""
    opendb = _db_get()
    with opendb:
        users = opendb.table("users")
        User = Query()
        user = users.get(User.userid == userid)
        if user:
            userdevices = list(user["devices"])
            if devid not in userdevices:
                userdevices.append(devid)

        users.upsert({"devices": userdevices}, User.userid == userid)


def user_remove_device(userid: str, devid: str) -> None:
    """Remove device from user."""
    opendb = _db_get()
    with opendb:
        users = opendb.table("users")
        User = Query()
        user = users.get(User.userid == userid)
        if user:
            userdevices = list(user["devices"])
            if devid in userdevices:
                userdevices.remove(devid)

        users.upsert({"devices": userdevices}, User.userid == userid)


def user_add_bot(userid: str, did: str) -> None:
    """Add bot to user."""
    opendb = _db_get()
    with opendb:
        users = opendb.table("users")
        User = Query()
        user = users.get(User.userid == userid)
        if user:
            userbots = list(user["bots"])
            if did not in userbots:
                userbots.append(did)

        users.upsert({"bots": userbots}, User.userid == userid)


def user_remove_bot(userid: str, did: str) -> None:
    """Remove bot from user."""
    opendb = _db_get()
    with opendb:
        users = opendb.table("users")
        User = Query()
        user = users.get(User.userid == userid)
        if user:
            userbots = list(user["bots"])
            if did in userbots:
                userbots.remove(did)

        users.upsert({"bots": userbots}, User.userid == userid)


def user_get_tokens(userid: str) -> list[Document]:
    """Get all tokens by given user."""
    tokens = _db_get().table("tokens")
    return tokens.search(Query().userid == userid)


def user_get_token(userid: str, token: str) -> Document | None:
    """Get token by user."""
    tokens = _db_get().table("tokens")
    return tokens.get((Query().userid == userid) & (Query().token == token))


def user_add_token(userid: str, token: str) -> None:
    """Ass token for given user."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
        if not tmptoken:
            _LOGGER.debug(f"Adding token {token} for userid {userid}")
            tokens.insert(
                {
                    "userid": userid,
                    "token": token,
                    "expiration": "{}".format(
                        datetime.now()
                        + timedelta(seconds=bumper.token_validity_seconds)
                    ),
                }
            )


def user_revoke_all_tokens(userid: str) -> None:
    """Revoke all tokens for given user."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tsearch = tokens.search(Query().userid == userid)
        for i in tsearch:
            tokens.remove(doc_ids=[i.doc_id])


def user_revoke_expired_tokens(userid: str) -> None:
    """Revoke expired user tokens."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tsearch = tokens.search(Query().userid == userid)
        for i in tsearch:
            if datetime.now() >= datetime.fromisoformat(i["expiration"]):
                _LOGGER.debug("Removing token {} due to expiration".format(i["token"]))
                tokens.remove(doc_ids=[i.doc_id])


def user_revoke_token(userid: str, token: str) -> None:
    """Revoke user token."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
        if tmptoken:
            tokens.remove(doc_ids=[tmptoken.doc_id])


def user_add_authcode(userid: str, token: str, authcode: str) -> None:
    """Add user authcode."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
        if tmptoken:
            tokens.upsert(
                {"authcode": authcode},
                ((Query().userid == userid) & (Query().token == token)),
            )


def user_revoke_authcode(userid: str, token: str) -> None:
    """Revoke user authcode."""
    opendb = _db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
        if tmptoken:
            tokens.upsert(
                {"authcode": ""},
                ((Query().userid == userid) & (Query().token == token)),
            )


def revoke_expired_oauths() -> None:
    """Revoke expired oauths."""
    opendb = _db_get()
    with opendb:
        table = opendb.table("oauth")
        entries = table.all()

        for i in entries:
            oauth = OAuth(**i)
            if datetime.now() >= datetime.fromisoformat(oauth.expire_at):
                _LOGGER.debug(f"Removing oauth {oauth.access_token} due to expiration")
                table.remove(doc_ids=[i.doc_id])


def user_revoke_expired_oauths(userid: str) -> None:
    """Revoke expired oauths by user."""
    opendb = _db_get()
    with opendb:
        table = opendb.table("oauth")
        search = table.search(Query().userid == userid)
        for i in search:
            oauth = OAuth(**i)
            if datetime.now() >= datetime.fromisoformat(oauth.expire_at):
                _LOGGER.debug(f"Removing oauth {oauth.access_token} due to expiration")
                table.remove(doc_ids=[i.doc_id])


def user_add_oauth(userid: str) -> OAuth:
    """Add oauth for user."""
    user_revoke_expired_oauths(userid)
    opendb = _db_get()
    with opendb:
        table = opendb.table("oauth")
        entry = table.get(Query().userid == userid)
        if entry:
            return OAuth(**entry)
        else:
            oauth = OAuth.create_new(userid)
            _LOGGER.debug(f"Adding oauth {oauth.access_token} for userid {userid}")
            table.insert(oauth.toDB())
            return oauth


def token_by_authcode(authcode: str) -> Document | None:
    """Get token by authcode."""
    tokens = _db_get().table("tokens")
    return tokens.get(Query().authcode == authcode)


def get_disconnected_xmpp_clients() -> list[Document]:
    """Get disconnected XMPP clients."""
    clients = _db_get().table("clients")
    client = Query()
    return clients.search(client.xmpp_connection == False)  # noqa: E712


def check_authcode(uid: str, authcode: str) -> bool:
    """Check authcode."""
    _LOGGER.debug(f"Checking for authcode: {authcode}")
    tokens = _db_get().table("tokens")
    tmpauth = tokens.get(
        (Query().authcode == authcode)
        & (  # Match authcode
            (Query().userid == uid.replace("fuid_", ""))
            | (Query().userid == f"fuid_{uid}")
        )  # Userid with or without fuid_
    )
    if tmpauth:
        return True

    return False


def login_by_it_token(authcode: str) -> dict[str, str]:
    """Login by token."""
    _LOGGER.debug(f"Checking for authcode: {authcode}")
    tokens = _db_get().table("tokens")
    tmpauth = tokens.get(
        Query().authcode
        == authcode
        # & (  # Match authcode
        #    (Query().userid == uid.replace("fuid_", ""))
        #    | (Query().userid == "fuid_{}".format(uid))
        # )  # Userid with or without fuid_
    )
    if tmpauth:
        return {"token": tmpauth["token"], "userid": tmpauth["userid"]}

    return {}


def check_token(uid: str, token: str) -> bool:
    """Check token."""
    _LOGGER.debug(f"Checking for token: {token}")
    tokens = _db_get().table("tokens")
    tmpauth = tokens.get(
        (Query().token == token)
        & (  # Match token
            (Query().userid == uid.replace("fuid_", ""))
            | (Query().userid == f"fuid_{uid}")
        )  # Userid with or without fuid_
    )
    if tmpauth:
        return True

    return False


def revoke_expired_tokens() -> None:
    """Revoke expired tokens."""
    tokens = _db_get().table("tokens").all()
    for i in tokens:
        if datetime.now() >= datetime.fromisoformat(i["expiration"]):
            _LOGGER.debug("Removing token {} due to expiration".format(i["token"]))
            _db_get().table("tokens").remove(doc_ids=[i.doc_id])


def bot_add(sn: str, did: str, dev_class: str, resource: str, company: str) -> None:
    """Add bot."""
    bot = bot_get(did) or {}
    new_bot = VacBotDevice(**bot)
    new_bot.did = did
    new_bot.name = sn
    new_bot.vac_bot_device_class = dev_class
    new_bot.resource = resource
    new_bot.company = company

    if (not dev_class) or "@" in sn or "tmp" in sn:
        # try to prevent bad additions to the bot list
        _LOGGER.warning(f"Skipping new bot with DID: {new_bot.did}: {new_bot.asdict()}")
        return

    _LOGGER.info(f"Adding new bot with SN: {new_bot.name} DID: {new_bot.did}")
    bot_full_upsert(new_bot.asdict())


def bot_remove(did: str) -> None:
    """Remove bot."""
    bots = _db_get().table("bots")
    bot = bot_get(did)
    if bot:
        bots.remove(doc_ids=[bot.doc_id])


def bot_get(did: str) -> Document | None:
    """Get bot."""
    bots = _db_get().table("bots")
    bot = Query()
    return bots.get(bot.did == did)


def bot_full_upsert(vacbot: dict[str, Any]) -> None:
    """Upsert bot."""
    bots = _db_get().table("bots")
    bot = Query()
    if "did" in vacbot:
        bots.upsert(vacbot, bot.did == vacbot["did"])
    else:
        _LOGGER.error(f"No DID in vacbot: {vacbot}")


def bot_set_nick(did: str, nick: str) -> None:
    """Bot set nickname."""
    bots = _db_get().table("bots")
    bot = Query()
    bots.upsert({"nick": nick}, bot.did == did)


def bot_set_mqtt(did: str, mqtt: bool) -> None:
    """Bot ste MQTT status."""
    bots = _db_get().table("bots")
    bot = Query()
    bots.upsert({"mqtt_connection": mqtt}, bot.did == did)


def bot_set_xmpp(did: str, xmpp: bool) -> None:
    """Bot set XMPP status."""
    bots = _db_get().table("bots")
    bot = Query()
    bots.upsert({"xmpp_connection": xmpp}, bot.did == did)


def client_add(userid: str, realm: str, resource: str) -> None:
    """Add client."""
    new_client = VacBotClient()
    new_client.userid = userid
    new_client.realm = realm
    new_client.resource = resource

    client = client_get(resource)
    if not client:
        _LOGGER.info(f"Adding new client with resource {new_client.resource}")
        _client_full_upsert(new_client.asdict())


def client_remove(resource: str) -> None:
    """Remove client."""
    clients = _db_get().table("clients")
    client = client_get(resource)
    if client:
        clients.remove(doc_ids=[client.doc_id])


def client_get(resource: str) -> Document | None:
    """Get client by resource."""
    clients = _db_get().table("clients")
    client = Query()
    return clients.get(client.resource == resource)


def _client_full_upsert(client: dict[str, Any]) -> None:
    clients = _db_get().table("clients")
    client_query = Query()
    clients.upsert(client, client_query.resource == client["resource"])


def client_set_mqtt(resource: str, mqtt: bool) -> None:
    """Client set MQTT status."""
    clients = _db_get().table("clients")
    client = Query()
    clients.upsert({"mqtt_connection": mqtt}, client.resource == resource)


def client_set_xmpp(resource: str, xmpp: bool) -> None:
    """Client set XMPP status."""
    clients = _db_get().table("clients")
    client = Query()
    clients.upsert({"xmpp_connection": xmpp}, client.resource == resource)


def bot_reset_connection_status() -> None:
    """Reset all bot connection status."""
    bots = _db_get().table("bots")
    for bot in bots:
        bot_set_mqtt(bot["did"], False)
        bot_set_xmpp(bot["did"], False)


def client_reset_connection_status() -> None:
    """Reset all client connection status."""
    clients = _db_get().table("clients")
    for client in clients:
        client_set_mqtt(client["resource"], False)
        client_set_xmpp(client["resource"], False)
