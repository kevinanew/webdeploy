# coding: utf8
from django.contrib import admin

from deploy_it.models import DeployLog


admin.site.register(DeployLog, admin.ModelAdmin)
