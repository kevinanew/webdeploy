# coding: utf-8


class DjangoTemplateCompiler(object):
    def __init__(self, template_path):
        self.template_path = template_path
        self.template_content = open(template_path, 'r').read().decode('utf8')
        self.context_value = {}

    def process(self):
        import inspect
        for _compile_name, _compile_function in inspect.getmembers(self):
            is_compile_function = _compile_name.find('compile_') == 0
            if is_compile_function and inspect.ismethod(_compile_function):
                _compile_function()

    def set_value(self, **kargs):
        assert kargs
        self.context_value.update(kargs)

    def compile_scm_revision(self):
        """add revision info into template"""
        tag = '{{ dev_version }}'
        if tag not in self.template_content:
            return False

        from datetime import datetime
        compile_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        code_version = self.context_value.get('code_version')

        self.template_content = self.template_content.replace(
            tag, u'<!--%s|r%s-->' % (compile_date, code_version))


    def save_template_file(self):
        template_file = open(self.template_path, "w")
        template_file.write(self.template_content.encode('utf8'))
        template_file.close()
