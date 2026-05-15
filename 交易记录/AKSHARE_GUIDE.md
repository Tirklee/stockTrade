# AKshare 股票数据获取模块使用指南

## 简介

AKshare 是一个开源的中国金融数据获取库，提供股票实时行情、历史数据、财务指标等丰富的金融数据。本项目已集成 AKshare，实现了以下功能：

- 📊 获取股票实时行情数据
- 📈 获取股票日线行情数据  
- 📋 自动查询股票信息
- 🔄 自动添加交易记录并填充市场数据

## 核心函数

### 1. get_stock_info(stock_code: str) -> Dict
获取指定股票的**实时基本信息**。

**参数：**
- `stock_code`: 股票代码，格式可以是 '600000' 或 'sh600000'

**返回值：**
```python
{
    'stock_code': 'sh600000',        # 股票代码（带市场标识）
    'stock_name': '浦发银行',         # 股票名称
    'current_price': 10.50,          # 最新价格
    'opening_price': 10.40,          # 今日开盘价
    'highest_price': 10.60,          # 今日最高价
    'lowest_price': 10.30,           # 今日最低价
    'closing_price': 10.45,          # 昨日收盘价
    'volume': 12345600,              # 成交量（股数）
    'turnover': 123456789.0,         # 成交额（元）
    'price_change': 0.05,            # 涨跌额
    'price_change_pct': 0.48         # 涨跌幅（%）
}
```

**示例：**
```python
info = get_stock_info('600000')
print(f"浦发银行最新价: {info['current_price']}")
print(f"今日涨幅: {info['price_change_pct']}%")
```

### 2. get_stock_daily(stock_code: str, period: str = '100') -> pd.DataFrame
获取股票的**日线历史行情数据**。

**参数：**
- `stock_code`: 股票代码
- `period`: 获取数据的天数（默认100天）

**返回列：**
| 列名 | 说明 |
|-----|------|
| date | 交易日期 |
| open | 开盘价 |
| close | 收盘价 |
| high | 最高价 |
| low | 最低价 |
| volume | 成交量 |
| turnover | 成交额 |
| amplitude | 振幅（%） |
| change_pct | 涨跌幅（%） |
| change_amount | 涨跌额 |
| turnover_rate | 换手率（%） |

**示例：**
```python
# 获取最近 30 天的日线数据
daily_df = get_stock_daily('600000', period='30')
print(daily_df)

# 只显示指定列
print(daily_df[['date', 'close', 'volume']])

# 查看涨跌最大的三天
top_changes = daily_df.nlargest(3, 'change_amount')
print(top_changes)
```

### 3. get_stock_list() -> pd.DataFrame
获取所有**A股股票的列表**（包含代码和名称）。

**返回列：**
| 列名 | 说明 |
|-----|------|
| 代码 | 股票代码 |
| 名称 | 股票名称 |

**示例：**
```python
stocks = get_stock_list()
print(f"总共有 {len(stocks)} 只股票")

# 查找特定股票
pfyh = stocks[stocks['名称'] == '浦发银行']
print(pfyh)

# 查找包含"银行"的股票
banks = stocks[stocks['名称'].str.contains('银行')]
print(banks)
```

### 4. add_trade_with_market_data(...) -> int
添加交易记录，**自动从 AKshare 获取实时市场数据**。

**参数：**
```python
record_id = add_trade_with_market_data(
    stock_code: str,           # 股票代码（必填）
    trade_type: str,           # 交易类型：'buy' 或 'sell'（必填）
    quantity: int,             # 交易数量（必填）
    trade_price: float,        # 交易价格（必填）
    commission_fee: float,     # 交易手续费（必填）
    trade_basis: str,          # 交易依据（必填）
    stock_name: Optional[str]  # 股票名称（可选，会自动获取）
) -> int
```

**返回值：**
- 成功：交易记录的 ID（正整数）
- 失败：-1

**特点：**
- 自动从 AKshare 获取股票名称、开盘价、当前价格
- 网络失败时自动重试
- 若网络不可用，可手动提供股票名称继续记录

**示例：**
```python
# 自动获取市场数据并添加交易
record_id = add_trade_with_market_data(
    stock_code='600000',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='技术面突破'
)
print(f"交易已记录，ID: {record_id}")
```

## 使用场景

### 场景 1：查看股票实时行情后再决定交易

```python
# 1. 查看实时数据
info = get_stock_info('600000')
if info['price_change_pct'] > 2:  # 涨幅大于 2%
    print(f"浦发银行涨幅 {info['price_change_pct']}%，考虑买入")
    
    # 2. 决定交易
    add_trade_with_market_data(
        stock_code='600000',
        trade_type='buy',
        quantity=100,
        trade_price=info['current_price'],
        commission_fee=5.0,
        trade_basis='涨幅超过 2%，技术面看好'
    )
```

### 场景 2：分析股票技术走势再交易

```python
# 1. 获取 20 天日线数据
daily = get_stock_daily('600000', period='20')

# 2. 计算均线
daily['ma5'] = daily['close'].rolling(5).mean()
daily['ma10'] = daily['close'].rolling(10).mean()

# 3. 如果短期均线上穿长期均线，则买入
if daily.iloc[-1]['ma5'] > daily.iloc[-1]['ma10']:
    print("5日线上穿10日线，出现金叉信号")
    
    # 4. 执行交易
    add_trade_with_market_data(
        stock_code='600000',
        trade_type='buy',
        quantity=100,
        trade_price=daily.iloc[-1]['close'],
        commission_fee=5.0,
        trade_basis='5日线上穿10日线形成金叉'
    )
```

### 场景 3：批量查询多只股票

```python
# 1. 获取关注的股票列表
watch_list = ['600000', '000001', '000333']

# 2. 逐个查询
for code in watch_list:
    info = get_stock_info(code)
    if info:
        print(f"{info['stock_name']}({code}): {info['current_price']:.2f} "
              f"({info['price_change_pct']:+.2f}%)")
    else:
        print(f"获取 {code} 信息失败")

# 3. 根据涨幅购买
for code in watch_list:
    info = get_stock_info(code)
    if info and info['price_change_pct'] < -3:  # 下跌超过 3%
        print(f"{info['stock_name']} 下跌 {info['price_change_pct']}%，反弹买入")
        add_trade_with_market_data(
            stock_code=code,
            trade_type='buy',
            quantity=100,
            trade_price=info['current_price'],
            commission_fee=5.0,
            trade_basis='超跌反弹'
        )
```

### 场景 4：导出交易分析报告

```python
# 1. 获取所有交易记录
all_trades = get_all_records()

# 2. 按股票分组统计
by_stock = all_trades.groupby('stock_code').agg({
    'quantity': 'sum',
    'profit_loss': 'sum',
    'commission_fee': 'sum'
})

print("按股票统计:")
print(by_stock)

# 3. 导出为 CSV
all_trades.to_csv('all_trades.csv', index=False)
```

## 网络连接处理

### 自动重试机制
- `get_stock_info()` 会在网络失败时自动重试最多 3 次
- 每次重试会输出进度提示

### 降级到离线模式
若网络不可用，`add_trade_with_market_data()` 会：
1. 首先尝试从 AKshare 获取数据
2. 若失败且提供了 `stock_name`，则直接使用该名称记录交易
3. 若未提供 `stock_name`，则返回 -1 表示失败

示例：
```python
# 网络可用时，自动获取数据
record_id = add_trade_with_market_data(
    stock_code='600000',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='买入理由'
)

# 网络不可用时，手动提供股票名称
record_id = add_trade_with_market_data(
    stock_code='600000',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='买入理由',
    stock_name='浦发银行'  # 手动指定
)
```

## 数据更新频率

- **实时数据**：交易日 9:30-15:00 每分钟更新
- **日线数据**：交易日收盘后更新

## 常见问题

**Q: 为什么获取数据很慢？**
A: AKshare 首次使用时需要下载数据库，这可能需要几分钟。后续请求会更快。

**Q: 股票代码格式有要求吗？**
A: 支持多种格式：
- '600000' （上证代码直接写）
- 'sh600000' （带市场标识）
- '000001' （深证代码直接写）
- 'sz000001' （带市场标识）

**Q: 如何获取特定时间的数据？**
A: 使用 `get_stock_daily()` 获取日线数据，然后过滤：
```python
daily = get_stock_daily('600000', period='100')
daily['date'] = pd.to_datetime(daily['date'])
may_data = daily[(daily['date'] >= '2026-05-01') & (daily['date'] <= '2026-05-31')]
print(may_data)
```

**Q: 如何计算收益率？**
A: 使用 DataFrame 进行计算：
```python
df = get_all_records('600000')
df['profit_rate'] = df['profit_loss'] / (df['trade_price'] * df['quantity']) * 100
print(df[['trade_type', 'profit_loss', 'profit_rate']])
```

## 相关资源

- AKshare 官方文档：https://akshare.akfamily.xyz/
- GitHub 项目：https://github.com/akfamily/akshare
- 金融数据指标说明：https://wiki.mbalib.com/
