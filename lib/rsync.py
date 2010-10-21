# coding: utf-8
import os
from lib import pexpect


class Rsync(object):
    def __init__(self, host, user, password, local_dir, remote_dir):
        self.host = host
        self.user = user
        self.password = password
        self.local_dir = os.path.normpath(local_dir)
        self.remote_dir = os.path.normpath(remote_dir)

        self.ssh_cmd = ['ssh']
        self.exclude_file_list = []

    def add_ssh_key(self, ssh_key_file):
        self.ssh_cmd.append('-i %s' % ssh_key_file)

    def add_ssh_port(self, ssh_port):
        if isinstance(ssh_port, basestring) and ssh_port.isdigit():
            ssh_port = int(ssh_port)

        assert isinstance(ssh_port, int)
        assert 0 < ssh_port <= 255*255
        self.ssh_cmd.append('-p %s' % ssh_port)

    def get_ssh_cmd(self):
        return " ".join(self.ssh_cmd)

    def add_exclude_file(self, exclude_file_pattern):
        self.exclude_file_list.append(
            '--exclude="%s"' % exclude_file_pattern)

    def get_exclude_file(self):
        return " ".join(self.exclude_file_list)

    def get_sync_dir(self):
        return '{local_dir}/ {user}@{host}:{remote_dir}'.format(
            **self.__dict__)

    def get_cmd(self):
        rsync_cmd = ['rsync']
        rsync_cmd.append("-e '%s'" % self.get_ssh_cmd())
        rsync_cmd.append(self.get_sync_dir())
        rsync_cmd.append(self.get_exclude_file())
        rsync_cmd.append('-rlvxz')
        rsync_cmd.append('--delete')
        rsync_cmd.append('--timeout=60')

        return " ".join(rsync_cmd)

    def run_cmd(self):
        rsync_cmd = self.get_cmd()
        print rsync_cmd
        rsync_process = pexpect.spawn(rsync_cmd)
        rsync_process.expect('.*password:.*')
        rsync_process.sendline(self.password)
        rsync_process.expect(pexpect.EOF)


class RsyncDir(object):
    def __init__(self, from_dir, to_dir):
        self.from_dir = self.normally_dir_path(from_dir)
        self.to_dir = self.normally_dir_path(to_dir)

    def normally_dir_path(self, dir_path):
        if dir_path[-1] == '/':
            return dir_path
        else:
            return dir_path + '/'

    def get_cmd(self):
        return 'rsync -av %s %s' % (self.from_dir, self.to_dir)

