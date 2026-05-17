# Stock Trade Backend

## 快速启动

### 1. 创建虚拟环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置数据库
确保 PostgreSQL 已安装并运行，创建数据库：
```sql
CREATE DATABASE stock_trade;
```

或者设置环境变量：
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=stock_trade
export DB_USER=postgres
export DB_PASSWORD=your_password
```

### 4. 运行服务
```bash
python run.py
```

服务地址：http://localhost:5000

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/portfolio/summary | GET | 组合总览 |
| /api/positions | GET | 持仓列表 |
| /api/positions/{code} | GET | 持仓详情 |
| /api/trades/buy | POST | 买入 |
| /api/trades/sell | POST | 卖出 |
| /api/brokers | GET | 券商列表 |
| /api/stocks/{code}/realtime | GET | 实时行情 |
| /api/calculator/fee | POST | 费用计算 |