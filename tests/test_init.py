import asyncio
import json
import os
import platform
from unittest import mock
from unittest.mock import patch

import pytest
from testfixtures import LogCapture
from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage

import bumper


def test_strtobool():
    assert bumper.strtobool("t") == True
    assert bumper.strtobool("f") == False
    assert bumper.strtobool(0) == False


async def test_start_stop():
    with LogCapture() as l:
        if os.path.exists("tests/tmp.db"):
            os.remove("tests/tmp.db")  # Remove existing db

        b = bumper
        b.db = "tests/tmp.db"  # Set db location for testing
        asyncio.create_task(b.start())
        await asyncio.sleep(0.1)
        l.check_present(("bumper", "INFO", "Starting Bumper"))
        l.clear()

        await b.shutdown()
        l.check_present(
            ("bumper", "INFO", "Shutting down"), ("bumper", "INFO", "Shutdown complete")
        )
        assert b.shutting_down == True


async def test_start_stop_debug():
    with LogCapture() as l:
        if os.path.exists("tests/tmp.db"):
            os.remove("tests/tmp.db")  # Remove existing db

        b = bumper
        b.db = "tests/tmp.db"  # Set db location for testing
        b.bumper_listen = "0.0.0.0"
        b.bumper_debug = True
        asyncio.create_task(b.start())

        await asyncio.sleep(0.1)
        while b.mqtt_server.state == "starting":
            await asyncio.sleep(0.1)
        l.check_present(("bumper", "INFO", "Starting Bumper"))
        l.clear()

        asyncio.create_task(b.shutdown())
        await asyncio.sleep(0.1)
        l.check_present(
            ("bumper", "INFO", "Shutting down"), ("bumper", "INFO", "Shutdown complete")
        )
        assert b.shutting_down == True
