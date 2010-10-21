# coding: utf-8
import os
import glob

import settings


class DatabaseRestore(object):
    def __init__(self, db_user, db_password, db_name):
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

        self.local_backup_dir = settings.LOCAL_DATABASE_BACKUP_DIR
        self.remote_restore_dir = settings.REMOTE_DATABASE_RESTORE_DIR

    def display_restore_info(self):
        print "========================================================"
        print "= Database name:", self.db_name
        print "= User:", self.db_user
        print "========================================================"

    def get_remote_restore_dir(self):
        return self.remote_restore_dir

    def get_remote_restore_file(self):
        restore_file_name = os.path.basename(self.restore_file)
        return os.path.join(self.remote_restore_dir, restore_file_name)

    def get_local_restore_file(self):
        return self.restore_file

    def get_unziped_sql_filename(self):
        unziped_sql_filename, _= os.path.splitext(
            self.get_remote_restore_file())
        return unziped_sql_filename

    def confirm(self):
        error = 0
        while True:
            is_continue = raw_input('Is contiune? (y/n): ')
            if is_continue == 'y':
                break
            elif is_continue == 'n':
                raise SystemExit('Command exit ...')
            else:
                print "choice wrong, please input again"
            
            if error > 3:
                raise SystemExit('Try %s times, command exit ...' % error)
            else:
                error += 1

    def get_backup_file_list(self):
        backup_file_pattern = os.path.join(self.local_backup_dir, '*.sql.gz')
        backup_files = glob.glob(backup_file_pattern)

        backup_files.sort()
        backup_files.reverse()
        return backup_files

    def list_backup_file(self):
        backup_file_id = 0
        for _backup_file in self.get_backup_file_list():
            backup_file_id += 1
            backup_file_id_text = "[id:%s]" % backup_file_id
            print backup_file_id_text, _backup_file, backup_file_id_text

    def set_restore_file(self):
        while True:
            user_input_backup_file_id_str = raw_input(
                "Restore backup file id: ")
            if not user_input_backup_file_id_str.isdigit():
                print "Error: Please re-inputer a backup file id"
                continue

            backup_file_id = int(user_input_backup_file_id_str)
            backup_file_list = self.get_backup_file_list()
            try:
                self.restore_file = backup_file_list[backup_file_id-1]
                break
            except IndexError:
                print "Error: Not find file_id:", backup_file_id

    def get_restore_database_cmd(self):
        return "%s && %s; %s" % (self._get_unziped_sql_file_cmd(),
            self._get_sql_restore_cmd(), self._get_sql_clean_file_cmd())
    
    def _get_unziped_sql_file_cmd(self):
        return 'gunzip -c %s > %s' % (self.get_remote_restore_file(),
            self.get_unziped_sql_filename())

    def _get_sql_restore_cmd(self):
        # cmd: mysql -u [uname] -p[pass] [db_to_restore] < [backupfile.sql]
        sql_restore_cmd_template = (
            'mysql -u {db_user} -p"{db_password}" {db_name} '
            '< {unziped_sql_file}')
        return sql_restore_cmd_template.format(
            unziped_sql_file=self.get_unziped_sql_filename(),
            **self.__dict__)

    def _get_sql_clean_file_cmd(self):
        return 'rm -f %s ;rm -f %s' % (self.get_remote_restore_file(),
            self.get_unziped_sql_filename())