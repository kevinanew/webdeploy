# coding: utf-8
import lib.config_parser import get_config


######################################################################
# Staging server config
######################################################################
STAGING_SSH_HOSTS = get_config('STAGING_SSH_HOSTS', [])
STAGING_SSH_PORT = get_config('STAGING_SSH_PORT', 22)
STAGING_SSH_USER = get_config('STAGING_SSH_USER')
STAGING_SSH_PASSWORD = get_config('STAGING_SSH_PASSWORD', '')


######################################################################
# Production server config
######################################################################
PRODUCTION_SSH_HOSTS = get_config('PRODUCTION_SSH_HOSTS', [])
PRODUCTION_SSH_PORT = get_config('PRODUCTION_SSH_PORT', 22)
PRODUCTION_SSH_USER = get_config('PRODUCTION_SSH_USER')
PRODUCTION_SSH_PASSWORD = get_config('PRODUCTION_SSH_PASSWORD', '')

