from handlers import Passport, IndexHandler,House,RegisterHandler,VerifyCode,ProfileHandler
from config import setting
import os
from handlers.BaseHandler import StaticFileBaseHandler as StaticFileHandler
from utils.DIY_captcha import DIY_captcha

urls = [
    (r"/house/index", House.Indexhandler),  #加载首页信息的接口
    (r"/house/myhouse", House.MyHouseHandler),  #加载我的房源接口
    (r"/house/areas", House.AreaInfoHandler),  #加载我的房源接口

    (r"/register", RegisterHandler.RegisterHandler),
    (r"/login", IndexHandler.LoginHandler),
    (r"/tologin", IndexHandler.ToLoginHandler),
    (r"/register_new", VerifyCode.regiser),
    (r"/checklogin",ProfileHandler.ProfileHandler ),
    (r"/api/imagecode", VerifyCode.ImageCodeHandler), #注册页面的验证码的路由
    (r"/api/new_imagecode", DIY_captcha.DIY_Verifycode), #注册页面的验证码的路由
    (r"/profile/ucenter", ProfileHandler.UcenterHander), #个人中心路由
    (r"/profile/ProfileShowEdit", ProfileHandler.ProfileShowEdit), #修改用户头像和用户名初始化页面显示接口
    (r"/profile/UploadHandler", ProfileHandler.UploadHandler), #用户修改头像上传图片接口
    (r"/profile/NickNameEdit", ProfileHandler.NickNameEdit), #用户修改昵称接口
    (r"/profile/LogoutHandler", ProfileHandler.LogoutHandler), #用户退出登录接口
    (r"/profile/AuthHandler", ProfileHandler.AuthHandler), #用户实名认证接口
    (r"/(.*)", StaticFileHandler,
    dict(path=os.path.join(os.path.dirname(__file__), "html"), default_filename="index.html"))
]
