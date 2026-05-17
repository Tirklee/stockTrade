# -*- coding: utf-8 -*-
"""
API路由
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.position_service import PositionService
from app.services.trade_service import TradeService
from app.services.stock_service import StockService
from app.services.broker_service import get_broker_commission_info
from app.models import Broker

api_bp = Blueprint('api', __name__)


# ==================== 券商API ====================

@api_bp.route('/brokers', methods=['GET'])
def get_brokers():
    """获取所有券商列表"""
    brokers = Broker.query.filter_by(is_active=True).all()
    return jsonify({
        'code': 0,
        'data': [b.to_dict() for b in brokers]
    })


@api_bp.route('/brokers/<int:broker_id>', methods=['GET'])
def get_broker(broker_id):
    """获取指定券商信息"""
    broker = Broker.query.get_or_404(broker_id)
    return jsonify({
        'code': 0,
        'data': broker.to_dict()
    })


@api_bp.route('/brokers/<int:broker_id>/commission', methods=['GET'])
def get_broker_commission(broker_id):
    """获取券商佣金信息"""
    trade_type = request.args.get('type', 'buy')
    commission_info = get_broker_commission_info(broker_id, trade_type)

    if not commission_info:
        return jsonify({
            'code': 404,
            'message': '券商不存在'
        }), 404

    return jsonify({
        'code': 0,
        'data': commission_info
    })


@api_bp.route('/brokers', methods=['POST'])
def create_broker():
    """创建券商"""
    data = request.get_json()

    broker = Broker(
        name=data.get('name'),
        description=data.get('description', ''),
        buy_commission_rate=data.get('buy_commission_rate', 2.5),
        sell_commission_rate=data.get('sell_commission_rate', 2.5),
        buy_min_commission=data.get('buy_min_commission', 5.0),
        sell_min_commission=data.get('sell_min_commission', 5.0)
    )

    from app import db
    db.session.add(broker)
    db.session.commit()

    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': broker.to_dict()
    })


# ==================== 持仓API ====================

@api_bp.route('/positions', methods=['GET'])
def get_positions():
    """获取持仓列表"""
    stock_code = request.args.get('stock_code')
    sort_by = request.args.get('sort_by', 'unrealized_pnl_rate')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = PositionService.get_all_positions(page=page, per_page=per_page)

    return jsonify({
        'code': 0,
        'data': result
    })


@api_bp.route('/positions/<stock_code>', methods=['GET'])
def get_position(stock_code):
    """获取指定持仓"""
    position = PositionService.get_position_by_code(stock_code)

    if not position:
        return jsonify({
            'code': 404,
            'message': '持仓不存在'
        }), 404

    return jsonify({
        'code': 0,
        'data': position
    })


@api_bp.route('/positions/<stock_code>/cost-detail', methods=['GET'])
def get_position_cost_detail(stock_code):
    """获取持仓成本明细"""
    cost_records = PositionService.get_position_cost_detail(stock_code)
    position = PositionService.get_position_by_code(stock_code)

    return jsonify({
        'code': 0,
        'data': {
            'position': position,
            'cost_records': cost_records
        }
    })


# ==================== 组合总览API ====================

@api_bp.route('/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """获取组合总览"""
    summary = PositionService.get_portfolio_summary()
    return jsonify({
        'code': 0,
        'data': summary
    })


# ==================== 交易API ====================

@api_bp.route('/trades/buy', methods=['POST'])
def buy_stock():
    """买入股票"""
    data = request.get_json()

    stock_code = data.get('stock_code')
    stock_name = data.get('stock_name')
    quantity = data.get('quantity')
    unit_price = data.get('unit_price')
    broker_id = data.get('broker_id')
    trade_basis = data.get('trade_basis', '')
    asset_type = data.get('asset_type', 'stock')

    if not all([stock_code, stock_name, quantity, unit_price, broker_id]):
        return jsonify({
            'code': 400,
            'message': '缺少必要参数'
        }), 400

    result = TradeService.buy_stock(
        stock_code=stock_code,
        stock_name=stock_name,
        quantity=quantity,
        unit_price=unit_price,
        broker_id=broker_id,
        trade_basis=trade_basis,
        asset_type=asset_type
    )

    if result['success']:
        return jsonify({
            'code': 0,
            'message': result['message'],
            'data': result['data']
        })
    else:
        return jsonify({
            'code': 400,
            'message': result['message']
        }), 400


@api_bp.route('/trades/sell', methods=['POST'])
def sell_stock():
    """卖出股票"""
    data = request.get_json()

    stock_code = data.get('stock_code')
    stock_name = data.get('stock_name')
    quantity = data.get('quantity')
    unit_price = data.get('unit_price')
    broker_id = data.get('broker_id')
    trade_basis = data.get('trade_basis', '')
    asset_type = data.get('asset_type', 'stock')

    if not all([stock_code, stock_name, quantity, unit_price, broker_id]):
        return jsonify({
            'code': 400,
            'message': '缺少必要参数'
        }), 400

    result = TradeService.sell_stock(
        stock_code=stock_code,
        stock_name=stock_name,
        quantity=quantity,
        unit_price=unit_price,
        broker_id=broker_id,
        trade_basis=trade_basis,
        asset_type=asset_type
    )

    if result['success']:
        return jsonify({
            'code': 0,
            'message': result['message'],
            'data': result['data']
        })
    else:
        return jsonify({
            'code': 400,
            'message': result['message']
        }), 400


@api_bp.route('/trades', methods=['GET'])
def get_trades():
    """获取交易记录"""
    stock_code = request.args.get('stock_code')
    trade_type = request.args.get('trade_type')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    result = TradeService.get_trade_records(
        stock_code=stock_code,
        trade_type=trade_type,
        page=page,
        per_page=per_page,
        start_date=start_date,
        end_date=end_date
    )

    return jsonify({
        'code': 0,
        'data': result
    })


@api_bp.route('/trades/<stock_code>/realized-pnl', methods=['GET'])
def get_realized_pnl(stock_code):
    """获取股票累计实现盈亏"""
    result = TradeService.get_stock_realized_pnl(stock_code)
    return jsonify({
        'code': 0,
        'data': result
    })


# ==================== 股票行情API ====================

@api_bp.route('/stocks/search', methods=['GET'])
def search_stocks():
    """搜索股票"""
    name = request.args.get('name', '')

    if not name or len(name) < 1:
        return jsonify({
            'code': 0,
            'data': []
        })

    stock_service = StockService()
    results = stock_service.search_stocks(name)

    return jsonify({
        'code': 0,
        'data': results
    })


@api_bp.route('/stocks/<stock_code>/realtime', methods=['GET'])
def get_stock_realtime(stock_code):
    """获取股票实时行情"""
    stock_service = StockService()
    data = stock_service.get_realtime_data(stock_code)

    if 'error' in data:
        return jsonify({
            'code': 400,
            'message': data['error']
        }), 400

    return jsonify({
        'code': 0,
        'data': data
    })


@api_bp.route('/stocks/<stock_code>/identify', methods=['GET'])
def identify_stock_type(stock_code):
    """识别股票类型"""
    stock_service = StockService()
    result = stock_service.identify_stock_type(stock_code)

    return jsonify({
        'code': 0,
        'data': result
    })


@api_bp.route('/stocks/<stock_code>/kline', methods=['GET'])
def get_stock_kline(stock_code):
    """获取K线数据"""
    period = request.args.get('period', 'daily')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    stock_service = StockService()
    result = stock_service.get_kline_data(
        stock_code=stock_code,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    if 'error' in result:
        return jsonify({
            'code': 400,
            'message': result['error']
        }), 400

    return jsonify({
        'code': 0,
        'data': result
    })


# ==================== 费用计算API ====================

@api_bp.route('/calculator/fee', methods=['POST'])
def calculate_fee():
    """计算交易费用"""
    data = request.get_json()

    quantity = data.get('quantity')
    unit_price = data.get('unit_price')
    trade_type = data.get('trade_type')  # buy/sell
    broker_id = data.get('broker_id')

    if not all([quantity, unit_price, trade_type]):
        return jsonify({
            'code': 400,
            'message': '缺少必要参数'
        }), 400

    # 获取券商佣金信息
    broker_info = get_broker_commission_info(broker_id, trade_type)

    if not broker_info:
        broker_info = {
            'commission_rate': 2.5,
            'min_commission': 5.0,
            'stamp_tax_rate': 0.0005
        }

    from app.services.broker_service import calculate_trade_fee
    fee_info = calculate_trade_fee(
        quantity=quantity,
        unit_price=unit_price,
        trade_type=trade_type,
        broker_info=broker_info
    )

    return jsonify({
        'code': 0,
        'data': fee_info
    })


# ==================== 健康检查 ====================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'code': 0,
        'message': 'OK',
        'data': {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
    })