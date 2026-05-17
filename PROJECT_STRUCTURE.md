# 股票交易管理系统 - 项目结构

## 目录结构

```
stockTrade/                     # 项目根目录
├── app/                        # 应用主模块
│   ├── __init__.py           # Flask应用工厂（创建应用实例，注册蓝图和过滤器）
│   ├── config.py              # 配置管理模块（统一管理所有配置项）
│   ├── database.py            # 数据库管理模块（初始化、连接管理、备份）
│   ├── logging_config.py      # 日志配置模块（统一管理日志输出）
│   ├── routes.py              # 路由定义（所有API端点和页面路由）
│   ├── models/                # 数据模型目录（预留）
│   │   └── __init__.py
│   ├── services/              # 服务层目录
│   │   ├── trade_service.py   # 交易记录服务（增删改查、持仓计算）
│   │   └── stock_service.py  # 股票数据服务（行情获取、搜索）
│   └── utils/                 # 工具函数目录（预留）
│       └── __init__.py
├── config/                     # 配置目录
│   └── brokers.json          # 券商佣金配置（JSON格式数组）
├── static/                    # 静态资源目录
│   ├── css/
│   │   ├── bootstrap.min.css  # Bootstrap CSS
│   │   └── custom.css         # 自定义样式
│   └── js/
│       ├── bootstrap.bundle.min.js  # Bootstrap JS
│       └── app.js             # 应用JavaScript
├── templates/                # HTML模板目录
│   ├── index.html            # 首页模板
│   ├── detail.html           # 详情页模板
│   └── add.html              # 添加记录模板（预留）
├── tests/                    # 测试目录
│   ├── __init__.py
│   ├── conftest.py           # pytest配置和fixtures
│   └── test_trade_service.py # 交易服务单元测试
├── init_project.py           # 项目初始化脚本
├── run.py                    # 应用入口文件
├── requirements.txt          # Python依赖清单
├── ENGINEERING_PLAN.md       # 工程化改造文档
├── BUGFIX_SUMMARY.md         # Bug修复记录
├── DEVELOPMENT_GUIDELINES.md # 开发指南
├── PROJECT_SUMMARY.md        # 项目总结
├── QUICK_GUIDE.md            # 快速入门
└── stock_trades.db           # SQLite数据库
```

## 核心文件说明

### app/__init__.py
Flask应用工厂，负责：
- 创建Flask应用实例
- 配置模板和静态文件路径
- 注册自定义Jinja2过滤器（如 `decimal3`）
- 注册蓝图

### app/config.py
统一配置管理，包含：
- 数据库路径配置
- 分页配置
- API超时配置
- 日志配置
- 默认券商配置

### app/database.py
数据库管理模块，提供：
- `init_database()` - 初始化数据库表
- `get_db_connection()` - 数据库连接上下文管理器
- `get_database_info()` - 获取数据库信息
- `backup_database()` - 数据库备份

### app/routes.py
所有路由定义，包括：
- 页面路由（首页、详情页等）
- API路由（股票搜索、实时行情、持仓盈亏等）
- CRUD操作路由（增删改查）

### app/services/trade_service.py
交易记录服务，提供：
- `get_trades()` - 获取交易记录列表
- `add_trade()` - 添加交易记录
- `update_trade()` - 更新交易记录
- `delete_trade()` - 删除交易记录
- `calculate_position_pnl()` - 计算持仓盈亏
- `calculate_portfolio_summary()` - 计算总账户盈亏

### app/services/stock_service.py
股票数据服务，提供：
- `get_stock_info()` - 获取股票信息
- `get_realtime_data()` - 获取实时行情
- `identify_stock_type()` - 识别股票类型
- `search_stocks()` - 搜索股票

## 已删除的冗余文件

以下文件已在工程化过程中删除：
- ❌ `trade_service.py` - 功能已迁移到 `app/services/trade_service.py`
- ❌ `web_app.py` - 功能已迁移到 `app/routes.py`
- ❌ `config.py` - 功能已迁移到 `app/config.py`
- ❌ `migrate_to_three_tables.py` - 迁移脚本（已完成迁移）
- ❌ `static/js/app_backup.js` - 备份文件
- ❌ `static/js/app_temp.js` - 临时文件
- ❌ `__pycache__/` - Python缓存目录
- ❌ `trade/` 子目录 - 已将所有文件移动到根目录

## 启动方式

### 方式1：直接启动
```bash
python run.py
```

### 方式2：初始化后启动
```bash
python init_project.py  # 初始化项目和数据库
python run.py            # 启动服务
```

### 方式3：运行测试
```bash
pytest tests/ -v
```

## 访问地址

- 本地访问：http://127.0.0.1:5000
- 局域网访问：http://<IP地址>:5000

## 技术栈

- **后端**：Flask 2.0+
- **数据库**：SQLite
- **数据源**：Baostock、新浪财经API
- **前端**：Bootstrap 5、Vanilla JavaScript
- **测试**：pytest