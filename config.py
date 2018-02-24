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
    host="47.97.165.75",
    database="ihome",
    user='root',
    password='123',
)

# redis
redis_options = dict(
    host='47.97.165.75',
    port=6379,
)

session_expires = 86400    #session过期时间一天

qiniu_url='http://p2yatani0.bkt.clouddn.com/'

# 日志配置
log_path = os.path.join(os.path.dirname(__file__), "logs/log")
log_level = "debug"

HOME_PAGE_MAX_HOUSES = 4

HOME_PAGE_DATA_REDIS_EXPIRE_SECOND = 86400  #首页图片redis有效期
REDIS_AREA_INFO_EXPIRES_SECONDES = 86400   #首页城区信息redis有效期
REDIS_HOUSE_INFO_EXPIRES_SECONDES = 86400  #房屋信息的redis缓存时间
