"""
Gunicorn 配置文件

使用方法: gunicorn -c gunicorn.conf.py 'app:create_app()'
"""
import os

# 绑定地址
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:5000')

# 工作进程数：请求量极小，1 个进程足够
workers = 1

# 超时时间（秒）
timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))

# 优雅重启超时
graceful_timeout = 30


# 日志配置
accesslog = '-'  # 输出到 stdout
errorlog = '-'   # 输出到 stderr
loglevel = os.getenv('LOG_LEVEL', 'info').lower()

# 进程名
proc_name = 'akgate'

