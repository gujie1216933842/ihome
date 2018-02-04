# Author:Bob
from handlers.BaseHandler import BaseHandler
import logging
from utils.common import require_logined
import config
from utils.image_storage import storage


class ProfileHandler(BaseHandler):
    '''
    需要判断登录态的页面刷新时需要异步调用的后台接口
    '''

    @require_logined
    def get(self):
        '''
        1.从session中获取user_id
        2.通过user_id去查询数据库,获取用户昵称,手机号,头像等信息
        3.需要判断一下头像连接是否存在,如果存在,需要在链接之前拼接一个公共地址,如果不存在,则赋值为none
        4.给前端返回json数据
        :return:
        '''
        logging.info(self.session.data)
        user_id = self.session.data['user_id']

        sql = "select up_name , up_mobile , up_avatar from ih_user_profile where up_user_id = %s"
        try:
            ret = self.db.get(sql, user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='01', msg='查询数据库出错!'))
        if ret['up_avatar']:
            img_url = ret['up_avatar']
        else:
            img_url = None
        self.write(dict(code='00', msg='ok', data=dict(user_id=user_id, name=ret['up_mobile']
                                                       , mobile=ret['up_mobile'], avatar=img_url)))


class UcenterHander(BaseHandler):
    '''
    ihome个人中心
    '''

    @require_logined
    def get(self):
        user_id = self.session.data['user_id']  # 在session中获取用户id
        sql = "select up_name , up_mobile ,up_name, up_avatar from ih_user_profile where up_user_id = %s"
        try:
            ret = self.db.get(sql, user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='01', msg='查询数据库出错!'))
        if ret['up_avatar']:
            img_url = config.qiniu_url + ret['up_avatar']
        else:
            img_url = None
        self.write(dict(code='00', msg='ok', data=dict(user_id=user_id, name=ret['up_name']
                                                       , mobile=ret['up_mobile'], avatar=img_url)))


class ProfileShowEdit(BaseHandler):
    @require_logined
    def get(self):
        '''
           展示图片和用户名修改页面的初始化数据接口
        :return:
        '''
        userinfo_data = self.session.data
        logging.info('session中的用户信息:')
        logging.info(userinfo_data)
        return self.write(dict(code='00', msg='ok', data=userinfo_data))


class UploadHandler(BaseHandler):
    @require_logined
    def post(self, *args, **kwargs):
        '''
        头像上传接口
        '''
        # 接受上传的数据
        try:
            image_data = self.request.files['avatar'][0]['body']
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='bb', msg='前端向后台传输图片失败'))
        # 如果后台接收到图片数据,把图片数据作为参数传递给封装好的七牛接口
        try:
            key = storage(image_data)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='cc', msg="向七牛传递数据出错"))
        # 七牛上传图片成功,拿到返回的key,把key保存到数据库
        user_id = self.session.data['user_id']
        sql = "update ih_user_profile set up_avatar = %(avatar)s where up_user_id = %(user_id)s "
        try:
            row_count = self.db.execute_rowcount(sql, avatar=key, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="dd", msg="更新数据库图片失败"))
        # 保存成功,修改session中的头像图片
        self.session.data['avatar'] = "%s%s" % (config.qiniu_url, key)
        self.session.save()
        return self.write(dict(code="00", msg="ok", data="%s%s" % (config.qiniu_url, key)))


class NickNameEdit(BaseHandler):
    @require_logined
    def post(self, *args, **kwargs):
        # 获取前台传过来的昵称
        nickName = self.get_argument('name')
        # 在session中获取user_id,在数据库中修改
        user_id = self.session.data['user_id']
        sql = "update ih_user_profile set up_name = %(name)s where up_user_id = %(user_id)s "
        try:
            self.db.execute_rowcount(sql, name=nickName, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='bb', msg="数据库修改昵称出错"))
        # 如果是成功,则在session中把昵称修改,把修改的值保存在redis中,并且返回给前端
        self.session.data['nickname'] = nickName
        self.session.save()
        return self.write(dict(code='00', msg='ok', data=nickName))


class LogoutHandler(BaseHandler):
    @require_logined
    def get(self):
        '''
        用户退出登录接口
        :return:
        '''
        # 调用session中封装的clear方法
        self.session.clear()
        return self.write(dict(code="00", msg="ok,退出成功"))


class AuthHandler(BaseHandler):
    @require_logined
    def get(self):
        '''
        进入实名认证页面加载的接口
        :return:
        '''
        # 在session中获取用户的user_id
        # 通过user_id在数据库中查询用户实名信息(是否已经实名过了)
        user_id = self.session.data['user_id']
        sql = " select up_real_name , up_id_card from ih_user_profile where up_user_id = %s "
        try:
            ret = self.db.get(sql, user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='bb', msg="查询数据库出错"))
        if not ret:
            return self.write(dict(code='cc', msg="数据库中没用该用户的信息"))
        return self.write(dict(code="00",msg="ok",data=ret))

    @require_logined
    def post(self, *args, **kwargs):
        '''
        如果用户还没有进行实名注册,实名注册的接口,需要提交用户的真实姓名和身份证信息,
        :param args:
        :param kwargs:
        :return:
        '''
