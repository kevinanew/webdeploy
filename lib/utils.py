# coding: utf-8
import os
import re

from fabric.api import run
import settings


def print_server_info(env):
    print '%s server:' % env.server_type
    print '--- host:', env.hosts
    print '--- port:', env.port or '22'
    print '--- username:', env.user

    if env.password:
        print '--- password: ******'
    else:
        print '--- password: (Not use)'

    if env.ssh_key_file:
        print '--- ssh key:', env.ssh_key_file


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


def make_dir_if_not_exists(dir_path):
    run('test -d {dir_path} || mkdir {dir_path}'.format(dir_path=dir_path))


def get_files_in_dir(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file_path in files:
            yield os.path.abspath(os.path.join(root, file_path))


def get_config_file(filename):
    config_template_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../config_template'))
    config_template_file = os.path.join(config_template_dir, filename)
    config_template_content = open(config_template_file, 'r').read()

    config_context = dict([(settings_name, getattr(settings, settings_name))
        for settings_name in dir(settings)])
    return config_template_content % config_context
