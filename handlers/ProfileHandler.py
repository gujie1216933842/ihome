# Author:Bob
from handlers.BaseHandler import BaseHandler
import logging
from utils.common import require_logined

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
        self.write(dict(code='00', msg='ok', data=dict(user_id=user_id, name=ret['up_avatar']
                                                       , mobile=ret['up_mobile'], avatar=img_url)))

