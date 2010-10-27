# coding: utf-8
import shlex
import subprocess
from cStringIO import StringIO


def run_cmd(cmd):
    process = subprocess.Popen(shlex.split(cmd), 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    normal_output, error_output = process.communicate()

    return normal_output, error_output
