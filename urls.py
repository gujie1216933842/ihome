from handlers import Passport, IndexHandler,House,VerifyCode,ProfileHandler,Orders,ShowChatHandler
import os
from handlers.BaseHandler import StaticFileBaseHandler as StaticFileHandler
from utils.DIY_captcha import DIY_captcha

urls = [
    (r"/house/index", House.Indexhandler),  #加载首页信息的接口
    (r"/house/myhouse", House.MyHouseHandler),  #加载我的房源接口
    (r"/house/areas", House.AreaInfoHandler),  #加载区域信息接口
    (r"/house/info", House.HouseInfoHandle),  #加载房屋信息接口,上传房屋图片接口
    (r"/house/image", House.HouseImageHandler),  #上传房屋图片接口

    (r"/house/list", House.HouseList),  #搜索房屋列表

    (r"/order/checklogin", Passport.CheckLoginHandler),  #订单页面检查是登录接口
    (r"/order/order", Orders.OrderHandler),  #提交订单接口
    (r"/order/orderlist", Orders.OrderListHandler),  #订单列表,对于每一个用户包括我的订单和客户订单
    (r'/order/accept', Orders.AcceptOrderHandler), # 接单
    (r'/order/reject', Orders.RejectOrderHandler), # 拒单
    (r'/order/comment', Orders.OrderCommentHandler),

    (r"/tologin", IndexHandler.ToLoginHandler),
    (r"/register_new", VerifyCode.regiser),
    (r"/checklogin",ProfileHandler.ProfileHandler ),
    (r"/imagecode", VerifyCode.ImageCodeHandler), #注册页面的验证码的接口
    #(r"/api/new_imagecode", DIY_captcha.DIY_Verifycode), #单独测试的图片验证码的接口
    (r"/profile/ucenter", ProfileHandler.UcenterHander), #个人中心路由
    (r"/profile/ProfileShowEdit", ProfileHandler.ProfileShowEdit), #修改用户头像和用户名初始化页面显示接口
    (r"/profile/UploadHandler", ProfileHandler.UploadHandler), #用户修改头像上传图片接口
    (r"/profile/NickNameEdit", ProfileHandler.NickNameEdit), #用户修改昵称接口
    (r"/profile/LogoutHandler", ProfileHandler.LogoutHandler), #用户退出登录接口
    (r"/profile/AuthHandler", ProfileHandler.AuthHandler), #用户实名认证接口
    (r"/chat", ShowChatHandler.ChatHandler), #用户实名认证接口
    (r"/(.*)", StaticFileHandler,
    dict(path=os.path.join(os.path.dirname(__file__), "html"), default_filename="index.html"))
]
