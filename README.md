# 股票交易管理系统

基于 Vue3 + Flask 的前后端分离股票交易记录管理系统。

## 功能特性

- [x] 总览页面 - 显示总资产、市值、盈亏等关键指标
- [x] 持仓管理 - 股票持仓查询和管理
- [x] 股票搜索 - 按代码或名称搜索股票
- [x] 买入/卖出 - 支持买卖操作，自动计算佣金
- [x] 交易记录 - 完整的交易历史记录
- [x] K线图表 - 支持分时、日K、周K、月K等多周期图表
- [x] 券商管理 - 灵活配置不同券商佣金
- [x] 技术指标 - MA、MACD、KDJ、布林带等指标

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue3 + Vite | 现代前端框架 |
| UI | Element Plus | 企业级UI组件库 |
| 图表 | ECharts | 数据可视化 |
| 状态 | Pinia | Vue3状态管理 |
| 后端 | Flask | 轻量级Python Web框架 |
| ORM | SQLAlchemy | 数据库ORM |
| 数据库 | PostgreSQL | 关系型数据库 |

## 项目结构

```
stockTrade/
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── models/                   # 数据模型
│   │   │   └── __init__.py          # Broker, Position, TradeRecord, StockPrice
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── broker_service.py    # 券商服务
│   │   │   ├── position_service.py  # 持仓服务
│   │   │   ├── stock_service.py      # 股票行情服务
│   │   │   └── trade_service.py     # 交易服务
│   │   ├── routes/                   # API路由
│   │   │   └── __init__.py          # 所有REST API
│   │   └── utils/                    # 工具函数
│   ├── config/                       # 配置
│   ├── requirements.txt              # Python依赖
│   └── run.py                        # 启动入口
│
├── frontend/                         # 前端应用
│   ├── src/
│   │   ├── api/                      # API调用封装
│   │   ├── components/               # Vue组件
│   │   │   ├── PortfolioSummary.vue # 总览卡片
│   │   │   ├── PositionList.vue     # 持仓列表
│   │   │   └── TradeDialog.vue       # 交易弹窗
│   │   ├── views/                   # 页面视图
│   │   │   ├── Dashboard.vue         # 总览页面
│   │   │   ├── Positions.vue        # 持仓页面
│   │   │   ├── Stocks.vue           # 股票搜索
│   │   │   ├── Trades.vue          # 交易记录
│   │   │   ├── StockDetail.vue      # 股票详情
│   │   │   ├── BrokerSettings.vue   # 券商管理
│   │   │   └── IndicatorSettings.vue # 指标设置
│   │   ├── store/                   # Pinia状态管理
│   │   ├── router/                  # 路由配置
│   │   ├── styles/                  # 全局样式
│   │   └── utils/                  # 工具函数
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 后端安装

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 创建数据库
createdb stock_trade

# 启动服务
python run.py
```

后端服务地址: http://localhost:5000

### 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务地址: http://localhost:3000

## API 接口

### 组合总览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/portfolio/summary` | GET | 获取组合总览 |

### 持仓管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/positions` | GET | 获取持仓列表 |
| `/api/positions/:code` | GET | 获取指定持仓 |
| `/api/positions/:code/cost-detail` | GET | 获取成本明细 |

### 交易操作

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/trades/buy` | POST | 买入股票 |
| `/api/trades/sell` | POST | 卖出股票 |
| `/api/trades` | GET | 获取交易记录 |

### 股票行情

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/stocks/search` | GET | 搜索股票 |
| `/api/stocks/:code/realtime` | GET | 获取实时行情 |
| `/api/stocks/:code/kline` | GET | 获取K线数据 |

### 券商管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/brokers` | GET | 获取券商列表 |
| `/api/brokers` | POST | 创建券商 |
| `/api/brokers/:id` | PUT | 更新券商 |

### 费用计算

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/calculator/fee` | POST | 计算交易费用 |

## 数据库表

### Broker 券商表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| name | VARCHAR(50) | 券商名称 |
| buy_commission_rate | NUMERIC | 买入佣金率 |
| sell_commission_rate | NUMERIC | 卖出佣金率 |
| min_commission | NUMERIC | 最低佣金 |

### Position 持仓表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| stock_code | VARCHAR(10) | 股票代码 |
| stock_name | VARCHAR(100) | 股票名称 |
| total_quantity | INTEGER | 持股数量 |
| avg_cost | NUMERIC | 持仓成本 |
| unrealized_pnl | NUMERIC | 未实现盈亏 |

### TradeRecord 交易记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| trade_type | VARCHAR(10) | buy/sell |
| quantity | INTEGER | 数量 |
| unit_price | NUMERIC | 单价 |
| commission | NUMERIC | 佣金 |
| stamp_tax | NUMERIC | 印花税 |

## 佣金计算规则

```python
# 买入佣金
commission = max(amount × rate / 10000, min_fee)

# 卖出费用
total_fee = commission + stamp_tax
stamp_tax = amount × 0.0005  # 印花税减半
```

## 开发指南

### 添加新的API

1. 在 `backend/app/services/` 添加业务逻辑
2. 在 `backend/app/routes/__init__.py` 添加路由
3. 在 `frontend/src/api/index.js` 添加API调用
4. 创建或更新Vue组件

### 添加新的页面

1. 在 `frontend/src/views/` 创建Vue组件
2. 在 `frontend/src/router/index.js` 添加路由配置
3. 在 `frontend/src/App.vue` 添加菜单项

## 许可证

MIT License