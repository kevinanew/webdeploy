# coding: utf-8
"""
Source control system
"""
import os
import subprocess


class Mercury(object):
    def __init__(self, repository_url, deploy_dir):
        self.repository_url = repository_url
        self.deploy_dir = os.path.abspath(deploy_dir)
        self.work_dir = os.path.join(self.deploy_dir, 'working')
        self.export_dir = os.path.join(self.deploy_dir, "working.export")

        if not os.path.exists(self.deploy_dir):
            os.makedirs(self.deploy_dir)

    def build_current_repository(self):
        if os.path.exists(self.work_dir):
            os.system('cd {work_dir} && hg pull && hg up -C'.format(
                **self.__dict__))
        else:
            self.clone()

    def clone(self):
        os.system('hg clone {repository_url} {work_dir}'.format(
            **self.__dict__))

    def export(self):
        os.system('rm {work_dir} -rf')
        os.system(
            'cd {work_dir} && hg archive -t files {export_dir}'.format(
                **self.__dict__))

    def get_revision(self):
        cmd_output= subprocess.Popen('cd {work_dir} && hg tip'.format(
            **self.__dict__), shell=True, stdout=subprocess.PIPE).stdout

        version = cmd_output.read().split(':')[1].strip()
        assert version.isdigit()
        return int(version)

    def build_revision_file(self):
        revision_file = os.path.join(self.export_dir, 'revision.txt')
        open(revision_file, 'w').write(str(self.get_revision()))

    def package(self):
        """
        Package source code for deploy
        """
        pass
        self.build_current_repository()
        self.export()
        self.build_revision_file()

