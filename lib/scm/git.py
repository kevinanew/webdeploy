# coding: utf-8
import os
from lib.scm.base import ScmBase


class Git(ScmBase):
    def package(self):
        """
        Package source code for deploy
        """
        self._build_current_repository()
        self._export()

    def _build_current_repository(self):
        if os.path.exists(self.work_dir):
            self._update()
        else:
            self._clone()

    def _clone(self):
        git_clone_cmd = 'git clone {repository_url} {work_dir}'.format(
            **self.__dict__)

        self.run_cmd(git_clone_cmd)

    def _update(self):
        os.chdir(self.work_dir)

        self.run_cmd('git pull')

    def _export(self):
        self.run_cmd(('cd {work_dir} && '
            'git checkout-index -a -f --prefix={export_dir}/').format(
                **self.__dict__))
