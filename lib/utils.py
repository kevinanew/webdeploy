# coding: utf-8
import os
import re

from fabric.api import run, local, sudo, put
from fabric.contrib import files

import settings


def print_server_info(env):
    print '%s server:' % env.server_type
    print '--- host:', env.hosts
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
    for root, dirs, _files in os.walk(root_dir):
        for file_path in _files:
            yield os.path.abspath(os.path.join(root, file_path))


def get_config_file(filename):
    config_template_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../config_template'))
    config_template_file = os.path.join(config_template_dir, filename)
    config_template_content = open(config_template_file, 'r').read()

    config_context = dict([(settings_name, getattr(settings, settings_name))
        for settings_name in dir(settings)])
    return config_template_content % config_context


def backup(remote_path, use_sudo=False):
    # bak remote file
    if files.exists(remote_path):
        bak_cmd = 'mv "%s" "%s.bak"' % (remote_path, remote_path)
        print "Backup:", remote_path, '->', '%s.bak' % remote_path
        if use_sudo:
            sudo(bak_cmd)
        else:
            run(bak_cmd)

def upload(local_config_file, remote_config_file, use_sudo, mode):
    mkdir_cmd = ('test -d {dirname} || mkdir -p {dirname} ||'
        ' echo "skip"').format(dirname=os.path.dirname(remote_config_file))
    if use_sudo:
        sudo(mkdir_cmd)
    else:
        run(mkdir_cmd)

    put(local_config_file, remote_config_file, use_sudo=True, mode=0644)


def is_same_content(local_path, remote_path):
    md5py_content = """
import sys, hashlib, os
if __name__ == '__main__':
    if os.path.exists(sys.argv[1]):
        print hashlib.md5(open(sys.argv[1], 'rb').read()).hexdigest()
"""

    open('md5.py', 'w').write(md5py_content)
    local_md5 = local('python md5.py %s' % local_path, capture=True)

    put('md5.py', 'md5.py')
    remote_md5 = run('python md5.py %s' % remote_path)

    os.remove('md5.py')
    run('rm md5.py')

    if local_md5 == remote_md5:
        print "[Same]:",
    else:
        print "[Different]:",

    print 'local:', local_path, '-> remote:', remote_path
    return local_md5 == remote_md5

