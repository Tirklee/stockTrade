# -*- coding: utf-8 -*-
"""
交易服务
"""
from datetime import datetime
from decimal import Decimal
from app import db
from app.models import TradeRecord, Position
from app.services.position_service import PositionService
from app.services.broker_service import calculate_trade_fee, get_broker_commission_info


class TradeService:
    """交易服务类"""

    @staticmethod
    def buy_stock(stock_code, stock_name, quantity, unit_price, broker_id,
                  trade_basis='', asset_type='stock'):
        """
        买入股票

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            quantity: 买入数量
            unit_price: 买入价格
            broker_id: 券商ID
            trade_basis: 交易依据
            asset_type: 资产类型

        Returns:
            dict: 交易结果
        """
        try:
            # 获取持仓记录（按股票代码和券商查询）
            position = PositionService.get_or_create_position(
                stock_code, stock_name, asset_type, broker_id
            )

            # 获取券商佣金信息
            broker_info = get_broker_commission_info(broker_id, 'buy')

            # 计算费用
            fee_info = calculate_trade_fee(
                quantity=quantity,
                unit_price=unit_price,
                trade_type='buy',
                broker_info=broker_info
            )

            # 创建交易记录
            trade = TradeRecord(
                trade_time=datetime.now(),
                stock_code=stock_code,
                stock_name=stock_name,
                asset_type=asset_type,
                trade_type='buy',
                quantity=quantity,
                unit_price=Decimal(str(unit_price)),
                total_amount=Decimal(str(fee_info['amount'])),
                commission=Decimal(str(fee_info['commission'])),
                stamp_tax=Decimal('0'),
                transfer_fee=Decimal(str(fee_info['transfer_fee'])),
                total_fee=Decimal(str(fee_info['total_fee'])),
                broker_id=broker_id,
                position_id=position.id,
                trade_basis=trade_basis
            )
            db.session.add(trade)

            # 更新持仓
            PositionService.update_position_after_buy(
                position, quantity, unit_price, fee_info['commission']
            )

            # 更新持仓成本到交易记录
            trade.avg_cost = position.avg_cost

            db.session.commit()

            # 计算更新后的持仓信息
            position_pnl = position.to_dict()
            portfolio_summary = PositionService.get_portfolio_summary()

            return {
                'success': True,
                'message': '买入成功',
                'data': {
                    'trade_id': trade.id,
                    'trade_type': 'buy',
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_amount': fee_info['amount'],
                    'commission': fee_info['commission'],
                    'total_fee': fee_info['total_fee'],
                    'position': {
                        'total_quantity': position.total_quantity,
                        'avg_cost': float(position.avg_cost),
                        'total_cost': float(position.total_cost),
                        'unrealized_pnl': float(position.unrealized_pnl)
                    },
                    'portfolio_summary': portfolio_summary
                }
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'买入失败: {str(e)}',
                'data': None
            }

    @staticmethod
    def sell_stock(stock_code, stock_name, quantity, unit_price, broker_id,
                   trade_basis='', asset_type='stock'):
        """
        卖出股票

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            quantity: 卖出数量
            unit_price: 卖出价格
            broker_id: 券商ID
            trade_basis: 交易依据

        Returns:
            dict: 交易结果
        """
        try:
            # 获取持仓（按股票代码和券商查询）
            query = Position.query.filter_by(stock_code=stock_code, broker_id=broker_id)
            position = query.first()

            if not position:
                return {
                    'success': False,
                    'message': '该股票在该券商没有持仓',
                    'data': None
                }

            if position.available_quantity < quantity:
                return {
                    'success': False,
                    'message': f'可卖数量不足，当前可卖: {position.available_quantity}',
                    'data': None
                }

            # 获取券商佣金信息
            broker_info = get_broker_commission_info(broker_id, 'sell')

            # 计算费用
            fee_info = calculate_trade_fee(
                quantity=quantity,
                unit_price=unit_price,
                trade_type='sell',
                broker_info=broker_info
            )

            # 计算成本
            avg_cost_from_sold = float(position.avg_cost)

            # 创建交易记录
            trade = TradeRecord(
                trade_time=datetime.now(),
                stock_code=stock_code,
                stock_name=stock_name,
                asset_type=asset_type,
                trade_type='sell',
                quantity=quantity,
                unit_price=Decimal(str(unit_price)),
                total_amount=Decimal(str(fee_info['amount'])),
                commission=Decimal(str(fee_info['commission'])),
                stamp_tax=Decimal(str(fee_info['stamp_tax'])),
                transfer_fee=Decimal(str(fee_info['transfer_fee'])),
                total_fee=Decimal(str(fee_info['total_fee'])),
                broker_id=broker_id,
                position_id=position.id,
                trade_basis=trade_basis
            )
            db.session.add(trade)

            # 计算实现盈亏
            realized_pnl = (unit_price - avg_cost_from_sold) * quantity - fee_info['total_fee']

            # 更新持仓
            PositionService.update_position_after_sell(
                position, quantity, avg_cost_from_sold, fee_info['commission']
            )

            db.session.commit()

            # 获取更新后的持仓信息
            position_data = position.to_dict()
            portfolio_summary = PositionService.get_portfolio_summary()

            return {
                'success': True,
                'message': '卖出成功',
                'data': {
                    'trade_id': trade.id,
                    'trade_type': 'sell',
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_amount': fee_info['amount'],
                    'commission': fee_info['commission'],
                    'stamp_tax': fee_info['stamp_tax'],
                    'total_fee': fee_info['total_fee'],
                    'realized_pnl': realized_pnl,
                    'avg_cost': avg_cost_from_sold,
                    'position': {
                        'remaining_quantity': position.total_quantity,
                        'avg_cost': float(position.avg_cost),
                        'total_cost': float(position.total_cost)
                    },
                    'portfolio_summary': portfolio_summary
                }
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'卖出失败: {str(e)}',
                'data': None
            }

    @staticmethod
    def get_trade_records(stock_code=None, trade_type=None, page=1, per_page=20,
                          start_date=None, end_date=None):
        """获取交易记录"""
        query = TradeRecord.query

        if stock_code:
            query = query.filter(TradeRecord.stock_code == stock_code)

        if trade_type:
            query = query.filter(TradeRecord.trade_type == trade_type)

        if start_date:
            query = query.filter(TradeRecord.trade_time >= start_date)

        if end_date:
            query = query.filter(TradeRecord.trade_time <= end_date)

        # 分页
        total = query.count()
        trades = query.order_by(TradeRecord.trade_time.desc()).offset(
            (page - 1) * per_page
        ).limit(per_page).all()

        return {
            'total': total,
            'page': page,
            'per_page': per_page,
            'data': [t.to_dict() for t in trades]
        }

    @staticmethod
    def get_stock_realized_pnl(stock_code):
        """获取股票累计实现盈亏"""
        trades = TradeRecord.query.filter_by(
            stock_code=stock_code,
            trade_type='sell'
        ).all()

        total_realized_pnl = 0
        sell_details = []

        for trade in trades:
            # 计算该笔卖出的盈亏
            # 需要关联买入记录来计算实际成本
            realized_pnl = float(trade.total_amount - trade.total_fee)

            total_realized_pnl += realized_pnl
            sell_details.append({
                'trade_id': trade.id,
                'trade_time': trade.trade_time.strftime('%Y-%m-%d %H:%M:%S'),
                'quantity': trade.quantity,
                'unit_price': float(trade.unit_price),
                'total_amount': float(trade.total_amount),
                'fee': float(trade.total_fee),
                'realized_pnl': realized_pnl
            })

        return {
            'stock_code': stock_code,
            'total_realized_pnl': total_realized_pnl,
            'sell_count': len(sell_details),
            'sell_details': sell_details
        }