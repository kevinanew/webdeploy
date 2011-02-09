# coding: utf-8
"""
Source control system
"""
import os
import subprocess
import urllib

from lib.scm.base import ScmBase


class Mercury(ScmBase):
    def get_revision(self):
        if self._reversion is None:
            cmd_output= subprocess.Popen('cd {work_dir} && hg tip'.format(
                **self.__dict__), shell=True, stdout=subprocess.PIPE).stdout
    
            reversion = cmd_output.read().split(':')[1].strip()
            assert reversion.isdigit()
            self._reversion = int(reversion)

        return self._reversion

    def package(self):
        """
        Package source code for deploy
        """
        self._build_current_repository()
        self._export()
        self._build_revision_file()

    def _build_current_repository(self):
        if os.path.exists(self.work_dir):
            self._update()
        else:
            self._clone()

    def _clone(self):
        self.repository_url = self.repository_url.replace(
            '@', ':%s@' % urllib.quote(self.password))
        hg_clone_cmd = 'hg clone {repository_url} {work_dir}'.format(
            **self.__dict__)

        # use quote because if "@" in password that will break this command
        self.run_cmd(hg_clone_cmd)

    def _update(self):
        os.chdir(self.work_dir)

        self.run_cmd('hg pull')
        self.run_cmd('hg up -C')

    def _export(self):
        self.run_cmd(
            'cd {work_dir} && hg archive -t files {export_dir}'.format(
                **self.__dict__))

    def _build_revision_file(self):
        print("make revision.txt")
        revision_file = os.path.join(self.export_dir, 'revision.txt')
        open(revision_file, 'w').write(str(self.get_revision()))
