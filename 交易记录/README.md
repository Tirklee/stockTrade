# 股票交易记录系统

## 项目概述

这是一个基于SQLite的股票交易记录管理系统，用于完整记录股票交易的各个环节，包括买入/卖出信息、盈亏统计等。

## 数据库表结构

### trade_records 表

| 字段名 | 类型 | 说明 | 必填 |
|--------|------|------|------|
| id | INTEGER | 记录ID（主键）| 是 |
| trade_time | TIMESTAMP | 交易时间 | 是 |
| stock_code | TEXT | 股票代码 | 是 |
| stock_name | TEXT | 股票名称 | 是 |
| trade_type | TEXT | 交易类型 (buy/sell) | 是 |
| quantity | INTEGER | 交易数量 | 是 |
| opening_price | REAL | 开盘价 | 否 |
| closing_price | REAL | 收盘价 | 否 |
| trade_price | REAL | 交易价格 | 是 |
| commission_fee | REAL | 交易手续费 | 是 |
| profit_loss | REAL | 盈亏金额 | 否 |
| profit_loss_reason | TEXT | 盈亏原因 | 否 |
| trade_basis | TEXT | 交易依据/理由 | 是 |
| created_at | TIMESTAMP | 创建时间 | 否 |
| updated_at | TIMESTAMP | 更新时间 | 否 |

## 主要函数

### 1. init_database()
初始化数据库和创建交易记录表

```python
init_database()
```

### 2. add_trade_record()
添加交易记录

```python
add_trade_record(
    stock_code: str,           # 股票代码
    stock_name: str,           # 股票名称
    trade_type: str,           # 交易类型 ('buy' 或 'sell')
    quantity: int,             # 交易数量
    trade_price: float,        # 交易价格
    commission_fee: float,     # 交易手续费
    trade_basis: str,          # 交易依据
    trade_time: Optional[str], # 交易时间 (默认为当前时间)
    opening_price: Optional[float],     # 开盘价
    closing_price: Optional[float],     # 收盘价
    profit_loss: Optional[float],       # 盈亏金额
    profit_loss_reason: Optional[str]   # 盈亏原因
) -> int  # 返回记录ID
```

**示例：**
```python
record_id = add_trade_record(
    stock_code='600000',
    stock_name='浦发银行',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='技术面突破，量能配合',
    opening_price=10.40,
    closing_price=10.60
)
```

### 3. get_all_records()
获取所有或指定股票的交易记录

```python
get_all_records(stock_code: Optional[str] = None) -> pd.DataFrame
```

**参数：**
- `stock_code`: 股票代码（可选，不指定则返回所有记录）

**返回：** pandas DataFrame 格式的交易记录

**示例：**
```python
# 获取所有记录
all_records = get_all_records()

# 获取特定股票的记录
pfyh_records = get_all_records('600000')
print(pfyh_records)
```

### 4. get_stock_summary()
获取指定股票的交易汇总统计

```python
get_stock_summary(stock_code: str) -> Dict
```

**返回值字典包含：**
- `stock_code`: 股票代码
- `stock_name`: 股票名称
- `total_trades`: 总交易次数
- `buy_count`: 买入次数
- `sell_count`: 卖出次数
- `total_buy_quantity`: 总买入数量
- `total_sell_quantity`: 总卖出数量
- `total_commission`: 总手续费
- `total_profit_loss`: 总盈亏

**示例：**
```python
summary = get_stock_summary('600000')
for key, value in summary.items():
    print(f"{key}: {value}")
```

### 5. update_profit_loss()
更新交易记录的盈亏信息

```python
update_profit_loss(
    record_id: int,
    profit_loss: float,
    reason: str = ""
)
```

**示例：**
```python
update_profit_loss(
    record_id=1,
    profit_loss=150.50,
    reason='目标位获利出场'
)
```

### 6. delete_record()
删除指定的交易记录

```python
delete_record(record_id: int)
```

**示例：**
```python
delete_record(1)
```

## 使用流程

### 第一步：初始化数据库
在首次使用时，运行初始化函数创建数据库和表：
```python
init_database()
```

### 第二步：添加交易记录
每次交易后，使用 `add_trade_record()` 函数记录交易信息：
```python
# 记录买入
buy_id = add_trade_record(
    stock_code='000001',
    stock_name='平安银行',
    trade_type='buy',
    quantity=200,
    trade_price=9.80,
    commission_fee=3.92,
    trade_basis='底部支撑，技术反弹'
)

# 记录卖出（可后续更新盈亏信息）
sell_id = add_trade_record(
    stock_code='000001',
    stock_name='平安银行',
    trade_type='sell',
    quantity=200,
    trade_price=10.20,
    commission_fee=4.08,
    trade_basis='压力位获利'
)
```

### 第三步：查询和分析
使用查询函数查看交易记录和统计信息：
```python
# 查看所有记录
all_trades = get_all_records()

# 查看特定股票的记录
pfyh_trades = get_all_records('600000')

# 获取统计汇总
summary = get_stock_summary('000001')
```

### 第四步：更新盈亏信息（可选）
如果初始添加时未记录盈亏，可后续更新：
```python
update_profit_loss(
    record_id=sell_id,
    profit_loss=75.0,  # 盈利75元
    reason='成功止盈'
)
```

## 文件位置

- **数据库文件**：`stock_trades.db`（自动创建在运行脚本的同目录）
- **Notebook文件**：`T20260512.ipynb`

## 注意事项

1. **股票代码**：建议使用标准的股票代码格式（如：600000）
2. **交易类型**：仅支持 `'buy'` 和 `'sell'` 两种（不区分大小写）
3. **手续费**：根据您的实际交易费用计算
4. **盈亏计算**：可以在添加记录时填写，也可以在后续更新
5. **时间格式**：如不指定交易时间，将自动使用当前时间（ISO 8601 格式）

## 示例输出

添加记录后的表格显示：

```
   id                  trade_time stock_code stock_name trade_type  quantity  opening_price  closing_price  trade_price  commission_fee  profit_loss profit_loss_reason trade_basis
0   2  2026-05-13T17:43:32.431174     600000       浦发银行       sell        50           11.0          11.15         11.2            2.80        30.95       突破目标压力位，获利出场  达到目标价，止盈出场
1   1  2026-05-13T17:43:32.429986     600000       浦发银行        buy       100           10.4          10.60         10.5            5.25          NaN                NaN  技术面突破，量能配合
```

统计汇总输出：

```
stock_code: 600000
stock_name: 浦发银行
total_trades: 2
buy_count: 1
sell_count: 1
total_buy_quantity: 100
total_sell_quantity: 50
total_commission: 8.05
total_profit_loss: 30.95
```

## AKshare 集成功能

### 什么是 AKshare？
AKshare 是一个开源的中国金融数据库，提供股票实时行情、历史数据、财务数据等。

### 获取实时股票信息

**函数：** `get_stock_info(stock_code: str) -> Dict`

```python
# 获取浦发银行的实时信息
info = get_stock_info('600000')
# 返回: {
#   'stock_code': 'sh600000',
#   'stock_name': '浦发银行',
#   'current_price': 10.50,
#   'opening_price': 10.40,
#   'highest_price': 10.60,
#   'lowest_price': 10.30,
#   'closing_price': 10.45,
#   'volume': 12345600,
#   'turnover': 123456789.0,
#   'price_change': 0.05,
#   'price_change_pct': 0.48
# }
```

### 获取日线数据

**函数：** `get_stock_daily(stock_code: str, period: str = '100') -> pd.DataFrame`

```python
# 获取浦发银行最近30天的日线数据
daily_data = get_stock_daily('600000', period='30')
# 返回包含以下列的DataFrame:
# date, open, close, high, low, volume, turnover, amplitude, 
# change_pct, change_amount, turnover_rate
```

### 自动添加带市场数据的交易记录

**函数：** `add_trade_with_market_data(...) -> int`

此函数会自动从 AKshare 获取当前的开盘价和收盘价，然后添加交易记录：

```python
# 添加交易，自动获取市场数据
record_id = add_trade_with_market_data(
    stock_code='600000',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='技术面突破'
)
```

### 获取股票列表

**函数：** `get_stock_list() -> pd.DataFrame`

```python
# 获取所有A股股票的代码和名称
stock_list = get_stock_list()
print(stock_list)  # 显示所有股票
```

## 网络连接说明

- **在线模式**：当网络正常时，系统会自动从 AKshare 获取实时数据
- **离线模式**：当网络不可用时，系统会自动降级到离线模式，仍可继续记录交易
- **自动重试**：网络请求失败时，系统会自动重试最多 3 次

**注意：** AKshare 数据源依赖于网络连接。如果中国大陆无法直接连接，可能需要配置代理或使用其他数据源。

## 扩展功能建议

- 添加持仓管理功能
- 按时间段统计收益率
- 添加止损/止盈提醒
- 导出报表功能
- 交易策略分类统计
- 集成其他数据源（如 tushare、wind 等）
