# coding: utf-8
# 
# Don't modify this file, if you need modify anything, modify settings
# in {ROOT}/settings.py
#
from lib.settings_parser import get_settings

######################################################################
# Staging server settings
######################################################################
WEBSITE_URL = get_settings('WEBSITE_URL', '')
WEB_SERVER_RESTART_CMD = get_settings('WEB_SERVER_RESTART_CMD', '')


######################################################################
# Staging server settings
######################################################################
STAGING_SSH_HOSTS = get_settings('STAGING_SSH_HOSTS', [])
STAGING_SSH_PORT = get_settings('STAGING_SSH_PORT', 22)
STAGING_SSH_USER = get_settings('STAGING_SSH_USER', '')
STAGING_SSH_PASSWORD = get_settings('STAGING_SSH_PASSWORD', '')


######################################################################
# Production server settings
######################################################################
PRODUCTION_SSH_HOSTS = get_settings('PRODUCTION_SSH_HOSTS', [])
PRODUCTION_SSH_PORT = get_settings('PRODUCTION_SSH_PORT', 22)
PRODUCTION_SSH_USER = get_settings('PRODUCTION_SSH_USER', '')
PRODUCTION_SSH_PASSWORD = get_settings('PRODUCTION_SSH_PASSWORD', '')


######################################################################
# SCM
######################################################################
SCM_NAME = 'mercury'
SCM_REPOSITORY = get_settings('SCM_REPOSITORY', 'mercury')
SCM_DEPLOY = 'deploy_code'
