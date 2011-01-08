# coding: utf-8
import os
from git import Git


def test_package():
    current_dir = os.path.dirname(__file__)
    deploy_dir = os.path.join(current_dir,
        'test_repository/deploy_git_project/export')
   
    scm = Git(repository_url='git://github.com/kevinanew/webdeploy.git',
        deploy_dir=deploy_dir)
    scm.package()
