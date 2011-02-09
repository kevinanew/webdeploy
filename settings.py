# coding: utf-8
# 
# !!! Don't modify this file !!!
#
# if you need modify anything, modify settings
# in {ROOT}/project_settings.py
#

######################################################################
# SCM
######################################################################
SCM_NAME = 'mercury'
SCM_REPOSITORY_URL = ''
SCM_DEPLOY = 'deploy_code'
SCM_PASSWORD = ''
SCM_PACKAGE_CMD_LIST_FOR_STAGING = ()
SCM_PACKAGE_CMD_LIST_FOR_PRODUCT = ()

######################################################################
# Database
######################################################################
REMOTE_DATABASE_BACKUP_DIR = '~/database_backup'
REMOTE_DATABASE_RESTORE_DIR = '~/database_restore'
LOCAL_DATABASE_BACKUP_DIR = '~/webdeploy_backup/database'

######################################################################
# Project dir
######################################################################
PROJECT_REMOTE_DIR = ''
PROJECT_TEMPLATE_DIR_LIST = ()
PROJECT_SYNC_DIR = (
)

######################################################################
# Web server
######################################################################
WEB_SERVER_RESTART_CMD = ''
IS_WEB_SERVER_RESTART_NEED_SUDO = True

######################################################################
# Staging server settings
######################################################################
STAGING_WEBSITE_URL = ''
STAGING_SSH_HOSTS = []
STAGING_SSH_PORT = 22
STAGING_SSH_USER = ''
STAGING_SSH_PASSWORD = ''
STAGING_SSH_KEY = ''

STAGING_DATABASE_HOST = ''
STAGING_DATABASE_USER = ''
STAGING_DATABASE_PASSWORD = ''
STAGING_DATABASE_NAME = ''
STAGING_DATABASE_PORT = ''


######################################################################
# Production server settings
######################################################################
PRODUCTION_WEBSITE_URL = ''
PRODUCTION_SSH_HOSTS = []
PRODUCTION_SSH_PORT = 22
PRODUCTION_SSH_USER = ''
PRODUCTION_SSH_PASSWORD = ''
PRODUCTION_SSH_KEY = ''

PRODUCTION_DATABASE_HOST = ''
PRODUCTION_DATABASE_USER = ''
PRODUCTION_DATABASE_PASSWORD = ''
PRODUCTION_DATABASE_NAME = ''
PRODUCTION_DATABASE_PORT = ''


######################################################################
# Project settings
######################################################################
try:
    from project_settings import *
except ImportError:
    pass

