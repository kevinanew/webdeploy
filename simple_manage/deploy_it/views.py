# coding: utf-8
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from deploy_it.models import DeployLog, DeployInfo
from deploy_it.utils import run_deploy_cmd, get_deploy_cmd, deploy_lock


def portal(request, template_name="deploy_it/portal.html"):
    return render_to_response(template_name,
        RequestContext(request,{
        }))


def deploy(request, server_type):
    if deploy_lock.is_deploying():
        return render_to_response('deploy_it/deploying.html',
            RequestContext(request,{
            }))

    # Running deploy command
    deploy_cmd = get_deploy_cmd(server_type)
    normal_output, error_output = run_deploy_cmd(deploy_cmd)

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


def deploy_force(request):
    deploy_lock.set_deploying(False)
    return HttpResponseRedirect(reverse('portal'))


