# coding: utf8
from django.conf.urls.defaults import *


urlpatterns = patterns('deploy_it.views',
    url(r'^$', 'portal', name="portal"),

    url(r'^deploy/staging/$', 'deploy', {'server_type': 'staging'},
        name="deploy_staging"),
    url(r'^deploy/production/$', 'deploy', {'server_type': 'production'},
        name="deploy_production"),

    url(r'^deploy_sucess/$', 'deploy_sucess', name="deploy_sucess"),
    url(r'^deploy_fail/$', 'deploy_fail', name="deploy_fail"),
    url(r'^deploy_force/$', 'deploy_force', name="deploy_force"),
)
