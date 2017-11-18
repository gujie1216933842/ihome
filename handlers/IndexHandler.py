from .BaseHandler import BaseHandler

class Indexhandler(BaseHandler):
    def get(self):
        self.render('index.html')