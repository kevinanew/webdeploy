# coding: utf-8
import os
from datetime import datetime

import settings


class DatabaseBackup(object):
    def __init__(self, db_user, db_password, db_name):
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

        self.sql_dump_filename = '%s.sql.gz' % datetime.now().strftime(
            '%F_%Hh%Mm%Ss')
    
        self.remote_backup_dir = settings.REMOTE_DATABASE_BACKUP_DIR
        self.local_backup_dir = os.path.expanduser(
            settings.LOCAL_DATABASE_BACKUP_DIR)

    def get_remote_backup_dir(self):
        return self.remote_backup_dir

    def get_remote_backup_file_path(self):
        return os.path.join(self.remote_backup_dir, self.sql_dump_filename)

    def get_local_backup_file_path(self):
        return os.path.join(self.local_backup_dir, self.sql_dump_filename)

    def make_local_backup_file_path(self):
        backup_file_dir = os.path.dirname(
            self.get_local_backup_file_path())
        if not os.path.exists(backup_file_dir):
            os.makedirs(backup_file_dir)

    def get_remove_remote_backup_file_cmd(self):
        return 'rm {backup_file}'.format(
            backup_file=self.get_remote_backup_file_path())

    def get_backup_cmd(self):
        mysql_backup_cmd_template = (
            'mysqldump -u {db_user} -p"{db_password}" {db_name} '
            ' --single-transaction | gzip -9 > {backup_file}')

        return mysql_backup_cmd_template.format(
            backup_file=self.get_remote_backup_file_path(), **self.__dict__)

    def get_show_remote_backup_file_cmd(self):
        return 'ls -lh {backup_file}'.format(
            backup_file=self.get_remote_backup_file_path())
