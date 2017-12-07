import logging

from utils.captcha import captcha
from .BaseHandler import BaseHandler
import constant
from utils.DIY_captcha.DIY_captcha import DIY_Verifycode


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
        self.redis.setex("image_code_%s" % code_id, constant.IMAGE_CODE_EXPIRES_SECONDS, code)
        # 存入redis
        try:
            self.redis.setex("image_code_%s" % code_id, constant.IMAGE_CODE_EXPIRES_SECONDS, code)
        except Exception as e:
            logging.error(e)
            self.write('')
        # 如果redis存入正常
        self.write(image)
        self.set_header("Content-Type", "image/png")
