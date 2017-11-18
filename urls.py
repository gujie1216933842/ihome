from handlers import Passport,IndexHandler

urls = [
    (r"/", Passport.IndexHandler),
    (r"/index", IndexHandler.Indexhandler),
]
