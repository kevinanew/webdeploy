# coding: utf-8


class SettingsBuilder(object):
    def __init__(self, filename='settings.py'):
        self.filename = filename
        self.server_type = ''
        self.content_list = []

    def add_settings(self, settings_key, settings_value):
        if isinstance(settings_value, basestring):
            _settings_value = '"%s"' % settings_value
        else:
            _settings_value = settings_value

        self.content_list.append(
            "%s = %s" % (settings_key, _settings_value)
            )

    def show_prompt(self, prompt):
        input_value = raw_input("[%s]: %s " % (self.server_type, 
            prompt.rstrip()))
        return input_value.strip()

    def input_settings(self, settings_key, prompt):
        settings_value = self.show_prompt(prompt)

        self.add_settings(settings_key, settings_value)

    def input_ssh_host(self):
        host = self.show_prompt("ssh host ip:")
        if ":" in host:
            ip_address, ip_port = host.split(':')
            ip_port = int(ip_port)
        else:
            ip_address = host
            ip_port = 22  # default ssh port
        
        # TODO: check ip address format
        
        self.add_settings('%s_SSH_HOSTS' % self.server_type.upper(),
            "['%s']" % ip_address)
        self.add_settings('%s_SSH_PORT' % self.server_type.upper(), ip_port)


    def set_server_type(self, server_type):
        assert server_type in ['staging', 'production']
        self.server_type = server_type

    def save(self):
        self.settings_file = open(self.filename, 'w')
        self.settings_file.write("\n".join(self.content_list))
        self.settings_file.close()


if __name__ == '__main__':
    settings_builder = SettingsBuilder()

    settings_builder.set_server_type('staging')
    settings_builder.input_ssh_host()
    settings_builder.input_settings('STAGING_SSH_USER', "ssh user:")
    settings_builder.input_settings('STAGING_SSH_PASSWORD', "ssh password:")

    settings_builder.set_server_type('production')
    settings_builder.input_ssh_host()
    settings_builder.input_settings('PRODUCTION_SSH_USER', "ssh user:")
    settings_builder.input_settings('PRODUCTION_SSH_PASSWORD', "ssh password:")

    settings_builder.save()
