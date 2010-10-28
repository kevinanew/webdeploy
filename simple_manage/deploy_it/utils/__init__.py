# coding: utf-8
import os
import shlex
import subprocess
from cStringIO import StringIO

from django.conf import settings as django_settings
from deploy_it.conf import settings
from deploy_it.utils import deploy_lock


def run_deploy_cmd(cmd):
    deploy_lock.set_deploying(True)

    os.chdir(os.path.dirname(django_settings.PROJECT_ROOT))
    process = subprocess.Popen(shlex.split(cmd), 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    normal_output, error_output = process.communicate()

    deploy_lock.set_deploying(False)

    return normal_output, error_output


def get_deploy_cmd(server_type):
    deploy_cmd = {}
    deploy_cmd['staging'] = settings.STAGING_DEPLOY_CMD
    deploy_cmd['production'] = settings.PRODUCTION_DEPLOY_CMD

    return deploy_cmd.get(server_type)



