from handlers import Passport



handlers = [
    (r"/",Passport.IndexHandler),
]