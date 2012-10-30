# coding: utf-8
import os
import subprocess

from lib.scm.base import ScmBase


class Git(ScmBase):
    def get_revision(self):
        if self._reversion is None:
            cmd_output= subprocess.Popen('cd {work_dir} && git log -1'.format(
                **self.__dict__), shell=True, stdout=subprocess.PIPE).stdout
    
            self._reversion = cmd_output.read().splitlines()[0].split(' ')[1]

        return self._reversion

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
        if self.branch:
            git_clone_cmd = 'git clone' + \
                ' -b {branch} {repository_url} {work_dir}'.format(
                    **self.__dict__)
        else:
            git_clone_cmd = 'git clone {repository_url} {work_dir}'.format(
                **self.__dict__)

        self.run_cmd(git_clone_cmd)
        self._update_submodules()

    def _update(self):
        os.chdir(self.work_dir)

        self.run_cmd('git pull')
        self._update_submodules()

    def _update_submodules(self):
        update_all_submodels_cmd = ('cd {work_dir} && '
            'git submodule init && git submodule update && '
            'git submodule foreach git pull -q origin master').format(
                **self.__dict__)

        self.run_cmd(update_all_submodels_cmd)

    def _export(self):
        export_cmd = ('rsync -av --delete {work_dir}/ {export_dir} --exclude=".git"'
            ' > /dev/null').format(**self.__dict__)
        self.run_cmd(export_cmd)

