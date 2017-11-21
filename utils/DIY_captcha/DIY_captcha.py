from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from handlers.BaseHandler import BaseHandler


class DIY_Verifycode(BaseHandler):
    def get(self):
        self.veri_code(self,160,40)

    '''
    生成随机码
    '''
    def randon_code(self, length=6):
        code = ''
        char = '23456789abcdefghjklmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
        for i in range(length):
            index = random.randint(0, 55)
            code += char[index]

        self.write(code)
    '''
    随机颜色
    '''
    def randon_color(self):
        return (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))

    # 生成图片
    def veri_code(self, width=160, height=40):
        # 创建image对象
        image = Image.new('RBG', (width, height), (255, 255, 0))
        # 创建font对象
        font = ImageFont.truetype('Arial.ttf', 32)
        # 创建画布对象
        draw = ImageDraw.Draw(image)
        # 随机颜色填充每一个像素
        for x in range(width):
            for y in range(height):
                draw.point((x, y), fill=random(64, 255))
        # 验证码
        code = self.randon_code()
        # 随机颜色验证码写到图片上
        for t in range(6):
            draw.text((40 * t + 5, 5), code[t], font=font, fill=self.randon_color())
        # 模糊滤镜
        image = image.filter(ImageFilter.BLUR)
        return code, image
