# 股票交易录入服务 (StockTrade)

基于 Flask 的股票/基金交易记录管理服务，支持交易录入、批量操作、持仓盈亏计算和实时行情展示。

## 功能特性

- ✅ 交易记录管理（增删改查）
- ✅ 批量修改/删除
- ✅ 股票搜索（按名称/代码）
- ✅ 自动获取实时行情
- ✅ 持仓盈亏计算
- ✅ 券商佣金自动计算
- ✅ 股票K线图表展示
- ✅ 表格排序和分页
- ✅ 数据导出

## 项目结构

```
trade/
├── app/                    # 应用主模块
│   ├── __init__.py        # Flask应用工厂
│   ├── routes.py          # 路由定义
│   ├── models/            # 数据模型
│   │   └── __init__.py
│   ├── services/          # 服务层
│   │   ├── __init__.py
│   │   ├── trade_service.py   # 交易记录服务
│   │   └── stock_service.py   # 股票数据服务
│   └── utils/             # 工具函数
│       └── __init__.py
├── config/                 # 配置目录
│   └── brokers.json       # 券商佣金配置
├── static/                # 静态资源
│   ├── css/
│   │   └── custom.css     # 自定义样式
│   └── js/
│       └── app.js         # 前端脚本
├── templates/             # HTML模板
│   ├── index.html
│   └── detail.html
├── config.py             # 配置文件
├── requirements.txt      # Python依赖
├── run.py               # 应用入口
├── trade_service.py     # 交易服务（原文件，保留兼容）
├── web_app.py           # Web应用（原文件，保留兼容）
└── stock_trades.db      # SQLite数据库
```

## 快速开始

### 1. 安装依赖

```bash
cd trade
pip install -r requirements.txt
```

### 2. 配置券商佣金

编辑 `config/brokers.json` 文件：

```json
[
    {"id": "hx", "name": "华西证券", "rate": 3, "min_fee": 5, "description": "万3，最低5元"}
]
```

### 3. 启动服务

```bash
python run.py
```

或使用原有入口：

```bash
python web_app.py
```

服务启动后访问 http://127.0.0.1:5000

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| FLASK_ENV | 运行环境 | development |
| SECRET_KEY | 应用密钥 | dev-secret-key |

## API接口

### 页面路由

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/submit` | POST | 提交交易 |
| `/detail/<id>` | GET | 查看详情 |
| `/edit/<id>` | GET/POST | 编辑记录 |
| `/delete/<id>` | POST | 删除记录 |
| `/bulk_action` | POST | 批量操作 |

### API接口

| 路由 | 方法 | 说明 |
|------|------|------|
| `/stock_search?name=` | GET | 搜索股票 |
| `/stock_info?stock_code=` | GET | 获取股票信息 |
| `/api/stock/realtime?code=` | GET | 实时行情 |
| `/api/stock/identify?code=` | GET | 识别股票类型 |
| `/api/position/pnl?stock_code=` | GET | 持仓盈亏 |
| `/api/brokers` | GET | 券商列表 |

## 数据库表结构

```sql
CREATE TABLE trade_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_time TIMESTAMP NOT NULL,
    stock_code TEXT,
    stock_name TEXT NOT NULL,
    asset_type TEXT DEFAULT 'stock',
    trade_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    opening_price REAL,
    closing_price REAL,
    high_price REAL,
    low_price REAL,
    trade_price REAL NOT NULL,
    commission_fee REAL DEFAULT 0,
    profit_loss REAL,
    profit_loss_reason TEXT,
    trade_basis TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 技术栈

- **后端**: Flask, SQLite
- **前端**: Bootstrap 5, Vanilla JavaScript
- **数据源**: Baostock, 新浪财经API
- **图表**: Sina Finance K线图

## License

MIT License