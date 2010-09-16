# coding: utf-8
from database_backup import DatabaseBackup


def test_get_backup_cmd():
    database_backup = DatabaseBackup('a_user', 'b_pwd', 'c_name')
    print database_backup.get_backup_cmd()
    assert 'mysqldump -u a_user -p"b_pwd" c_name | gzip -9 > ~/database_backup/' in database_backup.get_backup_cmd()
