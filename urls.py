from handlers import Passport, IndexHandler,House,RegisterHandler,VerifyCode
from config import setting
import os

from handlers.BaseHandler import StaticFileBaseHandler as StaticFileHandler

from utils.DIY_captcha import DIY_captcha

urls = [
    (r"/", Passport.IndexHandler),
    (r"/index", House.Indexhandler),
    (r"/register", RegisterHandler.RegisterHandler),
    (r"/api/imagecode", VerifyCode.ImageCodeHandler), #注册页面的验证码的路由
    (r"/api/new_imagecode", DIY_captcha.DIY_Verifycode), #注册页面的验证码的路由



    (r"/(.*)", StaticFileHandler,
    dict(path=os.path.join(os.path.dirname(__file__), "html"), default_filename="index.html"))
]
