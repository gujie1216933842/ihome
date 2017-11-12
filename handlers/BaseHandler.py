#Author:Bob
from tornado.web import RequestHandler



class BaseHandler(RequestHandler):
    '''
       handler的基础类
    '''
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