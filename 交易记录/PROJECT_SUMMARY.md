# 股票交易记录系统

## 项目完成总结

已成功构建基于 Baostock 和新浪财经的股票交易记录系统。

## 📦 项目文件结构

```
交易记录/
├── web_app.py              # Flask Web 应用
├── trade_service.py        # 核心服务模块
├── stock_trades.db         # SQLite 数据库文件
├── README.md               # 项目完整文档
├── QUICK_GUIDE.md          # 快速参考指南
└── BUGFIX_SUMMARY.md       # 问题修复记录
```

## 🎯 核心功能

### 数据库模块
- ✅ SQLite 数据库管理
- ✅ 交易记录存储和查询
- ✅ 股票汇总统计

### 数据获取模块
- ✅ Baostock 实时股票行情获取（主数据源）
- ✅ 新浪财经 API 实时行情（备选数据源）
- ✅ 自动数据填充交易记录

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
| high_price | REAL | 最高价 |
| low_price | REAL | 最低价 |
| trade_price | REAL | 实际交易价格 |
| commission_fee | REAL | 交易手续费 |
| profit_loss | REAL | 盈亏金额 |
| profit_loss_reason | TEXT | 盈亏原因 |
| trade_basis | TEXT | 交易依据 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

## 🔧 主要函数概览

### 交易记录函数
```python
add_trade_record()              # 添加交易记录
query_records()                 # 查询交易记录
get_stock_summary()             # 获取统计汇总
update_trade_record()           # 更新交易记录
delete_trade_record()           # 删除交易记录
bulk_delete_records()           # 批量删除
bulk_update_records()           # 批量更新
```

### 数据获取函数
```python
get_stock_info()                # 获取实时股票信息
add_trade_with_market_data()    # 自动添加交易（含市场数据）
```

## 📚 使用文档

### 1. 快速开始（QUICK_GUIDE.md）
- 最常用的操作
- 代码示例一目了然
- 新手推荐阅读

### 2. 完整文档（README.md）
- 详细的 API 说明
- 参数和返回值说明
- 适合深入学习

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
# 自动从 Baostock/新浪获取数据
add_trade_with_market_data(
    stock_code='600000',
    trade_type='buy',
    quantity=100,
    trade_price=10.50,
    commission_fee=5.25,
    trade_basis='市场数据确认'
)
```

### 查询和分析
```python
# 分页查询交易记录
records = query_records(page=1, per_page=20)

# 查询特定股票
records = query_records(stock_code='600000')

# 获取统计汇总
summary = get_stock_summary('600000')
print(f"总盈亏: {summary['total_profit_loss']}")
```

## 🌐 数据源说明

| 数据源 | 优先级 | 说明 |
|-------|--------|------|
| Baostock | 主数据源 | 专为A股设计，稳定免费 |
| 新浪财经 | 备选数据源 | HTTP请求，无需安装 |

系统支持：
- ✅ 自动切换数据源
- ✅ 网络故障降级处理
- ✅ 完整的离线功能

## 📦 依赖包

```
flask              # Web 框架
baostock          # 股票数据获取（主数据源）
```

## ✨ 功能亮点

1. **完整的 SQLite 数据持久化**
   - 所有交易记录永久保存
   - 支持复杂的 SQL 查询

2. **多数据源金融数据获取**
   - Baostock（主数据源）
   - 新浪财经 API（备选）

3. **智能网络处理**
   - 自动切换数据源
   - 在线/离线无缝切换
   - 优雅的错误处理

4. **Web 界面操作**
   - Flask Web 应用
   - Bootstrap 前端
   - 分页查询支持

5. **详尽的文档**
   - 快速参考指南
   - 完整的 API 文档
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
```

## 🛠️ 扩展建议

| 功能 | 优先级 | 说明 |
|-----|--------|------|
| 持仓管理 | 高 | 实时持仓统计 |
| 收益率计算 | 高 | 按时间段统计收益 |
| 止损/止盈提醒 | 中 | 价格提醒功能 |
| 数据可视化 | 中 | 图表展示 |

## 📞 故障排查

### 问题：数据获取失败
- **原因**：网络连接问题，数据源服务器不可达
- **解决**：
  1. 检查网络连接
  2. 使用离线模式继续工作
  3. 手动指定股票名称参数

### 问题：数据库锁定错误
- **原因**：多个进程访问数据库
- **解决**：确保只有一个程序访问数据库

## 📝 更新日志

### v2.0 (2026-05-16)
- ✅ 移除 akshare 依赖
- ✅ 使用 Baostock + 新浪财经作为数据源
- ✅ 添加 Flask Web 应用
- ✅ 支持批量操作

### v1.0 (2026-05-13)
- ✅ 基础交易记录系统
- ✅ SQLite 数据库管理
- ✅ 文档编写

---

**项目维护**：更新时间：2026-05-16