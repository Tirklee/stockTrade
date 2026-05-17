# -*- coding: utf-8 -*-
"""
数据库模型定义
"""
from datetime import datetime
from app import db


class Broker(db.Model):
    """券商表"""
    __tablename__ = 'brokers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))

    # 买入佣金配置
    buy_commission_rate = db.Column(db.Numeric(8, 4), default=1.0)  # 万分之一
    buy_min_commission = db.Column(db.Numeric(10, 2), default=5.0)  # 最低佣金

    # 卖出佣金配置
    sell_commission_rate = db.Column(db.Numeric(8, 4), default=1.0)
    sell_min_commission = db.Column(db.Numeric(10, 2), default=5.0)

    # 印花税配置
    stamp_tax_rate = db.Column(db.Numeric(8, 4), default=0.0005)  # 千分之0.5 (减半后)

    # 过户费配置(沪市)
    transfer_fee_rate = db.Column(db.Numeric(8, 4), default=0.00001)  # 万分之0.1

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    trades = db.relationship('TradeRecord', backref='broker', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'buy_commission_rate': float(self.buy_commission_rate),
            'sell_commission_rate': float(self.sell_commission_rate),
            'buy_min_commission': float(self.buy_min_commission),
            'sell_min_commission': float(self.sell_min_commission),
            'stamp_tax_rate': float(self.stamp_tax_rate),
            'is_active': self.is_active
        }


class Position(db.Model):
    """持仓表"""
    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(10), nullable=False, unique=True, index=True)
    stock_name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(20), default='stock')

    # 持仓数量
    total_quantity = db.Column(db.Integer, default=0)  # 总持股数
    available_quantity = db.Column(db.Integer, default=0)  # 可用数量
    frozen_quantity = db.Column(db.Integer, default=0)  # 冻结数量

    # 成本相关
    avg_cost = db.Column(db.Numeric(14, 4), default=0)  # 持仓成本
    total_cost = db.Column(db.Numeric(16, 2), default=0)  # 总成本

    # 当前行情
    current_price = db.Column(db.Numeric(12, 3))  # 当前价
    current_value = db.Column(db.Numeric(16, 2))  # 当前市值

    # 盈亏
    unrealized_pnl = db.Column(db.Numeric(14, 2), default=0)  # 未实现盈亏
    unrealized_pnl_rate = db.Column(db.Numeric(10, 4), default=0)  # 盈亏比率

    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    trades = db.relationship('TradeRecord', backref='position', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'asset_type': self.asset_type,
            'total_quantity': self.total_quantity,
            'available_quantity': self.available_quantity,
            'frozen_quantity': self.frozen_quantity,
            'avg_cost': float(self.avg_cost) if self.avg_cost else 0,
            'total_cost': float(self.total_cost) if self.total_cost else 0,
            'current_price': float(self.current_price) if self.current_price else 0,
            'current_value': float(self.current_value) if self.current_value else 0,
            'unrealized_pnl': float(self.unrealized_pnl) if self.unrealized_pnl else 0,
            'unrealized_pnl_rate': float(self.unrealized_pnl_rate) if self.unrealized_pnl_rate else 0,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def calculate_pnl(self, current_price):
        """计算盈亏"""
        if self.total_quantity > 0 and current_price:
            self.current_price = current_price
            self.current_value = self.total_quantity * current_price
            self.unrealized_pnl = self.current_value - self.total_cost
            if self.total_cost > 0:
                self.unrealized_pnl_rate = (self.unrealized_pnl / self.total_cost) * 100


class TradeRecord(db.Model):
    """交易记录表"""
    __tablename__ = 'trade_records'

    id = db.Column(db.Integer, primary_key=True)
    trade_time = db.Column(db.DateTime, default=datetime.now, index=True)
    stock_code = db.Column(db.String(10), nullable=False, index=True)
    stock_name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(20), default='stock')
    trade_type = db.Column(db.String(10), nullable=False)  # buy/sell

    # 交易数量和价格
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 3), nullable=False)
    total_amount = db.Column(db.Numeric(14, 2), nullable=False)

    # 费用明细
    commission = db.Column(db.Numeric(10, 3), default=0)
    commission_rate = db.Column(db.Numeric(8, 4))  # 实际佣金率
    stamp_tax = db.Column(db.Numeric(10, 3), default=0)  # 印花税
    transfer_fee = db.Column(db.Numeric(10, 3), default=0)  # 过户费
    total_fee = db.Column(db.Numeric(10, 3), default=0)  # 总费用

    # 券商
    broker_id = db.Column(db.Integer, db.ForeignKey('brokers.id'))
    custom_commission_rate = db.Column(db.Numeric(8, 4))  # 自定义佣金率

    # 关联持仓
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'))

    # 交易依据
    trade_basis = db.Column(db.Text)
    remark = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'trade_time': self.trade_time.strftime('%Y-%m-%d %H:%M:%S') if self.trade_time else None,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'asset_type': self.asset_type,
            'trade_type': self.trade_type,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'commission': float(self.commission) if self.commission else 0,
            'stamp_tax': float(self.stamp_tax) if self.stamp_tax else 0,
            'transfer_fee': float(self.transfer_fee) if self.transfer_fee else 0,
            'total_fee': float(self.total_fee) if self.total_fee else 0,
            'broker_id': self.broker_id,
            'broker_name': self.broker.name if self.broker else None,
            'position_id': self.position_id,
            'trade_basis': self.trade_basis,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class StockPrice(db.Model):
    """股票行情缓存表"""
    __tablename__ = 'stock_prices'

    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(10), nullable=False, unique=True, index=True)
    stock_name = db.Column(db.String(100))
    asset_type = db.Column(db.String(20), default='stock')

    # 行情数据
    open_price = db.Column(db.Numeric(12, 3))
    prev_close = db.Column(db.Numeric(12, 3))
    current_price = db.Column(db.Numeric(12, 3))
    high_price = db.Column(db.Numeric(12, 3))
    low_price = db.Column(db.Numeric(12, 3))
    volume = db.Column(db.BigInteger)  # 成交量
    amount = db.Column(db.Numeric(18, 2))  # 成交额
    change_pct = db.Column(db.Numeric(8, 4))  # 涨跌幅

    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'asset_type': self.asset_type,
            'open_price': float(self.open_price) if self.open_price else 0,
            'prev_close': float(self.prev_close) if self.prev_close else 0,
            'current_price': float(self.current_price) if self.current_price else 0,
            'high_price': float(self.high_price) if self.high_price else 0,
            'low_price': float(self.low_price) if self.low_price else 0,
            'volume': self.volume,
            'amount': float(self.amount) if self.amount else 0,
            'change_pct': float(self.change_pct) if self.change_pct else 0,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }