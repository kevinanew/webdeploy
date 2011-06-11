# coding: utf8
"""
Useage:
Deploy Staging Server:
    fab staging_server package deploy restart_web_server

Deploy Product Server:
    fab production_server package deploy restart_web_server
"""
import os
import shutil
from fabric.api import run, local, require, sudo, get, put
from fabric.state import env

from lib import utils, rsync
import settings


def init():
    """
    delete source code files in local pc
    """
    if os.path.exists(settings.SCM_DEPLOY):
        print "remove", settings.SCM_DEPLOY
        shutil.rmtree(settings.SCM_DEPLOY)


######################################################################
# Server settings
######################################################################

def staging_server():
    env.server_type = 'staging'
    env.hosts = settings.STAGING_SSH_HOSTS
    env.user = settings.STAGING_SSH_USER
    env.password = settings.STAGING_SSH_PASSWORD

    ssh_key_path = os.path.expanduser(settings.STAGING_SSH_KEY)
    if ssh_key_path:
        env.key_filename = [ssh_key_path]
    # this will use by some tool like rsync
    env.ssh_key_file = ssh_key_path

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

    ssh_key_path = os.path.expanduser(settings.PRODUCTION_SSH_KEY)
    if ssh_key_path:
        env.key_filename = [ssh_key_path]
    # this will use by some tool like rsync
    env.ssh_key_file = ssh_key_path

    env.database_host = settings.PRODUCTION_DATABASE_HOST 
    env.database_user = settings.PRODUCTION_DATABASE_USER 
    env.database_password = settings.PRODUCTION_DATABASE_PASSWORD
    env.database_name = settings.PRODUCTION_DATABASE_NAME
    env.database_port = settings.PRODUCTION_DATABASE_PORT 

    utils.print_server_info(env)


######################################################################
# Package Source code
######################################################################

def _scm_package():
    from lib import scm
    scm_class = scm.get_scm_class(settings.SCM_NAME)
    _scm = scm_class(settings.SCM_REPOSITORY_URL, settings.SCM_DEPLOY)
    _scm.set_password(settings.SCM_PASSWORD)
    _scm.package()
    env.scm = _scm


def _compress_templates():
    from lib.django_template_compress import DjangoTemplateCompressor

    for _template_dir in settings.PROJECT_TEMPLATE_DIR_LIST:
        template_dir = os.path.join(env.scm.get_package_dir(), _template_dir)
        print "compress templates:", template_dir
        for template_path in utils.get_files_in_dir(template_dir):
            compressor = DjangoTemplateCompressor(template_path)
            compressor.process()
            compressor.save_template_file()


def _compile_templates():
    from lib.django_template_compiler import DjangoTemplateCompiler

    for _template_dir in settings.PROJECT_TEMPLATE_DIR_LIST:
        template_dir = os.path.join(env.scm.get_package_dir(), _template_dir)
        print "compile templates:", template_dir
        for template_path in utils.get_files_in_dir(template_dir):
            compiler = DjangoTemplateCompiler(template_path)
            compiler.set_value(code_version=env.scm.get_revision())
            compiler.process()
            compiler.save_template_file()


def _scm_package_cmd():
    os.chdir(os.path.dirname(__file__))

    server_type = getattr(env, 'server_type', '')
    if server_type == 'staging':
        cmd_list = settings.SCM_PACKAGE_CMD_LIST_FOR_STAGING
    elif server_type == 'production':
        cmd_list = settings.SCM_PACKAGE_CMD_LIST_FOR_PRODUCT
    else:
        cmd_list = ()

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


######################################################################
# Deploy project
######################################################################

def _pip_install_virtualenv():
    """
    install python modules in virtualenv use pip
    """
    if not settings.PIP_REQUIREMENTS:
        return

    run("""cat << EOF > pip_requirements.txt
%s
EOF""" % settings.PIP_REQUIREMENTS.strip())
    run('source %s/bin/activate && pip install -r pip_requirements.txt' % \
        settings.PROJECT_REMOTE_VIRTUALENV_DIR)
    run('rm pip_requirements.txt')

def pip_install():
    """
    pip install at localhost
    """
    local("""cat << EOF > pip_requirements.txt
%s
EOF""" % settings.PIP_REQUIREMENTS.strip())
    local('pip install -r pip_requirements.txt')
    local('rm pip_requirements.txt')

def setup_virtualenv():
    require('hosts', provided_by=[staging_server, production_server])

    run(('test -d {virtualenv_dir} && echo "virtualenv existed" '
        '|| virtualenv --no-site-packages {virtualenv_dir}').format(
            virtualenv_dir=settings.PROJECT_REMOTE_VIRTUALENV_DIR))
    _pip_install_virtualenv()


def remove_virtualenv():
    require('hosts', provided_by=[staging_server, production_server])
    run('rm -rf %s' % settings.PROJECT_REMOTE_VIRTUALENV_DIR)


def _upload_code():
    for host in env.hosts:
        run('test -d {code_dir} || mkdir -p {code_dir}'.format(
            code_dir=settings.PROJECT_REMOTE_SOURCE_CODE_DIR))
        _rsync = rsync.Rsync(host=host, user=env.user,
            local_dir=env.scm.get_package_dir(),
            remote_dir=settings.PROJECT_REMOTE_SOURCE_CODE_DIR)

        _rsync.set_password(env.password)
        _rsync.set_ssh_key_file(env.ssh_key_file)
        _rsync.add_ssh_port(env.port)
        _rsync.add_exclude_file('*.pyc')
        _rsync.add_exclude_file('*.swp')
        _rsync.run_cmd()


def _sync_project_files():
    """
    sync project files
    """
    require('hosts', provided_by=[staging_server, production_server])
    for sync_item in settings.PROJECT_SYNC_DIR:
        run('test -d %s || mkdir -p %s' % (sync_item['to'], sync_item['to']))
        rsync_dir = rsync.RsyncDir(sync_item['from'], sync_item['to'])
        if sync_item.get('exclude', None): 
            rsync_dir.add_exclude_dir(sync_item.get('exclude'))
        run(rsync_dir.get_cmd())


def _run_remote_deploy_cmd():
    deploy_cmd_list = getattr(settings, 'PROJECT_DEPLOY_CMD_LIST', [])
    for deploy_cmd in deploy_cmd_list:
        run(deploy_cmd)

def _setup_crontab():
    if settings.PROJECT_CRON_FILE:
        run('test -f {cron_file} && crontab {cron_file} || echo "skip crontab"'.format(
            cron_file=settings.PROJECT_CRON_FILE))

def deploy():
    """
    Upload source code to server
    """
    require('hosts', provided_by=[staging_server, production_server])
    require('scm', provided_by=[package])

    _upload_code()
    _sync_project_files()
    _setup_crontab()
    _run_remote_deploy_cmd()


######################################################################
# Database management
######################################################################

def backup_database():
    require('database_host', provided_by=[staging_server, production_server])

    from lib.database_backup import DatabaseBackup
    # FIXME database_host is not used ???
    database_backup = DatabaseBackup(env.database_user, env.database_password,
        env.database_name, env.database_host)

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
        env.database_password, env.database_name, env.database_host)

    utils.make_dir_if_not_exists(database_restore.get_remote_restore_dir())

    database_restore.list_backup_file()
    database_restore.set_restore_file()
    put(database_restore.get_local_restore_file(),
        database_restore.get_remote_restore_file())

    run(database_restore.get_restore_database_cmd())


######################################################################
# Webserver management
######################################################################

def restart_web_server():
    require('hosts', provided_by=[staging_server, production_server])
    assert settings.WEB_SERVER_RESTART_CMD_LIST
    for server_restart_cmd in settings.WEB_SERVER_RESTART_CMD_LIST:
        print "Restart web server:", server_restart_cmd
        if settings.IS_WEB_SERVER_RESTART_NEED_SUDO:
            sudo(server_restart_cmd)
        else:
            run(server_restart_cmd)


######################################################################
# Testing
######################################################################

def test():
    require('hosts', provided_by=[staging_server, production_server])

    run('whoami')

