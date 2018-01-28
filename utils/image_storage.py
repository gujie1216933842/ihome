# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_data, etag, urlsafe_base64_encode
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'dew-f9QHC7lN7bw8tC02mIiGKQdGXqIcbJMexfCC'
secret_key = '6jrHizN6Gkcz-6b4eQdufitGu8GiCvA8zoyHipYu'


def storage(image_data):
    # 构建对象
    if not image_data:
        # print(1)
        return None
    # 构建鉴权对象
    # print(2)
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome'

    # 上传到七牛后保存的文件名
    # key = 'my-python-logo.png';

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    # 要上传文件的本地路径
    # localfile = './sync/bbb.jpg'

    ret, info = put_data(token, None, image_data)
    # print(info)
    # assert ret['key'] == key     python中的断言语法,可以注释掉
    # assert ret['hash'] == etag(image_data)
    return ret['key']

if __name__ == '__main__':
    file_name = input("请输入图片路径+图片名:")
    file = open(file_name, 'rb')
    file_data = file.read()
    key = storage(file_data)
    print(key)

