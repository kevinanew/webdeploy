# coding: utf8
"""
Useage:
Deploy Staging Server:
    fab staging deploy

Deploy Product Server:
    fab production deploy
"""
from fabric.api import run, local, require
from fabric.state import env

from lib import utils
from lib.scm import get_scm
from lib.rsync import Rsync
from conf import settings


def staging_server():
    env.server_type = 'staging'
    env.hosts = settings.STAGING_SSH_HOSTS
    env.user = settings.STAGING_SSH_USER
    env.password = settings.STAGING_SSH_PASSWORD

    utils.print_server_info(env)


def production_server():
    env.server_type = 'production'
    env.hosts = settings.PRODUCTION_SSH_HOSTS
    env.user = settings.PRODUCTION_SSH_USER
    env.password = settings.PRODUCTION_SSH_PASSWORD

    utils.print_server_info(env)


def package():
    """
    Package source code from Source Control System
    """
    scm_class = get_scm(settings.SCM_NAME)
    scm = scm_class(settings.SCM_REPOSITORY, settings.SCM_DEPLOY)
    scm.package()

    env.scm = scm


def deploy():
    """
    Upload source code to server
    """
    require('hosts', provided_by=[staging_server, production_server])
    require('scm', provided_by=[package])

    for host in env.hosts:
        rsync = Rsync(host=host, user=env.user,
            local_dir=env.scm.get_package_dir(), remote_dir='test_deploy')
        rsync.add_ssh_port(env.port)
        rsync.add_exclude_file('*.pyc')
        rsync.add_exclude_file('*.swp')

        local(rsync.get_cmd())


def restart_web_server():
    require('hosts', provided_by=[staging_server, production_server])
    run(settings.WEB_SERVER_RESTART_CMD)


def test():
    require('hosts', provided_by=[staging_server, production_server])

    run('whoami')
