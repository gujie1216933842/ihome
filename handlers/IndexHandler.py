
from .BaseHandler import BaseHandler


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')
