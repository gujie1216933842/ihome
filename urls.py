from handlers import Passport

urls = [
    # (r"/", Passport.IndexHandler),
    (r"^/api/house/index$", Passport.IndexHandler),
]
