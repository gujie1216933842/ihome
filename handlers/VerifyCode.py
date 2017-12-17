import logging

from utils.captcha import captcha
from .BaseHandler import BaseHandler
import constant
from utils.DIY_captcha.DIY_captcha import DIY_Verifycode
import json


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
        #获取参数
        #判断图片验证码,如果不成功,返回错误信息,如果成功,判断密码
        #查看手机号是否存在,如果存在,提示已经注册的提示信息
        #判断两次密码是否相同,如果相同提示注册成功,把数据插入数据库,如果不成功,提示错误信息
        mobile = self.get_argument('mobile')
        imagecode = self.get_argument('imagecode')
        password = self.get_argument('password')
        password2 = self.get_argument('password2')

        return self.write(dict(code = 'haha'))

