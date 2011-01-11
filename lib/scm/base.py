# coding: utf-8
import os


class ScmBase(object):
    def __init__(self, repository_url, deploy_dir):
        self.repository_url = repository_url
        self.deploy_dir = os.path.abspath(deploy_dir)
        self.work_dir = os.path.join(self.deploy_dir, 'working')
        self.export_dir = os.path.join(self.deploy_dir, "working.export")
        self.password = None
        self._reversion = None

        if not os.path.exists(self.deploy_dir):
            os.makedirs(self.deploy_dir)

    def get_package_dir(self):
        return self.export_dir

    def set_password(self, password):
        self.password = password

    def run_cmd(self, cmd):
        print("== dir: %s ==" % os.getcwd())
        print("[localhost] run: " + cmd)
        os.system(cmd)

    def get_revision(self):
        raise NotImplementedError 

    def package(self):
        raise NotImplementedError 
