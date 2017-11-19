from PIL import Image,ImageDraw,ImageFont,ImageFilter

import random
from handlers.BaseHandler import BaseHandler
class DIY_Verifycode(BaseHandler):
    #随机码
    def get(self,length = 6):
        code = ''
        char = '23456789abcdefghjklmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
        for i in range(length):
            index = random.randint(0,55)
            code += char[index]

        self.write(code)