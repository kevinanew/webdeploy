
class MySql:
    def __init__(self, root_user, root_password):
        self.root_user = root_user
        self.root_password = root_password
        self.mysql_client = ' mysql -u{username} -p{password} -e "%s"'.format(
            username=self.root_user, password=self.root_password)

    def create_user_for_database(self, user, password, database):
        cmd = ("grant ALL PRIVILEGES on {dbname}.* to "
            "'{username}'@'localhost' "
            "IDENTIFIED BY '{password}';").format(
                dbname=database, username=user, password=password)
        cmd += ("grant ALL PRIVILEGES on {dbname}.* to "
            "'{username}'@'127.0.0.1' "
            "IDENTIFIED BY '{password}';").format(
                dbname=database, username=user, password=password)

        return self.mysql_client % cmd

    def create_database(self, database):
        cmd = ('CREATE DATABASE IF NOT EXISTS {dbname} CHARACTER SET utf8'
        ' COLLATE utf8_general_ci;').format(dbname=database)
        return self.mysql_client % cmd

if __name__ == '__main__':
    mysql = MySql('root', 'RootPassword')
    print mysql.create_database('ABC')
