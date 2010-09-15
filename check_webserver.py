# coding: utf-8
# restart webserver if dead
import urllib2
import os


class Website(object):
    HTTP_CORRECT_STATUS = 200

    def __init__(self, url):
        self.work_dir = os.path.dirname(os.path.abspath(__file__))
        self.url = url

    def is_web_server_running(self):
        return self.get_url_http_code() == self.HTTP_CORRECT_STATUS

    def get_url_http_code(self):
        try:
            request = urllib2.urlopen(self.url)
        except:
            return False
        else:
            return request.code

    def restart_web_server(self):
        cmd_list = []
        cmd_list.append("cd %s" % self.work_dir)
        cmd_list.append("fab production_server restart_web_server")
        os.system(" && ".join(cmd_list))

if __name__ == '__main__':
    import settings

    website = Website(settings.WEBSITE_URL)
    if website.is_web_server_running():
        print "running"
    else:
        print "not running"
        website.restart_web_server()
