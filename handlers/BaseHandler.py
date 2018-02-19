# Author:Bob
from tornado.web import RequestHandler, StaticFileHandler
from utils import session
import json


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
        """预解析json数据"""
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body.decode())
        else:
            self.json_args = {}

    def write_error(self, status_code, **kwargs):
        pass

    def set_default_handlers(self):
        pass

    def initialize(self):
        pass

    def on_finish(self):
        pass

    def get_current_user(self):
        self.session = session.Session(self)
        return self.session.data

class StaticFileBaseHandler(StaticFileHandler):
    """自定义静态文件处理类, 在用户获取html页面的时候设置_xsrf的cookie"""
    def __init__(self, *args, **kwargs):
        super(StaticFileBaseHandler, self).__init__(*args, **kwargs)
        self.xsrf_token
