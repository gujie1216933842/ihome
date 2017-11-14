# Author:Bob
from .BaseHandler import BaseHandler
import logging

class IndexHandler(BaseHandler):
    def get(self):

        logging.debug('dug msg')
        logging.info('info msg')
        logging.warning('warning msg')
        logging.error('error msg')


        self.write('欢迎来到tornado的世界!')
