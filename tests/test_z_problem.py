from mock import patch

import bumper


def mock_subrun(*args):
    return args


@patch("bumper.start")
def test_argparse(mock_start):
    bumper.ca_cert = "tests/test_certs/ca.crt"
    bumper.server_cert = "tests/test_certs/bumper.crt"
    bumper.server_key = "tests/test_certs/bumper.key"

    bumper.main(["--debug"])
    assert bumper.bumper_debug == True
    assert mock_start.called == True

    bumper.main(["--listen", "127.0.0.1"])
    assert bumper.bumper_listen == "127.0.0.1"
    assert mock_start.called == True

    bumper.main(["--announce", "127.0.0.1"])
    assert bumper.bumper_announce_ip == "127.0.0.1"
    assert mock_start.called == True

    bumper.main(["--debug", "--listen", "127.0.0.1", "--announce", "127.0.0.1"])
    assert bumper.bumper_debug == True
    assert bumper.bumper_announce_ip == "127.0.0.1"
    assert bumper.bumper_listen == "127.0.0.1"
    assert mock_start.called == True
