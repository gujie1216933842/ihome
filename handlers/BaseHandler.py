# Author:Bob
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    '''
       handler的基础类
    '''

    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def prepare(self):
        pass

    def write_error(self):
        pass

    def set_default_handlers(self):
        pass

    def initialize(self):
        pass

    def on_finish(self):
        pass
