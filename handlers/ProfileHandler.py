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
        return self.write(dict(code='00',msg='ok',data=userinfo_data))


class UploadHandler(BaseHandler):
    '''

    '''
    @require_logined
    def post(self, *args, **kwargs):
        pass


