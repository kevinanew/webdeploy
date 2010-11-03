# coding: utf-8
"""
Source control system
"""
import os
import subprocess
from lib import pexpect 


class Mercury(object):
    def __init__(self, repository_url, deploy_dir):
        self.repository_url = repository_url
        self.deploy_dir = os.path.abspath(deploy_dir)
        self.work_dir = os.path.join(self.deploy_dir, 'working')
        self.export_dir = os.path.join(self.deploy_dir, "working.export")
        self.password = None
        self._reversion = None

        if not os.path.exists(self.deploy_dir):
            os.makedirs(self.deploy_dir)

    def set_password(self, password):
        self.password = password

    def package(self):
        """
        Package source code for deploy
        """
        self._build_current_repository()
        self._export()
        self._build_revision_file()

    def get_package_dir(self):
        return self.export_dir

    def _build_current_repository(self):
        if os.path.exists(self.work_dir):
            self._update()
        else:
            self._clone()

    def _login_use_password(self, hg_cmd):
        hg_process = pexpect.spawn(hg_cmd)
        hg_process.expect('.*password:.*')
        hg_process.sendline(self.password)
        hg_process.expect(pexpect.EOF)

    def _clone(self):
        hg_clone_cmd = 'hg clone {repository_url} {work_dir}'.format(
            **self.__dict__)

        if self.password:
            self._login_use_password(hg_clone_cmd)
        else:
            self.run_cmd(hg_clone_cmd)

    def _update(self):
        os.chdir(self.work_dir)

        if self.password:
            self._login_use_password('hg pull')
        else:
            self.run_cmd('hg pull')

        self.run_cmd('hg up -C')

    def _export(self):
        self.run_cmd('rm {work_dir} -rf')
        self.run_cmd(
            'cd {work_dir} && hg archive -t files {export_dir}'.format(
                **self.__dict__))

    def get_revision(self):
        if self._reversion is None:
            cmd_output= subprocess.Popen('cd {work_dir} && hg tip'.format(
                **self.__dict__), shell=True, stdout=subprocess.PIPE).stdout
    
            reversion = cmd_output.read().split(':')[1].strip()
            assert reversion.isdigit()
            self._reversion = int(reversion)

        return self._reversion

    def _build_revision_file(self):
        print("make revision.txt")
        revision_file = os.path.join(self.export_dir, 'revision.txt')
        open(revision_file, 'w').write(str(self.get_revision()))

    def run_cmd(self, cmd):
        print("== dir: %s ==" % os.getcwd())
        print("[localhost] run: " + cmd)
        os.system(cmd)
