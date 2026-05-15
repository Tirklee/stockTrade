# 股票交易记录系统 - 集成 AKshare 数据获取

## 项目完成总结

已成功整合 **AKshare 金融数据库**到股票交易记录系统中，实现了从数据获取到交易记录的完整工作流。

## 📦 项目文件结构

```
交易记录/
├── T20260512.ipynb              # 主要 Jupyter Notebook（核心代码）
├── stock_trades.db              # SQLite 数据库文件
├── README.md                    # 项目完整文档
├── QUICK_GUIDE.md              # 快速参考指南
├── AKSHARE_GUIDE.md            # AKshare 专用使用指南
└── stocks.db                    # 备用数据库
```

## 🎯 核心功能

### 数据库模块
- ✅ SQLite 数据库管理
- ✅ 交易记录存储和查询
- ✅ 股票汇总统计

### AKshare 集成模块
- ✅ 实时股票行情获取
- ✅ 日线历史数据查询
- ✅ 股票列表查询
- ✅ 自动数据填充交易记录
- ✅ 网络故障自动重试和降级

### 交易管理模块
- ✅ 添加交易记录
- ✅ 查询交易历史
- ✅ 股票统计分析
- ✅ 更新盈亏信息
- ✅ 删除交易记录

## 📊 数据库表结构

### trade_records 表
记录所有股票交易信息，包含 14 个字段：

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INTEGER | 记录 ID（主键） |
| trade_time | TIMESTAMP | 交易时间 |
| stock_code | TEXT | 股票代码 |
| stock_name | TEXT | 股票名称 |
| trade_type | TEXT | 交易类型（buy/sell） |
| quantity | INTEGER | 交易数量 |
| opening_price | REAL | 开盘价 |
| closing_price | REAL | 收盘价 |
| trade_price | REAL | 实际交易价格 |
| commission_fee | REAL | 交易手续费 |
| profit_loss | REAL | 盈亏金额 |
| profit_loss_reason | TEXT | 盈亏原因 |
| trade_basis | TEXT | 交易依据 |
| created_at | TIMESTAMP | 创建时间 |

## 🔧 主要函数概览

### 交易记录函数
```python
add_trade_record()              # 添加交易记录
get_all_records()               # 查询交易记录
get_stock_summary()             # 获取统计汇总
update_profit_loss()            # 更新盈亏信息
delete_record()                 # 删除交易记录
```

### AKshare 数据获取函数
```python
get_stock_info()                # 获取实时股票信息
get_stock_daily()               # 获取日线行情数据
get_stock_list()                # 获取股票列表
add_trade_with_market_data()    # 自动添加交易（含市场数据）
```

## 📚 使用文档

### 1. 快速开始（QUICK_GUIDE.md）
- 最常用的 10 个操作
- 代码示例一目了然
- 新手推荐阅读

### 2. 完整文档（README.md）
- 详细的 API 说明
- 参数和返回值说明
- 适合深入学习

### 3. AKshare 专用指南（AKSHARE_GUIDE.md）
- AKshare 功能详解
- 4 大使用场景
- 数据分析示例

## 🚀 快速使用示例

### 无需网络的离线模式
```python
# 直接记录交易
add_trade_record(
    stock_code='600000',
    stock_name='浦发银行',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='技术面突破'
)
```

### 自动获取市场数据
```python
# 自动从 AKshare 获取数据
add_trade_with_market_data(
    stock_code='600000',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='AKshare 数据确认'
)
```

### 查询和分析
```python
# 查询所有交易
all_trades = get_all_records()

# 查询特定股票
pfyh_trades = get_all_records('600000')

# 获取统计汇总
summary = get_stock_summary('600000')
print(f"总盈亏: {summary['total_profit_loss']}")
```

## 🌐 网络连接说明

| 模式 | 说明 | 使用场景 |
|-----|------|---------|
| 在线 | 自动获取实时数据 | 有网络连接，需要最新数据 |
| 离线 | 本地数据库操作 | 无网络或网络不稳定 |
| 自动降级 | 尝试在线，失败自动离线 | 网络不稳定 |

系统支持：
- ✅ 自动重试（最多 3 次）
- ✅ 网络故障优雅降级
- ✅ 完整的离线功能

## 📦 依赖包

```
sqlite3         # 数据库
pandas          # 数据分析
akshare         # 股票数据获取
tqdm            # 进度显示
ipywidgets      # Jupyter 支持
```

## ✨ 功能亮点

1. **完整的 SQLite 数据持久化**
   - 所有交易记录永久保存
   - 支持复杂的 SQL 查询

2. **实时金融数据获取**
   - 集成 AKshare（开源中文金融库）
   - 获取 A 股实时行情和历史数据

3. **智能网络处理**
   - 自动重试机制
   - 在线/离线无缝切换
   - 优雅的错误处理

4. **灵活的数据查询**
   - Pandas DataFrame 支持
   - 支持导出 CSV/Excel
   - 可自定义分析

5. **详尽的文档**
   - 三份不同深度的文档
   - 丰富的使用示例
   - 常见问题解答

## 🔄 完整工作流示例

```python
# 1. 初始化
init_database()

# 2. 查看市场数据
info = get_stock_info('600000')
print(f"浦发银行: {info['current_price']}")

# 3. 记录买入交易
buy_id = add_trade_with_market_data(
    stock_code='600000',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='技术面看好'
)

# 4. 记录卖出交易
sell_id = add_trade_record(
    stock_code='600000',
    stock_name='浦发银行',
    trade_type='sell',
    quantity=100,
    trade_price=11.50,
    commission_fee=5.75,
    trade_basis='目标位获利',
    profit_loss=59.85,
    profit_loss_reason='成功止盈'
)

# 5. 查看交易统计
summary = get_stock_summary('600000')
print(f"总盈亏: {summary['total_profit_loss']:.2f}")

# 6. 导出数据
df = get_all_records()
df.to_csv('trades.csv', index=False)
```

## 📈 数据分析示例

```python
# 获取交易数据
trades = get_all_records()

# 按交易类型统计
buy_trades = trades[trades['trade_type'] == 'buy']
sell_trades = trades[trades['trade_type'] == 'sell']

# 计算平均价格
avg_buy_price = (buy_trades['trade_price'] * buy_trades['quantity']).sum() / buy_trades['quantity'].sum()
avg_sell_price = (sell_trades['trade_price'] * sell_trades['quantity']).sum() / sell_trades['quantity'].sum()

print(f"平均买入价: {avg_buy_price:.2f}")
print(f"平均卖出价: {avg_sell_price:.2f}")
print(f"平均价差: {avg_sell_price - avg_buy_price:.2f}")
```

## 🛠️ 扩展建议

| 功能 | 优先级 | 说明 |
|-----|--------|------|
| 持仓管理 | 高 | 实时持仓统计 |
| 收益率计算 | 高 | 按时间段统计收益 |
| 止损/止盈提醒 | 中 | 价格提醒功能 |
| 数据可视化 | 中 | 图表展示 |
| 多数据源支持 | 低 | 支持 Tushare 等其他源 |

## 📞 故障排查

### 问题：AKshare 数据获取失败
- **原因**：网络连接问题，AKshare 服务器不可达
- **解决**：
  1. 检查网络连接
  2. 使用离线模式继续工作
  3. 手动指定股票名称参数

### 问题：Jupyter 内核卡死
- **原因**：网络请求超时
- **解决**：重启内核，使用离线模式

### 问题：数据库锁定错误
- **原因**：多个进程访问数据库
- **解决**：确保只有一个程序访问数据库

## 📝 更新日志

### v1.0 (2026-05-13)
- ✅ 基础交易记录系统
- ✅ SQLite 数据库管理
- ✅ AKshare 集成
- ✅ 完整文档编写

## 📄 许可证

本项目遵循开源精神，免费使用和修改。

---

**项目维护**：自动更新时间：2026-05-13
**联系支持**：查看各文档的常见问题部分
