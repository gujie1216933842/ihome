from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random,os
from handlers.BaseHandler import BaseHandler
import logging



class DIY_Verifycode(BaseHandler):
    def get(self):
        width = 200  # 验证码图片长度
        height = 40  # 验证码图片宽度
        numbers = 5  # 验证码个数
        self.veri_code(width, height, numbers)

    '''
    生成随机码
    '''

    def randon_code(self, length=6):
        code = ''
        char = '23456789abcdefghjklmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
        for i in range(length):
            index = random.randint(0, 55)
            code += char[index]

        return code

    '''
    随机颜色
    '''

    def randon_color(self, begin, end):
        return (random.randint(begin, end), random.randint(begin, end), random.randint(begin, end))

    # 生成图片
    def veri_code(self, width=160, height=40, length=6):
        # 创建image对象
        image = Image.new('RGB', (width, height), (255, 255, 255))
        # 创建font对象
        logging.info('系统路径:'+os.path)
        ttf = '/home/gujie/project/utils/DIY_captcha/fonts/Arial.ttf'
        font = ImageFont.truetype(ttf, 32)
        # 创建画布对象
        draw = ImageDraw.Draw(image)
        '''
        # 随机颜色填充每一个像素
        for x in range(0,width,10):
            for y in range(0,height,10):
                draw.point((x, y), fill=self.randon_color(64, 255))
        '''
        # 验证码
        code = self.randon_code(length)
        logging.info('验证码code:' + code)
        # 随机颜色验证码写到图片上
        for t in range(length):
            draw.text((40 * t + 5, 5), code[t], font=font, fill=self.randon_color(32, 127))
        # 模糊滤镜
        # image = image.filter(ImageFilter.BLUR)

        image.save('/home/yanzhengma.png')

        image_out = open('/home/yanzhengma.png', 'rb')
        image_outs = image_out.read()
        self.write(image_outs)
        self.set_header("Content-Type", "image/png")


