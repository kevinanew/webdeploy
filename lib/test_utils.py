# coding: utf-8
import utils


def test_parse_ip_and_port():
    utils.parse_ip_and_port('127.0.0.1', default_port=22)

    try:
        utils.parse_ip_and_port('999.21.354.2', default_port=22)
    except Exception:
        pass
    else:
        raise
