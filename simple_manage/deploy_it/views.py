# coding: utf-8
import os

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.conf import settings

from deploy_it.models import DeployLog
from deploy_it.utils import run_cmd


def portal(request, template_name="deploy_it/portal.html"):
    return render_to_response(template_name,
        RequestContext(request,{
        }))


def deploy(request):
    # Running deploy command
    os.chdir(os.path.dirname(settings.PROJECT_ROOT))
    staging_deploy_cmd = ('fab staging_server package deploy '
        ' restart_web_server')
    normal_output, error_output = run_cmd(staging_deploy_cmd)

    # Save deploy command output
    deploy_log = DeployLog()
    deploy_log.normal_output = normal_output or '(not have)'
    deploy_log.error_output = error_output or '(not have)'
    deploy_log.ip_address = request.META.get('REMOTE_ADDR')
    deploy_log.save()

    # Display deploy infomation
    if error_output:
        return HttpResponseRedirect(reverse('deploy_fail'))
    else:
        return HttpResponseRedirect(reverse('deploy_sucess'))


def deploy_sucess(request, template_name="deploy_it/deploy_sucess.html"):
    return render_to_response(template_name,
        RequestContext(request,{
        }))


def deploy_fail(request, template_name="deploy_it/deploy_fail.html"):
    return render_to_response(template_name,
        RequestContext(request,{
        }))
