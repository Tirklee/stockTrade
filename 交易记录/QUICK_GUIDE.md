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

### 自动方式（使用 Baostock/新浪获取实时数据）
自动获取开盘价和收盘价：

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

## 股票数据查询

### 获取实时股票信息
```python
info = get_stock_info('600000')
print(f"当前价: {info.get('current_price', info.get('closing_price'))}")
print(f"涨跌幅: {info['price_change_pct']}%")
```

## 常用操作

### 查看所有交易记录
```python
all_records = query_records()
print(all_records)
```

### 查看特定股票的记录
```python
records = query_records(stock_code='600000')
print(records)
```

### 分页查询
```python
# 第1页，每页20条
page1 = query_records(page=1, per_page=20)
# 第2页
page2 = query_records(page=2, per_page=20)
```

### 查看股票统计汇总
```python
summary = get_stock_summary('600000')
print(summary)
```

## 更新操作

### 更新交易记录
```python
update_trade_record(
    record_id=1,
    profit_loss=150.50,
    profit_loss_reason='目标位获利出场'
)
```

### 删除交易记录
```python
delete_trade_record(record_id=1)
```

### 批量删除
```python
deleted = bulk_delete_records([1, 2, 3])
print(f"删除了 {deleted} 条记录")
```

### 批量更新
```python
updated = bulk_update_records(
    record_ids=[1, 2, 3],
    trade_basis='批量更新交易依据'
)
print(f"更新了 {updated} 条记录")
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
    trade_basis='技术突破 + 市场数据确认'
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
records = query_records(stock_code='600000')
print(records)

# 4. 查看统计汇总
summary = get_stock_summary('600000')
print(summary)
```

### 例子2：查询市场数据后手动交易记录
```python
# 1. 查询浦发银行的实时数据
pfyh_info = get_stock_info('600000')
print(f"浦发银行当前价: {pfyh_info.get('current_price', pfyh_info.get('closing_price'))}")
print(f"今日涨幅: {pfyh_info['price_change_pct']}%")

# 2. 根据数据决定交易
price = pfyh_info.get('current_price', pfyh_info.get('closing_price'))
if pfyh_info['price_change_pct'] > 0:
    add_trade_record(
        stock_code='600000',
        stock_name='浦发银行',
        trade_type='buy',
        quantity=100,
        trade_price=price,
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
A: 使用 `update_trade_record()` 更新记录，或使用 `delete_trade_record()` 删除后重新添加。

**Q: 获取实时数据需要网络连接吗？**
A: 是的，获取实时数据需要网络。离线模式下可继续添加交易记录。

**Q: 网络不可用时会怎样？**
A: 系统会自动切换数据源，失败后降级为离线模式，可继续记录交易。

**Q: 如何导出数据？**
A: 使用 `query_records()` 返回的列表：
```python
import csv
records = query_records()
with open('交易记录.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=records[0].keys() if records else [])
    writer.writeheader()
    writer.writerows(records)
```

**Q: 如何查询特定时间段的交易？**
A: 使用列表的过滤功能：
```python
from datetime import datetime
records = query_records(stock_code='600000')
recent = [r for r in records if r['trade_time'] >= '2026-05-01']
print(recent)