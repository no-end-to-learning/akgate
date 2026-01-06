# AKGate

akshare REST API 网关 - 将 akshare 金融数据库的功能通过 REST API 暴露出去。

## 功能特性

- 通用 API 端点，支持调用任意 akshare 函数
- 自动将 pandas DataFrame 转换为 JSON 格式
- 支持中文字符和特殊数据类型（日期、NaN 等）
- 可配置的函数白名单安全控制
- 完善的错误处理和日志记录
- 健康检查端点
- Docker 容器化支持

## 快速开始

### 本地运行

```bash
# 安装依赖
pip install .

# 开发环境（默认端口 5000）
FLASK_APP=app flask run

# 生产环境
gunicorn -c gunicorn.conf.py 'app:create_app()'
```

### Docker 运行

```bash
# 使用 Docker Compose
docker compose up -d

# 或直接运行
docker run -p 5000:5000 qiujun8023/akgate
```

## API 使用

### 调用 akshare 函数

```
GET /api/<function_name>?param1=value1&param2=value2
```

示例：

```bash
# 获取股票历史数据
curl "http://localhost:5000/api/stock_zh_a_hist?symbol=000001&start_date=20240101&end_date=20240131"

# 获取 ETF 数据
curl "http://localhost:5000/api/fund_etf_spot_em"
```

### 查看可用函数

```bash
# 当启用白名单时，返回允许的函数列表
curl "http://localhost:5000/api/"
```

### 健康检查

```bash
# 基本健康检查
curl "http://localhost:5000/health"

# 详细健康检查（包含 akshare 版本）
curl "http://localhost:5000/health/detail"
```

## 配置

通过环境变量配置应用：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `FLASK_ENV` | 运行环境 (development/production/testing) | development |
| `ENABLE_FUNCTION_WHITELIST` | 是否启用函数白名单 | false (开发环境) / true (生产环境) |
| `ALLOWED_FUNCTIONS` | 允许的函数列表（逗号分隔） | 内置默认列表 |
| `LOG_LEVEL` | 日志级别 | INFO |

### 生产环境建议

生产环境建议启用函数白名单以增强安全性：

```bash
export FLASK_ENV=production
export ENABLE_FUNCTION_WHITELIST=true
export ALLOWED_FUNCTIONS=stock_zh_a_hist,fund_etf_hist_em,index_zh_a_hist
```

## 项目结构

```
akgate/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── config.py            # 配置管理
│   ├── exceptions.py        # 异常定义和处理
│   ├── logging_config.py    # 日志配置
│   ├── api/                 # API 路由
│   ├── encoder/             # JSON 序列化
│   └── health/              # 健康检查
├── tests/                   # 测试
├── pyproject.toml           # 项目配置和依赖
├── gunicorn.conf.py         # Gunicorn 配置
├── Dockerfile
└── docker-compose.yml
```

## 开发

```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 错误响应

API 错误返回统一的 JSON 格式：

```json
{
  "error": true,
  "error_code": "FUNCTION_NOT_FOUND",
  "message": "Function 'xxx' not found in akshare"
}
```

错误码说明：

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| `FUNCTION_NOT_FOUND` | 404 | 函数不存在 |
| `FUNCTION_NOT_ALLOWED` | 403 | 函数不在白名单中 |
| `INVALID_PARAMETER` | 400 | 参数无效 |
| `DATA_FETCH_ERROR` | 500 | 数据获取失败 |
| `INTERNAL_ERROR` | 500 | 内部服务器错误 |

## 许可证

MIT License
