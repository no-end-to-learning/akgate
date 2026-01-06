"""
Gunicorn 配置文件

使用方法: gunicorn -c gunicorn.conf.py 'app:create_app()'
"""
import multiprocessing
import os

# 绑定地址
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:5000')

# 工作进程数
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# 每个工作进程的线程数
threads = int(os.getenv('GUNICORN_THREADS', 4))

# 工作模式
worker_class = 'gthread'

# 超时时间（秒）
timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))

# 优雅重启超时
graceful_timeout = 30

# 保持连接时间
keepalive = 5

# 最大请求数（之后工作进程会重启）
max_requests = 1000
max_requests_jitter = 100

# 日志配置
accesslog = '-'  # 输出到 stdout
errorlog = '-'   # 输出到 stderr
loglevel = os.getenv('LOG_LEVEL', 'info').lower()

# 进程名
proc_name = 'akgate'

# 预加载应用（节省内存）
preload_app = True
