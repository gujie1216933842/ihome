from .BaseHandler import BaseHandler
import re
from hashlib import sha1
import logging


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')


class ToLoginHandler(BaseHandler):
    def post(self):
        '''
        1.判断参数是否缺失
        2.判断手机号格式
        3.通过前台传入的手机号和密码去查询数据库,验证手机号和密码是否正确
        :return:
        '''
        mobile = self.get_argument('mobile')
        pwd = self.get_argument('pwd')
        if not all((mobile, pwd)):
            return self.write(dict(code='01', msg='参数缺失'))

        if not re.match(r"^1\d{10}$", mobile):
            return self.write(dict(code='02', msg='手机号格式不对'))

        sha = sha1()
        sha.update(pwd.encode('utf-8'))
        pwdsha1 = sha.hexdigest()
        # 开始查询数据库
        sql = 'select up_user_id from ih_user_profile where up_mobile = %(up_mobile)s and  up_passwd = %(up_passwd)s'
        try:
            ret = self.db.get(sql, up_mobile=mobile, up_passwd=pwd)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='03', msg='数据查询失败'))
        else:
            if not ret:
                return self.write(dict(code='04', msg='您输入的用户名和密码有误,请重新输入!'))
            else:
                return self.write(dict(code="00", msg='登录成功!'))


class IndexHandler(BaseHandler):
    def get(self):
        '''
        1.判断用户是否有登录态
          方法:读session
        2.如果有登陆态,
        3.如果
        '''
        self.render('index.html')
