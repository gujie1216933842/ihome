from .BaseHandler import BaseHandler

class RegisterHandler(BaseHandler):
    def get(self):
        self.render('register.html')