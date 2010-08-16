# coding: utf-8


class Rsync(object):
    def __init__(self, host, user, local_dir, remote_dir):
        self.host = host
        self.user = user
        self.local_dir = local_dir
        self.remote_dir = remote_dir

        self.ssh_cmd = ['ssh']
        self.exclude_file_list = []

    def add_ssh_key(self, ssh_key_file):
        self.ssh_cmd.append('-i %s' % ssh_key_file)

    def add_ssh_port(self, ssh_port):
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
        return '{local_dir} {user}@{host}:{remote_dir}'.format(
            **self.__dict__)

    def get_cmd(self):
        rsync_cmd = ['rsync']
        rsync_cmd.append("-e '%s'" % self.get_ssh_cmd())
        rsync_cmd.append(self.get_sync_dir())
        rsync_cmd.append(self.get_exclude_file())
        rsync_cmd.append('-rlvx')
        rsync_cmd.append('--delete')

        return " ".join(rsync_cmd)
