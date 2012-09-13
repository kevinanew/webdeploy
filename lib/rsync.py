# coding: utf-8
import os
import shlex
import subprocess

from lib import pexpect


RETURN_CODE_SECUESS = 0

class Rsync(object):
    def __init__(self, host, user, local_dir, remote_dir):
        if ':' in host:
            self.host, port = host.split(':')
        else:
            self.host = host
            port = '22'
        self.user = user
        self.password = ''
        self.ssh_key_file = ''
        self.local_dir = os.path.normpath(local_dir)
        self.remote_dir = os.path.normpath(remote_dir)

        self.ssh_cmd = ['ssh']
        self.exclude_file_list = []
        self.max_try_time = 5
        self.add_ssh_port(port)
        self.timeout = 120

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

    def set_password(self, password):
        self.password = password

    def set_ssh_key_file(self, ssh_key_file):
        self.ssh_key_file = ssh_key_file

    def get_cmd(self):
        rsync_cmd = ['rsync']
        rsync_cmd.append("-e '%s'" % self.get_ssh_cmd())
        rsync_cmd.append(self.get_sync_dir())
        rsync_cmd.append(self.get_exclude_file())
        rsync_cmd.append('-rlvxzc')
        rsync_cmd.append('--partial')
        rsync_cmd.append('--delete')
        rsync_cmd.append('--timeout=%s' % self.timeout)

        return " ".join(rsync_cmd)

    def _run_command(self, command):
        try_time = 0
        while try_time < self.max_try_time:
            process = subprocess.Popen(shlex.split(command))
            return_code = process.wait()
            if return_code == RETURN_CODE_SECUESS:
                break
            else:
                try_time += 1
                print "Try again ... "
        else:
            raise Exception("Run command fail")

    def run_cmd(self):
        rsync_cmd = self.get_cmd()
        print rsync_cmd

        if self.ssh_key_file:
            print "Rsync: use ssh key"
            self._run_command(rsync_cmd)
        elif self.password:
            print "Rsync: use password"
            rsync_process = pexpect.spawn(rsync_cmd)
            rsync_process.expect('.*[Pp]assword:.*')
            rsync_process.sendline(self.password)
            rsync_process.expect(pexpect.EOF)
        else:
            print "Rsync: no password and key"
            self._run_command(rsync_cmd)


class RsyncDir(object):
    def __init__(self, from_dir, to_dir):
        self.from_dir = self.normally_dir_path(from_dir)
        self.to_dir = self.normally_dir_path(to_dir)
        self.exclude_dir_list = []

    def normally_dir_path(self, dir_path):
        if dir_path[-1] == '/':
            return dir_path
        else:
            return dir_path + '/'

    def add_exclude_dir(self, exclude_dir):
        self.exclude_dir_list.append(
            '--exclude="%s"' % exclude_dir)

    def get_cmd(self):
        _cmd = 'rsync -avc %s %s' % (self.from_dir, self.to_dir)

        if self.exclude_dir_list:
            _cmd = "%s %s" % (_cmd, ' '.join(self.exclude_dir_list))

        return _cmd

