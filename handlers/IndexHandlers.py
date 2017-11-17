from .BaseHandler import BaseHandler
class Indexhandler(BaseHandler):
    def index(self):
        self.render('index.html')