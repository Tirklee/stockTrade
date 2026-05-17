# -*- coding: utf-8 -*-
"""
生成模拟数据脚本 - 支持生成大量数据
"""
import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import TradeRecord, Position, Broker


def generate_stocks(count=200):
    """生成指定数量的股票数据"""
    stocks = []
    prefixes = ['600', '601', '603', '000', '002', '300', '688']
    stock_names = [
        '科技', '银行', '证券', '保险', '医药', '白酒', '新能源', '芯片', '通信',
        '地产', '基建', '消费', '农业', '军工', '环保', '物流', '旅游', '教育',
        '传媒', '机械', '化工', '钢铁', '煤炭', '有色', '电力', '公路', '港口',
        '航空', '航运', '房地产', '建筑', '装修', '家电', '纺织', '食品', '农业',
        '林业', '牧业', '渔业', '采掘', '金属', '非金属', '电子', '软件', '互联网'
    ]
    companies = [
        '华', '中', '国', '东', '西', '南', '北', '大', '小', '长', '平', '安',
        '高', '新', '兴', '旺', '福', '泰', '龙', '凤', '鹏', '鹰', '虎', '狮'
    ]

    for _ in range(count):
        prefix = random.choice(prefixes)
        code = f"{prefix}{random.randint(100, 999):03d}{random.randint(100, 999):03d}"
        name_prefix = random.choice(stock_names)
        name_suffix = random.choice(companies) + random.choice(['', '公司', '集团', '股份', '实业'])
        name = f"{name_prefix}{name_suffix}"

        stocks.append({
            'code': code,
            'name': name,
            'asset_type': 'stock'
        })
    return stocks


def create_mock_data(record_count=10000):
    """创建模拟数据"""
    app = create_app()

    with app.app_context():
        print("开始创建模拟数据...")

        # 清空现有数据
        db.session.query(TradeRecord).delete()
        db.session.query(Position).delete()
        db.session.commit()
        print("已清空现有数据")

        # 生成模拟股票数据
        stocks = generate_stocks(200)
        print(f"已生成 {len(stocks)} 只股票")

        # 获取一个券商ID
        broker = Broker.query.first()
        broker_id = broker.id if broker else 1

        # 随机选择一部分股票进行交易
        selected_stocks = random.sample(stocks, min(150, len(stocks)))

        # 交易理由库
        trade_reasons = [
            '价值投资', '成长性强', '行业龙头', '估值合理', '技术突破',
            '业绩预增', '政策利好', '市场份额提升', '技术护城河', '现金流充沛',
            '分红优厚', '重组预期', '产能扩张', '出口增长', '国产替代'
        ]

        print(f"开始生成 {record_count} 条交易记录...")

        # 批量创建交易记录
        batch_size = 1000
        for batch_start in range(0, record_count, batch_size):
            batch_end = min(batch_start + batch_size, record_count)
            batch_trades = []

            for _ in range(batch_start, batch_end):
                stock = random.choice(selected_stocks)
                trade_type = random.choice(['buy', 'sell'])
                days_ago = random.randint(0, 365)
                quantity = random.choice([100, 200, 300, 500, 1000, 1500, 2000])
                base_price = random.uniform(5.0, 500.0)
                unit_price = round(base_price, 2)
                total_amount = round(unit_price * quantity, 2)
                commission = max(5.0, total_amount * 0.0003)
                stamp_tax = total_amount * 0.001 if trade_type == 'sell' else 0
                transfer_fee = total_amount * 0.00002

                trade = TradeRecord(
                    trade_time=datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23)),
                    stock_code=stock['code'],
                    stock_name=stock['name'],
                    asset_type='stock',
                    trade_type=trade_type,
                    quantity=quantity,
                    unit_price=Decimal(str(unit_price)),
                    total_amount=Decimal(str(total_amount)),
                    commission=Decimal(str(round(commission, 2))),
                    stamp_tax=Decimal(str(round(stamp_tax, 2))),
                    transfer_fee=Decimal(str(round(transfer_fee, 4))),
                    total_fee=Decimal(str(round(commission + stamp_tax + transfer_fee, 2))),
                    broker_id=broker_id,
                    trade_basis=random.choice(trade_reasons)
                )
                batch_trades.append(trade)

            db.session.bulk_save_objects(batch_trades)
            db.session.commit()
            print(f"  已创建 {batch_end} 条交易记录")

        total_trades = TradeRecord.query.count()
        print(f"交易记录总数: {total_trades}")

        # 按股票代码分组统计（使用 CASE WHEN 兼容 SQLite）
        from sqlalchemy import func, case

        net_qty = func.sum(
            case((TradeRecord.trade_type == 'buy', TradeRecord.quantity), else_=-TradeRecord.quantity)
        ).label('net_quantity')

        stock_summary = db.session.query(
            TradeRecord.stock_code,
            TradeRecord.stock_name,
            net_qty,
            func.avg(TradeRecord.unit_price).label('avg_price')
        ).group_by(
            TradeRecord.stock_code,
            TradeRecord.stock_name
        ).having(net_qty > 0).all()

        print(f"共有 {len(stock_summary)} 只股票有持仓")

        # 创建持仓数据
        for summary in stock_summary:
            current_price = round(float(summary.avg_price) * random.uniform(0.85, 1.15), 2)
            total_quantity = summary.net_quantity
            total_cost = round(float(summary.avg_price) * total_quantity, 2)
            current_value = round(current_price * total_quantity, 2)
            unrealized_pnl = round(current_value - total_cost, 2)
            unrealized_pnl_rate = round((unrealized_pnl / total_cost * 100), 2) if total_cost > 0 else 0

            position = Position(
                stock_code=summary.stock_code,
                stock_name=summary.stock_name,
                asset_type='stock',
                total_quantity=total_quantity,
                available_quantity=total_quantity,
                frozen_quantity=0,
                avg_cost=Decimal(str(round(summary.avg_price, 2))),
                total_cost=Decimal(str(total_cost)),
                current_price=Decimal(str(current_price)),
                current_value=Decimal(str(current_value)),
                unrealized_pnl=Decimal(str(unrealized_pnl)),
                unrealized_pnl_rate=Decimal(str(unrealized_pnl_rate))
            )
            db.session.add(position)

        db.session.commit()
        print("持仓数据已创建")

        print("\n模拟数据创建完成！")


if __name__ == '__main__':
    create_mock_data()