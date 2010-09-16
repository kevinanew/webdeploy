# coding: utf8
"""
Useage:
Deploy Staging Server:
    fab staging deploy

Deploy Product Server:
    fab production deploy
"""
from fabric.api import run, local, require, sudo, get
from fabric.state import env

from lib import scm
from lib import utils
from lib.database_backup import DatabaseBackup
from lib.rsync import Rsync
from conf import settings


def staging_server():
    env.server_type = 'staging'
    env.hosts = settings.STAGING_SSH_HOSTS
    env.user = settings.STAGING_SSH_USER
    env.password = settings.STAGING_SSH_PASSWORD

    env.database_host = settings.STAGING_DATABASE_HOST
    env.database_user = settings.STAGING_DATABASE_USER
    env.database_password = settings.STAGING_DATABASE_PASSWORD
    env.database_name = settings.STAGING_DATABASE_NAME
    env.database_port = settings.STAGING_DATABASE_PORT

    utils.print_server_info(env)


def production_server():
    env.server_type = 'production'
    env.hosts = settings.PRODUCTION_SSH_HOSTS
    env.user = settings.PRODUCTION_SSH_USER
    env.password = settings.PRODUCTION_SSH_PASSWORD

    env.database_host = settings.PRODUCTION_DATABASE_HOST 
    env.database_user = settings.PRODUCTION_DATABASE_USER 
    env.database_password = settings.PRODUCTION_DATABASE_PASSWORD
    env.database_name = settings.PRODUCTION_DATABASE_NAME
    env.database_port = settings.PRODUCTION_DATABASE_PORT 

    utils.print_server_info(env)


def package():
    """
    Package source code from Source Control System
    """
    scm_class = scm.get_scm(settings.SCM_NAME)
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


def backup_database():
    require('database_host', provided_by=[staging_server, production_server])

    database_backup = DatabaseBackup(env.database_user, env.database_password,
        env.database_name)

    utils.make_dir_if_not_exists(database_backup.get_remote_backup_dir())
    database_backup.make_local_backup_file_path()

    run(database_backup.get_backup_cmd())
    run(database_backup.get_show_remote_backup_file_cmd())
    get(database_backup.get_remote_backup_file_path(),
        database_backup.get_local_backup_file_path())
    run(database_backup.get_remove_remote_backup_file_cmd())


def restart_web_server():
    require('hosts', provided_by=[staging_server, production_server])
    sudo(settings.WEB_SERVER_RESTART_CMD)


def test():
    require('hosts', provided_by=[staging_server, production_server])

    run('whoami')

