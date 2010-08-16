# coding: utf-8
import re


def print_server_info(env):
    print '%s server:' % env.server_type
    print '--- host:', env.hosts
    print '--- port:', env.port
    print '--- username:', env.user

    if env.password:
        print '--- password: ******'
    else:
        print '--- password: (Not use)'


def parse_ip_and_port(host, default_port):
    """
    parse ip_address and port by host string
    """
    _host = host.strip()

    if ":" in _host:
        ip_address, ip_port = _host.split(':')
        if ip_port.isdigit():
            ip_port = int(ip_port)
        else:
            raise Exception
    else:
        ip_address = _host
        ip_port = default_port

    # validate ip address
    ipv4_re = re.compile((r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)'
        '(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$'))
    if not ipv4_re.search(ip_address):
        raise Exception

    return ip_address, ip_port
