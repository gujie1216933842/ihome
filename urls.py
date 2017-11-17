from handlers import Passport,IndexHandlers

urls = [
    (r"/", Passport.IndexHandler),
    (r"/index", IndexHandlers.index),
]
