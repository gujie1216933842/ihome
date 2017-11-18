from handlers import Passport,IndexHandler
from config import setting

from handlers.BaseHandler import StaticFileBaseHandler as StaticFileHandler


urls = [
    (r"/", Passport.IndexHandler),
    (r"/index", IndexHandler.Indexhandler),
]
