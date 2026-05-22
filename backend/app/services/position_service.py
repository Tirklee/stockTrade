# -*- coding: utf-8 -*-
"""
持仓管理服务
"""
from datetime import datetime
from decimal import Decimal
from app import db
from app.models import Position, TradeRecord


class PositionService:
    """持仓服务类"""

    @staticmethod
    def get_or_create_position(stock_code, stock_name, asset_type='stock', broker_id=None):
        """获取或创建持仓记录"""
        query = Position.query.filter_by(stock_code=stock_code)
        if broker_id is not None:
            query = query.filter_by(broker_id=broker_id)
        else:
            query = query.filter(Position.broker_id.is_(None))
        position = query.first()

        if not position:
            position = Position(
                stock_code=stock_code,
                stock_name=stock_name,
                asset_type=asset_type,
                broker_id=broker_id,
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
            db.session.flush()

        return position

    @staticmethod
    def update_position_after_buy(position, quantity, unit_price, commission_fee):
        """买入后更新持仓"""
        # 计算新的平均成本
        total_cost = quantity * unit_price + commission_fee

        if position.total_quantity == 0:
            # 首次买入
            position.total_quantity = quantity
            position.available_quantity = quantity
            position.avg_cost = Decimal(str(unit_price))
            position.total_cost = Decimal(str(total_cost))
        else:
            # 追加买入
            old_cost = float(position.total_cost)
            new_cost = total_cost
            total_new_cost = old_cost + new_cost
            total_new_qty = position.total_quantity + quantity

            position.total_quantity = total_new_qty
            position.available_quantity = total_new_qty
            position.avg_cost = Decimal(str(total_new_cost / total_new_qty))
            position.total_cost = Decimal(str(total_new_cost))

        position.updated_at = datetime.now()
        return position

    @staticmethod
    def update_position_after_sell(position, quantity, avg_cost_from_sold, commission_fee):
        """卖出后更新持仓"""
        position.total_quantity -= quantity
        position.available_quantity -= quantity

        # 计算成本变化
        sold_cost = avg_cost_from_sold * quantity
        position.total_cost = Decimal(str(float(position.total_cost) - sold_cost))

        # 重新计算平均成本
        if position.total_quantity > 0:
            position.avg_cost = position.total_cost / position.total_quantity
        else:
            position.avg_cost = Decimal('0')
            position.total_cost = Decimal('0')

        position.updated_at = datetime.now()
        return position

    @staticmethod
    def update_position_pnl(position, current_price):
        """更新持仓盈亏"""
        if position.total_quantity > 0 and current_price:
            position.current_price = Decimal(str(current_price))
            position.current_value = Decimal(str(position.total_quantity * current_price))
            position.unrealized_pnl = position.current_value - position.total_cost

            if position.total_cost > 0:
                position.unrealized_pnl_rate = (position.unrealized_pnl / position.total_cost) * 100
            else:
                position.unrealized_pnl_rate = Decimal('0')
        else:
            position.current_price = Decimal('0')
            position.current_value = Decimal('0')
            position.unrealized_pnl = Decimal('0')
            position.unrealized_pnl_rate = Decimal('0')

        position.updated_at = datetime.now()
        return position

    @staticmethod
    def get_all_positions(page=1, per_page=20):
        """获取所有持仓（分页）"""
        query = Position.query.filter(Position.total_quantity > 0)

        total = query.count()
        positions = query.order_by(Position.unrealized_pnl_rate.desc()).offset(
            (page - 1) * per_page
        ).limit(per_page).all()

        return {
            'total': total,
            'page': page,
            'per_page': per_page,
            'data': [p.to_dict() for p in positions]
        }

    @staticmethod
    def get_position_by_code(stock_code, broker_id=None):
        """根据股票代码获取持仓"""
        query = Position.query.filter_by(stock_code=stock_code)
        if broker_id is not None:
            query = query.filter_by(broker_id=broker_id)
        else:
            query = query.filter(Position.broker_id.is_(None))
        position = query.first()
        return position.to_dict() if position else None

    @staticmethod
    def get_position_cost_detail(stock_code):
        """获取持仓成本明细"""
        trades = TradeRecord.query.filter_by(
            stock_code=stock_code,
            trade_type='buy'
        ).order_by(TradeRecord.trade_time.asc()).all()

        cost_records = []
        remaining_qty = 0

        for trade in trades:
            if trade.position:
                remaining_qty += trade.quantity

            cost_records.append({
                'trade_id': trade.id,
                'trade_time': trade.trade_time.strftime('%Y-%m-%d %H:%M:%S'),
                'quantity': trade.quantity,
                'unit_price': float(trade.unit_price),
                'total_amount': float(trade.total_amount),
                'commission': float(trade.commission),
                'cost_amount': float(trade.total_amount + trade.commission)
            })

        return cost_records

    @staticmethod
    def get_portfolio_summary():
        """获取组合总览"""
        positions = Position.query.filter(Position.total_quantity > 0).all()

        total_market_value = sum(float(p.current_value or 0) for p in positions)
        total_cost = sum(float(p.total_cost or 0) for p in positions)
        total_pnl = total_market_value - total_cost
        pnl_rate = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        stock_count = len(positions)

        return {
            'total_market_value': round(total_market_value, 2),
            'total_cost': round(total_cost, 2),
            'total_pnl': round(total_pnl, 2),
            'pnl_rate': round(pnl_rate, 2),
            'stock_count': stock_count,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def create_position(stock_code, stock_name, total_quantity, avg_cost, asset_type='stock', broker_id=None, buy_commission_rate=None, sell_commission_rate=None):
        """新增持仓"""
        query = Position.query.filter_by(stock_code=stock_code)
        if broker_id is not None:
            query = query.filter_by(broker_id=broker_id)
        else:
            query = query.filter(Position.broker_id.is_(None))
        existing = query.first()
        if existing:
            return {'success': False, 'message': '该股票在该券商已有持仓'}

        position = Position(
            stock_code=stock_code,
            stock_name=stock_name,
            asset_type=asset_type,
            broker_id=broker_id,
            buy_commission_rate=Decimal(str(buy_commission_rate)) if buy_commission_rate else None,
            sell_commission_rate=Decimal(str(sell_commission_rate)) if sell_commission_rate else None,
            total_quantity=total_quantity,
            available_quantity=total_quantity,
            frozen_quantity=0,
            avg_cost=Decimal(str(avg_cost)),
            total_cost=Decimal(str(total_quantity * avg_cost)),
            current_price=Decimal(str(avg_cost)),
            current_value=Decimal(str(total_quantity * avg_cost)),
            unrealized_pnl=Decimal('0'),
            unrealized_pnl_rate=Decimal('0')
        )
        db.session.add(position)
        db.session.commit()

        return {'success': True, 'message': '新增成功', 'data': position.to_dict()}

    @staticmethod
    def update_position(stock_code, total_quantity, avg_cost, broker_id=None, buy_commission_rate=None, sell_commission_rate=None):
        """修改持仓"""
        query = Position.query.filter_by(stock_code=stock_code)
        if broker_id is not None:
            query = query.filter_by(broker_id=broker_id)
        else:
            query = query.filter(Position.broker_id.is_(None))
        position = query.first()
        if not position:
            return {'success': False, 'message': '持仓不存在'}

        position.total_quantity = total_quantity
        position.available_quantity = total_quantity
        position.avg_cost = Decimal(str(avg_cost))
        position.total_cost = Decimal(str(total_quantity * avg_cost))
        if buy_commission_rate is not None:
            position.buy_commission_rate = Decimal(str(buy_commission_rate))
        if sell_commission_rate is not None:
            position.sell_commission_rate = Decimal(str(sell_commission_rate))
        position.updated_at = datetime.now()
        db.session.commit()

        return {'success': True, 'message': '修改成功', 'data': position.to_dict()}

    @staticmethod
    def delete_position(stock_code, broker_id=None):
        """删除持仓"""
        query = Position.query.filter_by(stock_code=stock_code)
        if broker_id is not None:
            query = query.filter_by(broker_id=broker_id)
        else:
            query = query.filter(Position.broker_id.is_(None))
        position = query.first()
        if not position:
            return {'success': False, 'message': '持仓不存在'}

        if position.total_quantity > 0:
            return {'success': False, 'message': '该股存在持股数，请先卖出或清仓后再删除'}

        db.session.delete(position)
        db.session.commit()

        return {'success': True, 'message': '删除成功'}