from handlers import Passport, IndexHandler,House,RegisterHandler
from config import setting
import os

from handlers.BaseHandler import StaticFileBaseHandler as StaticFileHandler

urls = [
    (r"/", Passport.IndexHandler),
    (r"/index", House.Indexhandler),
    (r"/register", RegisterHandler.RegisterHandler),

    (r"/(.*)", StaticFileHandler,
    dict(path=os.path.join(os.path.dirname(__file__), "html"), default_filename="index.html"))
]
