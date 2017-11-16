from .BaseHandler import BaseHandler
class Indexhandler(BaseHandler):
    def index(self):
        self.render(self,'index.html')