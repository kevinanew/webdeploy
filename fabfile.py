# coding: utf8
"""
Useage:
Deploy Staging Server:
    fab staging package deploy django_nginx_restart

Deploy Product Server:
    fab production package deploy django_nginx_restart
"""
from fabric.api import run, local
from fabric.state import env

from lib import utils
from conf import settings


def staging_server():
    env.server_type = 'staging'
    env.hosts = settings.STAGING_SSH_HOSTS
    env.port = settings.STAGING_SSH_PORT
    env.user = settings.STAGING_SSH_USER
    env.password = settings.STAGING_SSH_PASSWORD

    utils.print_server_info(env)


def production_server():
    env.server_type = 'production'
    env.hosts = settings.PRODUCTION_SSH_HOSTS
    env.port = settings.PRODUCTION_SSH_PORT
    env.user = settings.PRODUCTION_SSH_USER
    env.password = settings.PRODUCTION_SSH_PASSWORD

    utils.print_server_info(env)


def test():
    run('ls -al')
    run('whoami')
