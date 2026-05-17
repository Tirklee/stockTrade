# -*- coding: utf-8 -*-
"""
券商服务
"""
from app import db
from app.models import Broker
import json
import os


def init_default_brokers():
    """初始化默认券商配置"""
    # 检查是否已有券商数据
    broker_count = Broker.query.count()
    if broker_count > 0:
        return

    # 默认券商配置
    default_brokers = [
        {
            'name': '默认券商',
            'description': '系统默认券商',
            'buy_commission_rate': 2.5,
            'sell_commission_rate': 2.5,
            'buy_min_commission': 5.0,
            'sell_min_commission': 5.0
        },
        {
            'name': '银河证券',
            'description': '银河证券默认配置',
            'buy_commission_rate': 2.5,
            'sell_commission_rate': 2.5,
            'buy_min_commission': 5.0,
            'sell_min_commission': 5.0
        },
        {
            'name': '华泰证券',
            'description': '华泰证券优惠佣金',
            'buy_commission_rate': 2.3,
            'sell_commission_rate': 2.3,
            'buy_min_commission': 5.0,
            'sell_min_commission': 5.0
        },
        {
            'name': '东方财富',
            'description': '东方财富默认配置',
            'buy_commission_rate': 2.0,
            'sell_commission_rate': 2.0,
            'buy_min_commission': 5.0,
            'sell_min_commission': 5.0
        }
    ]

    try:
        for broker_data in default_brokers:
            broker = Broker(
                name=broker_data['name'],
                description=broker_data['description'],
                buy_commission_rate=broker_data['buy_commission_rate'],
                sell_commission_rate=broker_data['sell_commission_rate'],
                buy_min_commission=broker_data['buy_min_commission'],
                sell_min_commission=broker_data['sell_min_commission']
            )
            db.session.add(broker)

        db.session.commit()
        print("默认券商数据初始化完成")
    except Exception as e:
        print(f"初始化券商数据失败: {e}")
        db.session.rollback()


def get_broker_commission_info(broker_id, trade_type='buy'):
    """获取券商佣金信息"""
    broker = Broker.query.get(broker_id)
    if not broker:
        return None

    if trade_type == 'buy':
        return {
            'commission_rate': float(broker.buy_commission_rate),
            'min_commission': float(broker.buy_min_commission)
        }
    else:
        return {
            'commission_rate': float(broker.sell_commission_rate),
            'min_commission': float(broker.sell_min_commission)
        }


def calculate_trade_fee(quantity, unit_price, trade_type, broker_info):
    """
    计算交易费用

    Args:
        quantity: 数量
        unit_price: 单价
        trade_type: 交易类型 'buy'/'sell'
        broker_info: 券商信息字典
    """
    amount = quantity * unit_price

    # 1. 佣金计算
    commission_rate = broker_info.get('commission_rate', 2.5)  # 默认万2.5
    min_commission = broker_info.get('min_commission', 5.0)    # 默认最低5元

    commission = amount * (commission_rate / 10000)
    commission = max(commission, min_commission)

    # 2. 印花税(仅卖出时收取)
    stamp_tax = 0
    if trade_type == 'sell':
        stamp_tax_rate = broker_info.get('stamp_tax_rate', 0.0005)  # 默认千0.5(减半后)
        stamp_tax = amount * stamp_tax_rate

    # 3. 过户费(沪市)
    transfer_fee = 0
    if str(quantity)[:1] in ['6']:  # 沪市股票
        transfer_fee_rate = broker_info.get('transfer_fee_rate', 0.00001)  # 万0.1
        transfer_fee = amount * transfer_fee_rate

    total_fee = commission + stamp_tax + transfer_fee

    return {
        'amount': amount,
        'commission': commission,
        'stamp_tax': stamp_tax,
        'transfer_fee': transfer_fee,
        'total_fee': total_fee
    }