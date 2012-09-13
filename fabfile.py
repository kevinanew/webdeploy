# coding: utf8
"""
Useage:
    fab help
"""
import os
import shutil
from fabric.api import run, local, require, sudo, get, put
from fabric.state import env
from fabric.contrib import files

from lib import utils, rsync
import settings


def help():
    help_doc = settings.__doc__.strip()
    if help_doc:
        print help_doc
    else:
        print "Write down help doc before you can read it"

def default_deploy():
    """
    print a default deploy command
    """
    print "deploy command:", settings.DEFAULT_DEPLOY_CMD

######################################################################
# Server settings
######################################################################

def staging_server():
    """
    deployment at staging server
    """
    env.server_type = 'staging'
    env.hosts = settings.STAGING_SSH_HOSTS
    env.user = settings.STAGING_SSH_USER
    env.password = settings.STAGING_SSH_PASSWORD

    ssh_key_path = os.path.expanduser(settings.STAGING_SSH_KEY)
    if ssh_key_path:
        env.key_filename = [ssh_key_path]
    # this will use by some tool like rsync
    # FIXME: how it work if every server's ssh key is different
    env.ssh_key_file = ssh_key_path

    ssh_public_key_path = os.path.expanduser(settings.STAGING_SSH_PUBLIC_KEY)
    if ssh_public_key_path:
        env.public_key_filename = ssh_public_key_path

    env.database_host = settings.STAGING_DATABASE_HOST
    env.database_user = settings.STAGING_DATABASE_USER
    env.database_password = settings.STAGING_DATABASE_PASSWORD
    env.database_name = settings.STAGING_DATABASE_NAME
    env.database_port = settings.STAGING_DATABASE_PORT

    utils.print_server_info(env)


def production_server():
    """
    deployment at production server
    """
    env.server_type = 'production'
    env.hosts = settings.PRODUCTION_SSH_HOSTS
    env.user = settings.PRODUCTION_SSH_USER
    env.password = settings.PRODUCTION_SSH_PASSWORD

    ssh_key_path = os.path.expanduser(settings.PRODUCTION_SSH_KEY)
    if ssh_key_path:
        env.key_filename = [ssh_key_path]
    # this will use by some tool like rsync
    # FIXME: how it work if every server's ssh key is different
    env.ssh_key_file = ssh_key_path

    ssh_public_key_path = os.path.expanduser(settings.PRODUCTION_SSH_PUBLIC_KEY)
    if ssh_public_key_path:
        env.public_key_filename = ssh_public_key_path

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

    branch = getattr(settings, 'SCM_BRANCH', None)
    _scm.set_branch(branch)

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
    install all modules use pip at localhost
    """
    local("""cat << EOF > pip_requirements.txt
%s
EOF""" % settings.PIP_REQUIREMENTS.strip())
    local('pip install -r pip_requirements.txt')
    local('rm pip_requirements.txt')

def setup_virtualenv():
    """
    build virtualenv and install moduels use pip
    """
    require('hosts', provided_by=[staging_server, production_server])
    python_path = getattr(settings, 'PYTHON_PATH', '/usr/bin/python2.7')

    run(('test -d {virtualenv_dir} && echo "virtualenv existed" '
        '|| virtualenv -p {python_path} --no-site-packages {virtualenv_dir}'
        ).format(python_path=python_path,
            virtualenv_dir=settings.PROJECT_REMOTE_VIRTUALENV_DIR))
    _pip_install_virtualenv()


def remove_virtualenv():
    """
    delete virtualenv, then you can build a new virtualenv use setup_virtualenv
    command
    """
    require('hosts', provided_by=[staging_server, production_server])
    run('rm -rf %s' % settings.PROJECT_REMOTE_VIRTUALENV_DIR)


def backup_code():
    assert settings.PROJECT_REMOTE_SOURCE_CODE_DIR
    for host in env.hosts:
        # delete old backup
        run('rm -rf {code_dir}.bak'.format(
            code_dir=settings.PROJECT_REMOTE_SOURCE_CODE_DIR))

        # make new backup
        run('test -d {code_dir} && cp -r {code_dir} {code_dir}.bak ' \
            '|| echo "skip backup"'.format(
            code_dir=settings.PROJECT_REMOTE_SOURCE_CODE_DIR))


def _upload_code_in_tmp_dir():
    assert settings.PROJECT_REMOTE_SOURCE_CODE_DIR
    uploading_code_dir = '%s.uploading' % settings.PROJECT_REMOTE_SOURCE_CODE_DIR
    for host in env.hosts:
        run('test -d {code_dir} || mkdir -p {code_dir}'.format(
            code_dir=uploading_code_dir))
        _rsync = rsync.Rsync(host=host, user=env.user,
            local_dir=env.scm.get_package_dir(),
            remote_dir=uploading_code_dir)
        _rsync.timeout = 240
        _rsync.max_try_time = 10
        _rsync.set_password(env.password)
        _rsync.set_ssh_key_file(env.ssh_key_file)
        _rsync.add_exclude_file('*.pyc')
        _rsync.add_exclude_file('*.swp')
        _rsync.run_cmd()


def _sync_uploading_code_dir():
    assert settings.PROJECT_REMOTE_SOURCE_CODE_DIR
    uploading_code_dir = '%s.uploading' % settings.PROJECT_REMOTE_SOURCE_CODE_DIR
    rsync_cmd = 'rsync -rlvxc "%s/" "%s/"' % (uploading_code_dir, settings.PROJECT_REMOTE_SOURCE_CODE_DIR)
    print "cmd:,", rsync_cmd
    run(rsync_cmd)


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

    _upload_code_in_tmp_dir()
    backup_code()
    _sync_uploading_code_dir()

    _setup_crontab()
    _run_remote_deploy_cmd()
    _sync_project_files()


######################################################################
# Database management
######################################################################

def backup_database():
    """
    backup your database
    """
    require('database_host', provided_by=[staging_server, production_server])

    from lib.database_backup import DatabaseBackup
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
    """
    restore a database backup file, please use backup_database command first
    """
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
    """
    restart web server, you must add restart command in project_settings.py
    """
    require('hosts', provided_by=[staging_server, production_server])
    assert settings.WEB_SERVER_RESTART_CMD_LIST
    for server_restart_cmd, is_need_sudo in settings.WEB_SERVER_RESTART_CMD_LIST:
        print "Restart web server:", server_restart_cmd
        if is_need_sudo:
            sudo(server_restart_cmd)
        else:
            run(server_restart_cmd)


######################################################################
# Server setup
######################################################################
def _setup_dns():
    if settings.DNS_SETUP_CMD:
        local(settings.DNS_SETUP_CMD)

def _setup_mysql():
    mysql_cmd_template = 'mysql -u{username} -p{password} -e "%s"'.format(
        username=settings.MYSQL_ROOT_USER,
        password=settings.MYSQL_ROOT_PASSWORD)
    create_db_sql = ('CREATE DATABASE IF NOT EXISTS {dbname} CHARACTER SET utf8'
        ' COLLATE utf8_general_ci;').format(dbname=settings.MYSQL_DBNAME)
    run(mysql_cmd_template % create_db_sql)

    user_add_sql = ("grant ALL PRIVILEGES on {dbname}.* to "
        "'{username}'@'localhost' "
        "IDENTIFIED BY '{password}';").format(dbname=settings.MYSQL_DBNAME,
            username=settings.MYSQL_USER,
            password=settings.MYSQL_USER_PASSWORD)
    run(mysql_cmd_template % user_add_sql)

    user_add_sql = ("grant ALL PRIVILEGES on {dbname}.* to "
        "'{username}'@'127.0.0.1' "
        "IDENTIFIED BY '{password}';").format(dbname=settings.MYSQL_DBNAME,
            username=settings.MYSQL_USER,
            password=settings.MYSQL_USER_PASSWORD)
    run(mysql_cmd_template % user_add_sql)

def setup_project():
    """
    add DNS, web server config, mysql database, mysql user and etc
    """
    # TODO: setup_project is not used, please move code to setup_server
    require('hosts', provided_by=[staging_server, production_server])

    _setup_dns()
    _setup_mysql()
    #_setup_nginx()


def _setup_server_config():
    # TODO: set /etc config files
    def get_local_config_files():
        local_etc_dir = os.path.join(settings.LOCAL_SERVER_CONFIG_DIR, 'etc')
        for _root, _dirs, _files in os.walk(local_etc_dir):
            for _file in _files:
                yield os.path.join(_root, _file)

    is_update = False
    for local_config_file in get_local_config_files():
        remote_config_file = local_config_file.replace(
            settings.LOCAL_SERVER_CONFIG_DIR, '')

        if not utils.is_same_content(local_config_file, remote_config_file):
            is_update = True
            utils.backup(remote_config_file, use_sudo=True)
            utils.upload(local_config_file, remote_config_file,
                use_sudo=True, mode=0644)
            sudo('chown %s %s' % (env.user, remote_config_file))

    if is_update:
        print 'Config files are updated'
        print 'IMPORT:'
        print ' run "/etc/init.d/nginx reload" only if fastcgi port is static'
        print ' if not, please re-deployment project then restart server'

def _setup_server_cmd():
    for cmd, is_sudo in settings.SERVER_CONFIG_CMD:
        if is_sudo:
            sudo(cmd)
        else:
            run(cmd)

def setup_server():
    """
    deployment nginx, memcached and other server software's config
    """
    _setup_server_cmd()
    _setup_server_config()

def upload_ssh_key():
    run('test -d ~/.ssh || mkdir ~/.ssh')
    run('test -e ~/.ssh/authorized_keys || touch ~/.ssh/authorized_keys')
    run('chmod 600 ~/.ssh/authorized_keys')
    
    ssh_public_key_content = open(env.public_key_filename, 'rb').read().strip()
    authorized_keys_content = run('cat ~/.ssh/authorized_keys')
    if ssh_public_key_content in authorized_keys_content:
        print "SSH public key already added"
    else:
        files.append('~/.ssh/authorized_keys', ssh_public_key_content)
        print "SSH public key added"

######################################################################
# Misc 
######################################################################
def init():
    """
    delete source code files in local pc
    """
    if os.path.exists(settings.SCM_DEPLOY):
        print "remove", settings.SCM_DEPLOY
        shutil.rmtree(settings.SCM_DEPLOY)

def help():
    print settings.HELP_TEXT

######################################################################
# Testing
######################################################################

def test():
    require('hosts', provided_by=[staging_server, production_server])

    run('whoami')
