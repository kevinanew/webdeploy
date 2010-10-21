# coding: utf8
from django.conf.urls.defaults import *


urlpatterns = patterns('deploy_it.views',
    url(r'^$', 'portal', name="portal"),
    url(r'^deploy/$', 'deploy', name="deploy"),
)
