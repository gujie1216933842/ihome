
from .BaseHandler import BaseHandler


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

class ToLoginHandler(BaseHandler):
    def post(self):
        pass

class IndexHandler(BaseHandler):
    def get(self):
        '''
        1.判断用户是否有登录态
          方法:读session
        2.如果有登陆态,
        3.如果
        '''
        self.render('index.html')