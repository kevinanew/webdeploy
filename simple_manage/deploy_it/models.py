# coding: utf-8
from django.db import models


class DeployLog(models.Model):
    id = models.AutoField(primary_key=True)
    normal_output = models.TextField()
    error_output = models.TextField()
    ip_address = models.IPAddressField()
    add = models.DateTimeField(auto_now_add=True, auto_now=True)

    def __unicode__(self):
        return "%s at %s" % (self.id, self.add)


class DeployInfo(models.Model):
    name = models.CharField(primary_key=True, max_length=128)
    content = models.CharField(max_length=128)

    def __unicode__(self):
        return "%s : %s" % (self.name, self.content)


