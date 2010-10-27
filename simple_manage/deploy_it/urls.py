# coding: utf8
from django.conf.urls.defaults import *


urlpatterns = patterns('deploy_it.views',
    url(r'^$', 'portal', name="portal"),
    url(r'^deploy/$', 'deploy', name="deploy"),
    url(r'^deploy_sucess/$', 'deploy_sucess', name="deploy_sucess"),
    url(r'^deploy_fail/$', 'deploy_fail', name="deploy_fail"),
)
