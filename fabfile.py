# coding: utf8
"""
Useage:
Deploy Staging Server:
    fab staging deploy

Deploy Product Server:
    fab production deploy
"""
import os
from fabric.api import run, local, require, sudo, get, put
from fabric.state import env

from lib import utils
from lib.rsync import Rsync, RsyncDir
import settings


def staging_server():
    env.server_type = 'staging'
    env.hosts = settings.STAGING_SSH_HOSTS
    env.user = settings.STAGING_SSH_USER
    env.password = settings.STAGING_SSH_PASSWORD
    env.ssh_key_file = settings.STAGING_SSH_KEY

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
    env.ssh_key_file = settings.PRODUCTION_SSH_KEY

    env.database_host = settings.PRODUCTION_DATABASE_HOST 
    env.database_user = settings.PRODUCTION_DATABASE_USER 
    env.database_password = settings.PRODUCTION_DATABASE_PASSWORD
    env.database_name = settings.PRODUCTION_DATABASE_NAME
    env.database_port = settings.PRODUCTION_DATABASE_PORT 

    utils.print_server_info(env)


def _scm_package():
    from lib import scm
    scm_class = scm.get_scm_class(settings.SCM_NAME)
    _scm = scm_class(settings.SCM_REPOSITORY_URL, settings.SCM_DEPLOY)
    _scm.set_password(settings.SCM_PASSWORD)
    _scm.package()
    env.scm = _scm


def _compress_templates():
    def compress_django_templates(template_dir):
        from lib.django_template_compress import DjangoTemplateCompressor

        for root, dirs, files in os.walk(template_dir):
            for file_path in files:
                template_file_path = os.path.join(root, file_path)
                compressor = DjangoTemplateCompressor(template_file_path)
                compressor.process()
                compressor.save_template_file()

    for _template_dir in settings.PROJECT_TEMPLATE_DIR_LIST:
        template_dir = os.path.join(env.scm.get_package_dir(), _template_dir)
        compress_django_templates(template_dir)


def _compile_templates():
    def compile_django_templates(template_dir):
        from lib.django_template_compiler import DjangoTemplateCompiler
        for root, dirs, files in os.walk(template_dir):
            for file_path in files:
                template_file_path = os.path.join(root, file_path)
                compiler = DjangoTemplateCompiler(template_file_path)
                compiler.set_value(code_version=env.scm.get_revision())
                compiler.process()
                compiler.save_template_file()

    for _template_dir in settings.PROJECT_TEMPLATE_DIR_LIST:
        template_dir = os.path.join(env.scm.get_package_dir(), _template_dir)
        compile_django_templates(template_dir)


def _scm_package_cmd():
    os.chdir(os.path.dirname(__file__))
    if env.server_type == 'staging':
        cmd_list = settings.SCM_PACKAGE_CMD_LIST_FOR_STAGING
    elif env.server_type == 'production':
        cmd_list = settings.SCM_PACKAGE_CMD_LIST_FOR_PRODUCT
    else:
        raise

    for package_cmd in cmd_list:
        local(package_cmd)


def package():
    """
    Package source code from Source Control System
    """
    _scm_package()
    _compress_templates()
    # _compile_templates must after compress_templates, 
    # becuase _compile_templates will generate html comment that will be 
    # clean by _compress_templates
    _compile_templates()
    _scm_package_cmd()


def _upload_code():
    for host in env.hosts:
        rsync = Rsync(host=host, user=env.user,
            local_dir=env.scm.get_package_dir(),
            remote_dir=settings.PROJECT_REMOTE_DIR)

        rsync.set_password(env.password)
        rsync.set_ssh_key_file(env.ssh_key_file)
        rsync.add_ssh_port(env.port)
        rsync.add_exclude_file('*.pyc')
        rsync.add_exclude_file('*.swp')
        rsync.run_cmd()


def _sync_project_files():
    """
    sync project files
    """
    require('hosts', provided_by=[staging_server, production_server])
    for sync_item in settings.PROJECT_SYNC_DIR:
        rsync_dir = RsyncDir(sync_item['from'], sync_item['to'])
        run(rsync_dir.get_cmd())


def deploy():
    """
    Upload source code to server
    """
    require('hosts', provided_by=[staging_server, production_server])
    require('scm', provided_by=[package])

    _upload_code()
    _sync_project_files()


def _run_remote_deploy_cmd():
    if hasattr(settings, 'PROJECT_REMOTE_DEPLOY_CMD') and \
            settings.PROJECT_REMOTE_DEPLOY_CMD:
        run(settings.PROJECT_REMOTE_DEPLOY_CMD)


def backup_database():
    require('database_host', provided_by=[staging_server, production_server])

    from lib.database_backup import DatabaseBackup
    # FIXME database_host is not used ???
    database_backup = DatabaseBackup(env.database_user, env.database_password,
        env.database_name)

    utils.make_dir_if_not_exists(database_backup.get_remote_backup_dir())
    database_backup.make_local_backup_file_path()

    run(database_backup.get_backup_cmd())
    run(database_backup.get_show_remote_backup_file_cmd())
    get(database_backup.get_remote_backup_file_path(),
        database_backup.get_local_backup_file_path())
    run(database_backup.get_remove_remote_backup_file_cmd())


def restore_database():
    require('database_host', provided_by=[staging_server])

    from lib.database_restore import DatabaseRestore
    database_restore = DatabaseRestore(env.database_user,
        env.database_password, env.database_name)

    utils.make_dir_if_not_exists(database_restore.get_remote_restore_dir())

    database_restore.list_backup_file()
    database_restore.set_restore_file()
    put(database_restore.get_local_restore_file(),
        database_restore.get_remote_restore_file())

    run(database_restore.get_restore_database_cmd())


def restart_web_server():
    require('hosts', provided_by=[staging_server, production_server])
    assert settings.WEB_SERVER_RESTART_CMD
    print("Restart web server: " + settings.WEB_SERVER_RESTART_CMD)
    sudo(settings.WEB_SERVER_RESTART_CMD)


def test():
    require('hosts', provided_by=[staging_server, production_server])

    run('whoami')

