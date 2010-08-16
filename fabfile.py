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

def package():
    scm_class = get_scm(settings.SCM_NAME)
    scm = scm_class(settings.SCM_REPOSITORY, 'scm/code_export')
    scm.package()

def test():
    require('hosts', provided_by=[staging_server, production_server])

    run('whoami')
