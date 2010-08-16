# coding: utf-8

from rsync import Rsync


def test_get_rsync_dir():
    rsync = Rsync(host='127.0.0.1', user='test', local_dir='kkk',
        remote_dir='zzz')
    rsync.add_ssh_port(222)
    rsync.add_ssh_key('my_ssh_key.key')
    rsync.add_exclude_file('*.pyc')
    rsync.add_exclude_file('*.swp')

    assert rsync.get_cmd() == """rsync -e 'ssh -p 222 -i my_ssh_key.key' kkk test@127.0.0.1:zzz --exclude="*.pyc" --exclude="*.swp" -rlvx --delete"""
