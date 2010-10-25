# coding: utf-8
import os

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.conf import settings


def portal(request, template_name="deploy_it/portal.html"):
    return render_to_response(template_name,
        RequestContext(request,{
        }))


def deploy(request, template_name="deploy_it/deploy.html"):
    os.chdir(os.path.dirname(settings.PROJECT_ROOT))

    staging_deploy_cmd = ('fab staging_server package deploy '
        ' restart_web_server')
    os.system(staging_deploy_cmd)

    return render_to_response(template_name,
        RequestContext(request,{
        }))
