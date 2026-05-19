# -*- coding: utf-8 -*-
"""
从网络获取真实股票数据并更新持仓
"""
import os
import sys
import logging
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Position, StockPrice
from app.services.stock_service import StockService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_and_update_realtime_data():
    """获取实时数据并更新持仓"""
    app = create_app()
    stock_service = StockService()

    with app.app_context():
        print("=" * 60)
        print("从网络获取真实股票数据...")
        print("=" * 60)

        positions = Position.query.filter(Position.total_quantity > 0).all()
        print(f"需要更新的持仓数量: {len(positions)}")

        success_count = 0
        fail_count = 0
        batch_size = 50

        for i, position in enumerate(positions):
            stock_code = position.stock_code

            # 批量输出进度
            if (i + 1) % batch_size == 0:
                print(f"进度: {i + 1}/{len(positions)}")

            try:
                data = stock_service.get_realtime_data(stock_code)

                if 'error' in data:
                    logger.warning(f"{stock_code} 获取失败: {data.get('error')}")
                    fail_count += 1
                    continue

                # 更新StockPrice表
                stock_price = StockPrice.query.filter_by(stock_code=stock_code).first()
                if not stock_price:
                    stock_price = StockPrice(stock_code=stock_code)
                    db.session.add(stock_price)

                stock_price.stock_name = data.get('stock_name', position.stock_name)
                stock_price.open_price = Decimal(str(data.get('open_price', 0)))
                stock_price.prev_close = Decimal(str(data.get('prev_close', 0)))
                stock_price.current_price = Decimal(str(data.get('current_price', 0)))
                stock_price.high_price = Decimal(str(data.get('high_price', 0)))
                stock_price.low_price = Decimal(str(data.get('low_price', 0)))
                stock_price.volume = data.get('volume', 0)
                stock_price.amount = Decimal(str(data.get('amount', 0)))
                stock_price.change_pct = Decimal(str(data.get('change_pct', 0)))
                stock_price.update_time = datetime.now()

                # 更新Position表
                current_price = float(data.get('current_price', 0))
                if current_price > 0:
                    position.current_price = Decimal(str(current_price))
                    position.current_value = position.total_quantity * Decimal(str(current_price))
                    position.unrealized_pnl = position.current_value - position.total_cost
                    if float(position.total_cost) > 0:
                        position.unrealized_pnl_rate = (position.unrealized_pnl / position.total_cost) * 100

                success_count += 1

            except Exception as e:
                logger.error(f"{stock_code} 更新异常: {e}")
                fail_count += 1

        db.session.commit()

        print("\n" + "=" * 60)
        print(f"更新完成! 成功: {success_count}, 失败: {fail_count}")
        print("=" * 60)

        # 显示更新后的持仓汇总
        print("\n持仓汇总 (前10只):")
        print("-" * 80)
        positions = Position.query.filter(Position.total_quantity > 0).order_by(
            Position.current_value.desc()
        ).limit(10).all()

        total_value = 0
        total_cost = 0

        for p in positions:
            value = float(p.current_value) if p.current_value else 0
            cost = float(p.total_cost) if p.total_cost else 0
            pnl = float(p.unrealized_pnl) if p.unrealized_pnl else 0
            rate = float(p.unrealized_pnl_rate) if p.unrealized_pnl_rate else 0
            price = float(p.current_price) if p.current_price else 0

            print(f"{p.stock_name}({p.stock_code}): 现价¥{price:.2f} | "
                  f"持股{p.total_quantity} | 市值¥{value:.2f} | 盈亏¥{pnl:.2f}({rate:.2f}%)")

            total_value += value
            total_cost += cost

        total_pnl = total_value - total_cost
        total_rate = (total_pnl / total_cost * 100) if total_cost > 0 else 0

        print("-" * 80)
        print(f"总市值: ¥{total_value:,.2f}")
        print(f"总成本: ¥{total_cost:,.2f}")
        print(f"总盈亏: ¥{total_pnl:,.2f} ({total_rate:.2f}%)")


def add_hot_stocks():
    """添加热门股票到持仓（可选）"""
    app = create_app()

    hot_stocks = [
        ('600519', '贵州茅台'),
        ('000858', '五粮液'),
        ('601318', '中国平安'),
        ('600036', '招商银行'),
        ('300750', '宁德时代'),
        ('688981', '中芯国际'),
        ('000001', '平安银行'),
        ('002594', '比亚迪'),
        ('600900', '长江电力'),
        ('601888', '中国中免'),
    ]

    with app.app_context():
        print("\n添加热门股票到持仓...")

        for code, name in hot_stocks:
            existing = Position.query.filter_by(stock_code=code).first()
            if existing:
                print(f"  {code} {name} 已存在，跳过")
                continue

            position = Position(
                stock_code=code,
                stock_name=name,
                asset_type='stock',
                total_quantity=0,
                available_quantity=0,
                frozen_quantity=0,
                avg_cost=Decimal('0'),
                total_cost=Decimal('0'),
                current_price=Decimal('0'),
                current_value=Decimal('0'),
                unrealized_pnl=Decimal('0'),
                unrealized_pnl_rate=Decimal('0')
            )
            db.session.add(position)
            print(f"  添加: {code} {name}")

        db.session.commit()
        print("热门股票添加完成")


if __name__ == '__main__':
    fetch_and_update_realtime_data()