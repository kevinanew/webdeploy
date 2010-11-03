# coding: utf8
"""
Compressor for django template
"""
import os
import re
import sys

from lib.slimmer import html_slimmer

YUI_COMPRESSOR_PATH = '../tool/yuicompressor-2.4.2.jar'


class DjangoTemplateCompressor():
    """
    Compressor for django template
    """
    def __init__(self, template_file_path):
        self.template_file_path = template_file_path
        self.template_content = open(template_file_path, 'rb').read()
        self.result = self.template_content.decode('utf8')

        self.yui_compressor_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), YUI_COMPRESSOR_PATH))

    def process(self):
        """
        template compressor process
        """
        if os.path.splitext(self.template_file_path)[1] in ('.html', '.htm'):
            self.result = self.remove_line_space()
            self.result = html_slimmer(self.result)
            self.result = self.strip_spaces_between_tags(self.result)
        elif os.path.splitext(self.template_file_path)[1] in ('.js', ):
            self.compress_js()

    def save_template_file(self):
        template_file = open(self.template_file_path, "wb")
        template_file.write(self.get_result().encode('utf8'))
        template_file.close()

    def get_result(self):
        return self.result

    def strip_spaces_between_tags(self, value):
        return re.sub(r'%}\s+', '%}', value)

    def remove_line_space(self):
        result = ""
        for content_line in self.result.split(u'\n'):
            content_line = content_line.strip()

            if content_line:
                result += content_line + u'\n'

        return result

    def compress_js(self):
        compress_cmd = ('java -jar {yuicompressor} '
            '{js_source_file} -o {js_minfy_file} 1>/dev/null 2>/dev/null'
            ).format(yuicompressor=self.yui_compressor_path, 
                js_source_file=self.template_file_path,
                js_minfy_file=self.template_file_path)

        self.run_cmd(compress_cmd)

    def run_cmd(self, cmd):
        print("[localhost] run: " + cmd)
        os.system(cmd)


if __name__ == '__main__':
    template_filename = sys.argv[1]
    
    _, file_ext_name = os.path.splitext(template_filename)
    if file_ext_name not in ['.html', '.htm']:
        SystemExit('template must be *.html or *.htm')

    compressor = DjangoTemplateCompressor(template_filename)
    compressor.process()
    compressor.save_template_file()

