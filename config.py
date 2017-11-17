import os

# Application配置
setting = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'html'),
    'cookie_secret': 'ca/woTXGTRmbgilfRjtsB56tNpLoPUqesEPqHD1L0vE=',
    'xsrf_cookies': '+IMtKSeQQTi7YjIOl/oZjXopKd16E0erj9Llvbp7KQQ=',
    'debug': True,
}

# mysql
mysql_options = dict(
    host="192.168.116.128",
    database="ihome",
    user='root',
    password='123',
)

# redis
redis_options = dict(
    host='192.168.116.128',
    port=6379,
)

# 日志配置
log_path = os.path.join(os.path.dirname(__file__), "logs/log")
log_level = "debug"
