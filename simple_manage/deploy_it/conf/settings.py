# coding: utf-8


STAGING_DEPLOY_CMD = ('fab staging_server package deploy '
    ' restart_web_server')
PRODUCTION_DEPLOY_CMD = ('fab production_server package deploy '
    ' restart_web_server')
