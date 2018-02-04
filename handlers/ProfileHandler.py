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
        sql = "select up_name , up_mobile , up_avatar from ih_user_profile where up_user_id = %s"
        try:
            ret = self.db.get(sql, user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='01', msg='查询数据库出错!'))
        if ret['up_avatar']:
            img_url = config.qiniu_url + ret['up_avatar']
        else:
            img_url = None
        self.write(dict(code='00', msg='ok', data=dict(user_id=user_id, name=ret['up_mobile']
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
        logging.info("修改前的session信息")
        logging.info(self.session.data)
        logging.info("需要修改的值: %s%s" % (config.qiniu_url, key))
        self.session.data['avatar'] = "%s%s" % (config.qiniu_url, key)
        logging.info("修改后的session信息")
        logging.info(self.session.data)

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
        # 如果是成功,则在session中把昵称修改,并且返回给前端
        logging.info("修改前的session信息: %s" % (self.session.data))
        logging.info("需要修改的昵称值: %s" % (nickName))
        self.session.data['nickname'] = nickName
        logging.info("修改后的session信息: %s" % (self.session.data))
        return self.write(dict(code='00', msg='ok', data=nickName))
