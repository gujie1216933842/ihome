import logging

from utils.captcha import captcha
from .BaseHandler import BaseHandler
import constant
from utils.DIY_captcha.DIY_captcha import DIY_Verifycode
import json
import re


class ImageCodeHandler(BaseHandler):
    def get(self):
        code_id = self.get_argument('code_id')  # 本条验证码
        pcode_id = self.get_argument('pcode_id')  # 上一条验证码
        logging.info(code_id)
        logging.info(pcode_id)
        if pcode_id:
            try:
                self.redis.delete('')
            except Exception as e:
                logging.error(e)  # 如果redis删除有误,则记录在日志中
                # 调用验证码生成模块
                # name:验证码名称
                # text:验证码内容
                # image:验证码二进制数据
        Verifycode = DIY_Verifycode()
        code, image = Verifycode.get()
        logging.info('验证码code_lower:' + code)
        # 存入redis
        try:
            self.redis.setex("image_code_%s" % code_id, constant.IMAGE_CODE_EXPIRES_SECONDS, code)
        except Exception as e:
            logging.error(e)
            self.write('')
        # 如果redis存入正常
        self.write(image)
        self.set_header("Content-Type", "image/png")


class regiser(BaseHandler):
    def post(self):
        # 获取参数
        # 判断图片验证码,如果不成功,返回错误信息,如果成功,判断密码
        # 查看手机号是否存在,如果存在,提示已经注册的提示信息
        # 判断两次密码是否相同,如果相同提示注册成功,把数据插入数据库,如果不成功,提示错误信息
        mobile = self.get_argument('mobile')
        code_id = self.get_argument('code_id')
        imagecode = self.get_argument('imagecode')
        password = self.get_argument('password')
        password2 = self.get_argument('password2')

        logging.info('mobile:' + mobile)
        logging.info('imagecode:' + imagecode)
        logging.info('password:' + password)
        logging.info('password2:' + password2)
        '''
        1.比较验证码是否正确
        2.比较两次密码是否一致
        3.判断用户是否已经注册
        4.用户数据入库
        '''
        if not all((mobile, imagecode, password, password2)):
            # all()方法等价于   if mobile  and imagecode and password and password2
            return self.write(dict(code='01', msg='参数缺失'))
        if not re.match(r"^1\d{10}$", mobile):
            return self.write(dict(code='02', msg='手机号格式不对'))

        # 开始验证图片验证码
        '''
        1.查询redis可能出错
        2.查询的redis可能为空
        3.如果查询redis中有对应的value值,删除redis
        4.与前台传入的图片验证码做比较,注:都是转为小写字母比较
        '''
        try:
            real_piccode = self.redis.get('image_code_' + code_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='03', msg='查询redis出错'))

        if not real_piccode:
            return self.write(dict(code='04', msg='redis中图片验证码过期'))

        # 输入的图片验证码和redis中的比较
        if real_piccode != imagecode:
            return self.write(dict(code='09', msg='输入的验证码不正确'))

        # 如果redis是存在的,需要删除redis中的相关的key
        try:
            self.redis.delete('image_code_' + imagecode)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='05', msg='删除redis失败'))

        # 判断用户两次输入的密码是否一致
        if password != password2:
            return self.write(dict(code='06', msg='两次密码设置不一致,请重新设置'))

        # 检查手机号是否在数据库中存在(需要查询数据库)
        sql = "select count(*) as n from ih_user_profile where up_mobile = %s "
        try:
            ret = self.db.get(sql, mobile)
        except Exception as e:
            logging.error(e)
        else:
            if 0 != ret['n']:
                return self.write(dict(code='07', msg='手机号已经注册'))
            else:
                # 插入数据库
                sql = "insert into ih_user_profile (up_mobile,up_passwd,up_ctime)" \
                      "VALUES(%s,%s,now()) "
                try:
                    self.db.execute(sql, mobile, password, )
                except Exception as e:
                    logging.error(e)
                    return self.write(dict(code='08', msg='sql插入出错'))
                else:
                    return self.write(dict(code='00', msg='恭喜,注册成功'))
