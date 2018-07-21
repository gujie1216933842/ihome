import os

# Application配置
setting = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'html'),
    'cookie_secret': 'ca/woTXGTRmbgilfRjtsB56tNpLoPUqesEPqHD1L0vE=',
    'xsrf_cookies': True,
    'debug': True,
}

# mysql
mysql_options = dict(
    host="127.0.0.1",
    database="ihome",
    user='root',
    password='123',
)

# redis
redis_options = dict(
    host='127.0.0.1',
    port=6379,
    password='123',
)

session_expires = 864000    #session过期时间一天

qiniu_url='http://p2yatani0.bkt.clouddn.com/'
default_avatar = "FiaSbumysMdx89r9rzxdNjDPfuvh" #新用户有一个默认头像

# 日志配置
log_path = os.path.join(os.path.dirname(__file__), "logs/log")
log_level = "debug"


