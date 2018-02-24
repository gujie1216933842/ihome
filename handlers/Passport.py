# Author:Bob
from .BaseHandler import BaseHandler
import logging


class IndexHandler(BaseHandler):
    def get(self):
        # logging.debug('dug msg')
        # logging.info('info msg')
        # logging.warning('warning msg')
        logging.error('error msg')
        self.render('index.html')
        # self.write('欢迎来到tornado的世界!')


class CheckLoginHandler(BaseHandler):
    def get(self):
        if not self.get_current_user():
            return self.write(dict(code='aa', msg='no login'))
        else:
            return self.write(dict(code='00', msg="ok, is login"))
