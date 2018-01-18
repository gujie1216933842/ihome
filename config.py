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
    host="47.94.165.75",
    database="ihome",
    user='root',
    password='123',
)

# redis
redis_options = dict(
    host='47.94.165.75',
    port=6379,
)

session_expires = 86400    #session过期时间一天

# 日志配置
log_path = os.path.join(os.path.dirname(__file__), "logs/log")
log_level = "debug"
