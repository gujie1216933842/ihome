# Author:Bob
from .BaseHandler import BaseHandler


class IndexHandler(BaseHandler):
    def get(self):
        self.write('欢迎来到tornado的世界!')
