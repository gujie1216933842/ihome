
from .BaseHandler import BaseHandler
import logging
from utils import  image_storage

class AvatarHandler(BaseHandler):
    def post(self):
        '''
        用户上传头像的接口
        :return:
        '''
        try:
            image_data = self.request.files['avatar'][0]['body']
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='bb',msg='前端向服务端上传图片失败'))
        #如果没有问题,拿到头像之后需要上传,上传过程也可能会出错
        try:
            key = image_storage.storage(image_data)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='cc',msg='向七牛上传图片失败'))
        #如果图片成功上传到七牛,把七牛返回的图片访问标记字段存入数据库
        #返回新图片的url





