from handlers import Passport, IndexHandler,House,RegisterHandler,VerifyCode,ProfileHandler
from config import setting
import os

from handlers.BaseHandler import StaticFileBaseHandler as StaticFileHandler

from utils.DIY_captcha import DIY_captcha

urls = [
    (r"/", Passport.IndexHandler),
    (r"/index", IndexHandler.IndexHandler),
    (r"/register", RegisterHandler.RegisterHandler),
    (r"/login", IndexHandler.LoginHandler),
    (r"/tologin", IndexHandler.ToLoginHandler),
    (r"/register_new", VerifyCode.regiser),
    (r"/checklogin",ProfileHandler.ProfileHandler ),
    (r"/api/imagecode", VerifyCode.ImageCodeHandler), #注册页面的验证码的路由
    (r"/api/new_imagecode", DIY_captcha.DIY_Verifycode), #注册页面的验证码的路由
    (r"/profile/ucenter", ProfileHandler.UcenterHander), #个人中心路由
    (r"/profile/ProfileShowEdit", ProfileHandler.ProfileShowEdit), #修改用户头像和用户名初始化页面显示接口




    (r"/(.*)", StaticFileHandler,
    dict(path=os.path.join(os.path.dirname(__file__), "html"), default_filename="index.html"))
]
