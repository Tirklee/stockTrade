# 快速参考指南

## 导入和初始化

```python
# 初始化数据库（第一次使用）
init_database()
```

## 核心功能：添加交易记录

### 简单方式（离线）
无需网络连接，直接记录交易：

```python
# 记录买入
buy_id = add_trade_record(
    stock_code='600000',
    stock_name='浦发银行',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='技术面突破'
)

# 记录卖出
sell_id = add_trade_record(
    stock_code='600000',
    stock_name='浦发银行',
    trade_type='sell',
    quantity=100,
    trade_price=11.20,
    commission_fee=2.80,
    trade_basis='目标位获利',
    profit_loss=30.95,
    profit_loss_reason='成功止盈'
)
```

### 自动方式（使用 AKshare 获取实时数据）
使用 AKshare 自动获取开盘价和收盘价：

```python
# 添加交易并自动获取市场数据
record_id = add_trade_with_market_data(
    stock_code='600000',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='技术分析'
)
```

## AKshare 股票数据查询

### 获取实时股票信息
```python
info = get_stock_info('600000')
print(f"当前价: {info['current_price']}")
print(f"涨跌幅: {info['price_change_pct']}%")
```

### 获取日线行情
```python
# 获取最近 30 天的日线数据
daily_df = get_stock_daily('600000', period='30')
print(daily_df[['date', 'open', 'close', 'volume']])
```

### 获取股票列表
```python
# 获取所有 A 股的代码和名称
stocks = get_stock_list()
print(stocks)
```

## 常用操作

### 查看所有交易记录
```python
all_records = get_all_records()
print(all_records)
```

### 查看特定股票的记录
```python
records = get_all_records('600000')
print(records)
```

### 查看股票统计汇总
```python
summary = get_stock_summary('600000')
print(summary)
```

## 更新操作

### 更新盈亏信息
```python
update_profit_loss(
    record_id=1,
    profit_loss=150.50,
    reason='目标位获利出场'
)
```

### 删除交易记录
```python
delete_record(record_id=1)
```

## 实际例子

### 例子1：完整的买卖流程（带实时数据）
```python
# 1. 购买 100 股浦发银行（自动获取市场数据）
buy_id = add_trade_with_market_data(
    stock_code='600000',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='技术突破 + AKshare 数据确认'
)

# 2. 卖出 50 股
sell_id = add_trade_with_market_data(
    stock_code='600000',
    trade_type='sell',
    quantity=50,
    trade_price=11.20,
    commission_fee=2.80,
    trade_basis='达到目标价格'
)

# 3. 查看该股票的所有交易
df = get_all_records('600000')
print(df)

# 4. 查看统计汇总
summary = get_stock_summary('600000')
print(summary)
```

### 例子2：查询市场数据后手动交易记录
```python
# 1. 查询浦发银行的实时数据
pfyh_info = get_stock_info('600000')
print(f"浦发银行当前价: {pfyh_info['current_price']}")
print(f"今日涨幅: {pfyh_info['price_change_pct']}%")

# 2. 查询最近 10 天的日线
daily = get_stock_daily('600000', period='10')
print(daily)

# 3. 根据数据决定交易
if pfyh_info['price_change_pct'] > 0:
    add_trade_record(
        stock_code='600000',
        stock_name='浦发银行',
        trade_type='buy',
        quantity=100,
        trade_price=pfyh_info['current_price'],
        commission_fee=5.0,
        trade_basis='技术面利好'
    )
```

### 例子3：多股票批量交易
```python
# 交易 A 股
add_trade_record('000001', '平安银行', 'buy', 200, 9.80, 3.92, '底部反弹')
add_trade_record('000001', '平安银行', 'sell', 200, 10.20, 4.08, '压力位获利')

# 交易 B 股
add_trade_record('000333', '美的集团', 'buy', 50, 25.50, 6.37, '利好消息')
add_trade_record('000333', '美的集团', 'sell', 50, 26.80, 6.70, '减仓止盈')

# 查看各股票统计
for stock_code in ['000001', '000333']:
    summary = get_stock_summary(stock_code)
    if summary:
        print(f"\n{stock_code} 统计信息:")
        print(f"  总交易次数: {summary['total_trades']}")
        print(f"  总盈亏: {summary['total_profit_loss']}")
```

## 常见问题

**Q: 如何修改已添加的交易记录？**
A: 目前可以通过 `update_profit_loss()` 更新盈亏信息，或使用 `delete_record()` 删除后重新添加。

**Q: AKshare 需要网络连接吗？**
A: 是的，获取实时数据需要网络。离线模式下可继续添加交易记录。

**Q: 网络不可用时会怎样？**
A: 系统会自动重试，失败后降级为离线模式，可继续记录交易。

**Q: 如何导出数据？**
A: 使用 `get_all_records()` 返回的 DataFrame：
```python
df = get_all_records()
df.to_csv('交易记录.csv', index=False)
df.to_excel('交易记录.xlsx', index=False)
```

**Q: 如何查询特定时间段的交易？**
A: 使用 DataFrame 的过滤功能：
```python
df = get_all_records('600000')
df['trade_time'] = pd.to_datetime(df['trade_time'])
recent_trades = df[df['trade_time'] > '2026-05-01']
print(recent_trades)
```
