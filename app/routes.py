# -*- coding: utf-8 -*-
"""
Flask路由定义
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.services.trade_service import TradeService
from app.services.stock_service import StockService
import json
import os

main_bp = Blueprint('main', __name__)
trade_service = TradeService()
stock_service = StockService()

@main_bp.route('/')
def index():
    """首页"""
    stock_code = request.args.get('stock_code', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    trades, total = trade_service.get_trades(
        stock_code=stock_code if stock_code else None,
        page=page,
        per_page=per_page
    )
    
    # 加载券商配置
    broker_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'brokers.json')
    brokers = []
    if os.path.exists(broker_config_path):
        with open(broker_config_path, 'r', encoding='utf-8') as f:
            brokers = json.load(f)
    
    return render_template('index.html', 
                         records=trades,
                         current_page=page,
                         current_per_page=per_page,
                         total_pages=(total + per_page - 1) // per_page if per_page > 0 else 0,
                         total_records=total,
                         brokers=brokers,
                         stock_code=stock_code,
                         stock_name=request.args.get('stock_name', ''))

@main_bp.route('/submit', methods=['POST'])
def submit():
    """提交交易记录"""
    data = request.form.to_dict()
    success, message = trade_service.add_trade(data)
    return jsonify({'success': success, 'message': message})

@main_bp.route('/detail/<int:trade_id>')
def detail(trade_id):
    """查看详情"""
    trade = trade_service.get_trade(trade_id)
    if not trade:
        return "记录不存在", 404
    return render_template('detail.html', trade=trade)

@main_bp.route('/edit/<int:trade_id>', methods=['GET', 'POST'])
def edit(trade_id):
    """编辑记录"""
    if request.method == 'POST':
        data = request.form.to_dict()
        success, message = trade_service.update_trade(trade_id, data)
        return jsonify({'success': success, 'message': message})
    
    trade = trade_service.get_trade(trade_id)
    if not trade:
        return "记录不存在", 404
    
    broker_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'brokers.json')
    brokers = []
    if os.path.exists(broker_config_path):
        with open(broker_config_path, 'r', encoding='utf-8') as f:
            brokers = json.load(f)
    
    return render_template('detail.html', trade=trade, edit=True, brokers=brokers)

@main_bp.route('/delete/<int:trade_id>', methods=['POST'])
def delete(trade_id):
    """删除记录"""
    success, message = trade_service.delete_trade(trade_id)
    return jsonify({'success': success, 'message': message})

@main_bp.route('/bulk_action', methods=['POST'])
def bulk_action():
    """批量操作"""
    data = request.get_json()
    action = data.get('action')
    ids = data.get('ids', [])
    
    if action == 'delete':
        success, message = trade_service.bulk_delete(ids)
    elif action == 'update':
        updates = data.get('updates', {})
        success, message = trade_service.bulk_update(ids, updates)
    else:
        success, message = False, '未知操作'
    
    return jsonify({'success': success, 'message': message})

# === 股票数据API ===

@main_bp.route('/stock_search')
def stock_search():
    """股票搜索"""
    name = request.args.get('name', '')
    if not name:
        return jsonify([])
    
    results = stock_service.search_stocks(name)
    return jsonify(results)

@main_bp.route('/stock_info')
def stock_info():
    """获取股票信息"""
    stock_code = request.args.get('stock_code', '')
    if not stock_code:
        return jsonify({'error': '缺少股票代码'})
    
    info = stock_service.get_stock_info(stock_code)
    return jsonify(info)

@main_bp.route('/api/stock/realtime')
def stock_realtime():
    """获取实时行情"""
    code = request.args.get('code', '')
    data = stock_service.get_realtime_data(code)
    return jsonify(data)

@main_bp.route('/api/stock/identify')
def stock_identify():
    """识别股票类型"""
    code = request.args.get('code', '')
    result = stock_service.identify_stock_type(code)
    return jsonify(result)

@main_bp.route('/api/position/pnl')
def position_pnl():
    """持仓盈亏计算"""
    stock_code = request.args.get('stock_code', '')
    pnl_data = trade_service.calculate_position_pnl(stock_code)
    return jsonify(pnl_data)

@main_bp.route('/api/portfolio/summary')
def portfolio_summary():
    """获取总体账户盈亏"""
    summary = trade_service.calculate_portfolio_summary()
    return jsonify(summary)

@main_bp.route('/api/sell', methods=['POST'])
def sell_stock():
    """卖出股票"""
    data = request.get_json()
    success, message, trade_id = trade_service.sell_stock(data)
    return jsonify({'success': success, 'message': message, 'trade_id': trade_id})

@main_bp.route('/api/brokers')
def get_brokers_list():
    """获取券商列表"""
    broker_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'brokers.json')
    if os.path.exists(broker_config_path):
        with open(broker_config_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])
