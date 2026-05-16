import logging
import os

from flask import Flask, flash, redirect, render_template, request, url_for

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

from trade_service import (
    add_trade_record,
    bulk_delete_records,
    bulk_update_records,
    count_records,
    delete_trade_record,
    format_trade_time,
    get_broker_by_id,
    get_brokers,
    get_record_by_id,
    get_stock_info,
    get_stock_summary,
    init_database,
    query_records,
    update_trade_record,
    DB_FILE,
)

import sqlite3
import urllib.request

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

@app.template_filter('decimal3')
def decimal3(value):
    if value is None:
        return ''
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return value

PAGE_SIZE = 10
PER_PAGE_OPTIONS = [5, 10, 20, 50, 100, 500, 1000]

init_database()


def parse_int(value: str, default: int) -> int:
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return default


@app.route('/')
def index():
    stock_code = request.args.get('stock_code', '').strip()
    stock_name = request.args.get('stock_name', '').strip()
    page = request.args.get('page', str(1))
    per_page = request.args.get('per_page', str(PAGE_SIZE))
    current_page = parse_int(page, 1)
    current_per_page = parse_int(per_page, PAGE_SIZE)
    # Allow any positive per_page value, but limit to reasonable bounds
    current_per_page = max(1, min(current_per_page, 1000))

    total = count_records(
        stock_code if stock_code else None,
        stock_name if stock_name else None
    )
    total_pages = max(1, (total + current_per_page - 1) // current_per_page)
    current_page = min(current_page, total_pages)
    records = query_records(
        stock_code if stock_code else None,
        stock_name if stock_name else None,
        page=current_page,
        per_page=current_per_page
    )
    summary = get_stock_summary(stock_code) if stock_code else None
    return render_template(
        'index.html',
        records=records,
        summary=summary,
        stock_code=stock_code,
        stock_name=stock_name,
        current_page=current_page,
        current_per_page=current_per_page,
        total_pages=total_pages,
        total_records=total,
        per_page_options=PER_PAGE_OPTIONS,
    )


@app.route('/submit', methods=['POST'])
def submit():
    record_id = request.form.get('record_id', '').strip()
    stock_code = request.form.get('stock_code', '').strip()
    stock_name = request.form.get('stock_name', '').strip()
    asset_type = request.form.get('asset_type', 'stock').strip()
    if asset_type not in ['stock', 'fund']:
        asset_type = 'stock'
    
    trade_type = request.form.get('trade_type', '').strip().lower()
    quantity = request.form.get('quantity', '').strip()
    trade_price = request.form.get('trade_price', '').strip()
    commission_fee = request.form.get('commission_fee', '').strip()
    trade_basis = request.form.get('trade_basis', '').strip()

    # 验证交易类型
    if not trade_type or trade_type not in ['buy', 'sell']:
        flash('请选择正确的交易类型 buy 或 sell。', 'danger')
        return redirect(url_for('index'))
    
    # 验证交易数量
    if not quantity.isdigit() or int(quantity) <= 0:
        flash('请输入有效的交易数量（正整数）。', 'danger')
        return redirect(url_for('index'))
    
    # 验证交易价格
    try:
        trade_price_value = float(trade_price)
        if trade_price_value <= 0:
            flash('交易价格必须为正数。', 'danger')
            return redirect(url_for('index'))
    except ValueError:
        flash('交易价格必须是有效的数字。', 'danger')
        return redirect(url_for('index'))
    
    # 验证手续费
    try:
        commission_fee_value = float(commission_fee or 0)
        if commission_fee_value < 0:
            flash('手续费不能为负数。', 'danger')
            return redirect(url_for('index'))
    except ValueError:
        flash('手续费必须是有效的数字。', 'danger')
        return redirect(url_for('index'))
    
    # 验证股票代码或名称
    if not stock_name and not stock_code:
        flash('请输入股票代码或股票名称。', 'danger')
        return redirect(url_for('index'))
    
    # 验证交易依据
    if not trade_basis:
        flash('请输入交易依据。', 'danger')
        return redirect(url_for('index'))
    
    # 验证股票代码格式（如果提供）
    if stock_code:
        # 移除可能的市场前缀进行检查
        code_without_prefix = stock_code.upper()
        if code_without_prefix.startswith('SH') or code_without_prefix.startswith('SZ'):
            code_without_prefix = code_without_prefix[2:]
        
        if not code_without_prefix.isdigit() or len(code_without_prefix) != 6:
            flash('股票代码格式不正确，应为6位数字（如：600000）。', 'danger')
            return redirect(url_for('index'))

    stock_info = None
    opening_price = closing_price = high_price = low_price = None
    if stock_code:
        # 尝试获取股票信息，如果失败则使用用户提供的名称
        stock_info = get_stock_info(stock_code)
        if stock_info:
            # 如果成功获取股票信息，使用返回的数据
            stock_name = stock_name or stock_info.get('stock_name')
            opening_price = stock_info.get('opening_price')
            closing_price = stock_info.get('closing_price')
            high_price = stock_info.get('high_price')
            low_price = stock_info.get('low_price')
        # 注意：如果获取股票信息失败，我们仍然允许保存，使用用户提供的名称

    try:
        if record_id:
            existing = get_record_by_id(int(record_id))
            if not existing:
                flash(f'未找到记录 ID={record_id}', 'danger')
                return redirect(url_for('index'))
            updated_id = update_trade_record(
                record_id=int(record_id),
                stock_code=stock_code or existing.get('stock_code'),
                stock_name=stock_name or existing.get('stock_name'),
                trade_type=trade_type,
                quantity=int(quantity),
                trade_price=trade_price_value,
                commission_fee=commission_fee_value,
                trade_basis=trade_basis,
                opening_price=opening_price if stock_code and stock_info else existing.get('opening_price'),
                closing_price=closing_price if stock_code and stock_info else existing.get('closing_price'),
                high_price=high_price if stock_code and stock_info else existing.get('high_price'),
                low_price=low_price if stock_code and stock_info else existing.get('low_price'),
                profit_loss=existing.get('profit_loss'),
                profit_loss_reason=existing.get('profit_loss_reason'),
            )
            flash(f'交易记录已更新，ID={updated_id}', 'success')
        else:
            new_id = add_trade_record(
                stock_code=stock_code or None,
                stock_name=stock_name,
                asset_type=asset_type,
                trade_type=trade_type,
                quantity=int(quantity),
                trade_price=trade_price_value,
                commission_fee=commission_fee_value,
                trade_basis=trade_basis,
                opening_price=opening_price,
                closing_price=closing_price,
                high_price=high_price,
                low_price=low_price,
            )
            flash(f'交易记录已保存，ID={new_id}', 'success')
    except Exception as exc:
        flash(f'保存失败: {exc}', 'danger')

    return redirect(url_for('index'))


@app.route('/edit/<int:record_id>')
def edit(record_id: int):
    stock_code = request.args.get('stock_code', '').strip()
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', str(PAGE_SIZE))
    current_page = parse_int(page, 1)
    current_per_page = parse_int(per_page, PAGE_SIZE)
    # Allow any positive per_page value, but limit to reasonable bounds
    current_per_page = max(1, min(current_per_page, 1000))
    total = count_records(stock_code if stock_code else None)
    total_pages = max(1, (total + current_per_page - 1) // current_per_page)
    current_page = min(current_page, total_pages)
    records = query_records(stock_code if stock_code else None, page=current_page, per_page=current_per_page)
    summary = get_stock_summary(stock_code) if stock_code else None
    edit_record = get_record_by_id(record_id)
    if not edit_record:
        flash(f'未找到记录 ID={record_id}', 'danger')
        return redirect(url_for('index', stock_code=stock_code, page=current_page, per_page=current_per_page) if stock_code else url_for('index', page=current_page, per_page=current_per_page))
    return render_template(
        'index.html',
        records=records,
        summary=summary,
        stock_code=stock_code,
        current_page=current_page,
        current_per_page=current_per_page,
        total_pages=total_pages,
        total_records=total,
        per_page_options=PER_PAGE_OPTIONS,
        edit_record=edit_record,
    )


@app.route('/detail/<int:record_id>')
def detail(record_id: int):
    stock_code = request.args.get('stock_code', '').strip()
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', str(PAGE_SIZE))
    current_page = parse_int(page, 1)
    current_per_page = parse_int(per_page, PAGE_SIZE)
    current_per_page = max(1, min(current_per_page, 1000))

    record = get_record_by_id(record_id)
    if not record:
        flash(f'未找到记录 ID={record_id}', 'danger')
        return redirect(url_for('index', stock_code=stock_code, page=current_page, per_page=current_per_page) if stock_code else url_for('index', page=current_page, per_page=current_per_page))

    record['trade_time'] = format_trade_time(record.get('trade_time'))
    return render_template(
        'detail.html',
        record=record,
        stock_code=stock_code,
        current_page=current_page,
        current_per_page=current_per_page,
    )


@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id: int):
    stock_code = request.args.get('stock_code', '').strip()
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', str(PAGE_SIZE))
    try:
        delete_trade_record(record_id)
        flash(f'记录已删除，ID={record_id}', 'success')
    except Exception as exc:
        flash(f'删除失败: {exc}', 'danger')
    return redirect(url_for('index', stock_code=stock_code, page=page, per_page=per_page) if stock_code else url_for('index', page=page, per_page=per_page))


@app.route('/bulk_action', methods=['POST'])
def bulk_action():
    stock_code = request.args.get('stock_code', '').strip()
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', str(PAGE_SIZE))
    action = request.form.get('action', '').strip()
    selected_ids = request.form.getlist('selected_ids')
    if not selected_ids:
        flash('请先勾选要操作的记录。', 'warning')
        return redirect(url_for('index', stock_code=stock_code, page=page, per_page=per_page) if stock_code else url_for('index', page=page, per_page=per_page))

    record_ids = []
    for record_id in selected_ids:
        try:
            record_ids.append(int(record_id))
        except ValueError:
            continue

    if not record_ids:
        flash('无效的记录ID。', 'danger')
        return redirect(url_for('index', stock_code=stock_code, page=page, per_page=per_page) if stock_code else url_for('index', page=page, per_page=per_page))

    try:
        if action == 'delete':
            deleted = bulk_delete_records(record_ids)
            flash(f'已删除 {deleted} 条记录。', 'success')
        elif action == 'update':
            bulk_stock_code = request.form.get('stock_code', '').strip() or None
            bulk_stock_name = request.form.get('stock_name', '').strip() or None
            bulk_trade_type = request.form.get('trade_type', '').strip().lower() or None
            bulk_quantity = request.form.get('quantity', '').strip() or None
            bulk_trade_price = request.form.get('trade_price', '').strip() or None
            bulk_commission_fee = request.form.get('commission_fee', '').strip() or None
            bulk_trade_basis = request.form.get('trade_basis', '').strip() or None

            if bulk_trade_type is not None and bulk_trade_type not in ['buy', 'sell']:
                bulk_trade_type = None

            if bulk_quantity is not None:
                try:
                    bulk_quantity = int(bulk_quantity)
                except ValueError:
                    flash('批量股票数必须为整数。', 'danger')
                    return redirect(url_for('index', stock_code=stock_code, page=page, per_page=per_page) if stock_code else url_for('index', page=page, per_page=per_page))

            if bulk_trade_price is not None:
                try:
                    bulk_trade_price = float(bulk_trade_price)
                except ValueError:
                    flash('批量交易价格必须为数字。', 'danger')
                    return redirect(url_for('index', stock_code=stock_code, page=page, per_page=per_page) if stock_code else url_for('index', page=page, per_page=per_page))

            if bulk_commission_fee is not None:
                try:
                    bulk_commission_fee = float(bulk_commission_fee)
                except ValueError:
                    flash('批量手续费必须为数字。', 'danger')
                    return redirect(url_for('index', stock_code=stock_code, page=page, per_page=per_page) if stock_code else url_for('index', page=page, per_page=per_page))

            if all(value is None for value in [bulk_stock_code, bulk_stock_name, bulk_trade_type, bulk_quantity, bulk_trade_price, bulk_commission_fee, bulk_trade_basis]):
                flash('请填写至少一个批量修改字段。', 'warning')
                return redirect(url_for('index', stock_code=stock_code, page=page, per_page=per_page) if stock_code else url_for('index', page=page, per_page=per_page))

            updated = bulk_update_records(
                record_ids=record_ids,
                stock_code=bulk_stock_code,
                stock_name=bulk_stock_name,
                trade_type=bulk_trade_type,
                quantity=bulk_quantity,
                trade_price=bulk_trade_price,
                commission_fee=bulk_commission_fee,
                trade_basis=bulk_trade_basis,
            )
            flash(f'已批量修改 {updated} 条记录。', 'success')
        else:
            flash('未知的批量操作。', 'danger')
    except Exception as exc:
        flash(f'批量操作失败: {exc}', 'danger')

    return redirect(url_for('index', stock_code=stock_code, page=page, per_page=per_page) if stock_code else url_for('index', page=page, per_page=per_page))


@app.route('/stock_info')
def stock_info():
    stock_code = request.args.get('stock_code', '').strip()
    info = get_stock_info(stock_code)
    return info or {}


@app.route('/stock_search')
def stock_search():
    """根据股票名称搜索股票代码"""
    stock_name = request.args.get('name', '').strip()
    if not stock_name:
        return {'results': []}
    
    # 使用新浪财经搜索接口
    try:
        import urllib.request
        import urllib.parse
        import re
        
        url = f'http://suggest3.sinajs.cn/suggest/type=11,12&key={urllib.parse.quote(stock_name.encode("gbk"))}&name=suggestdata'
        req = urllib.request.Request(url, headers={
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read().decode('gbk')
        
        if not data or 'suggestdata=' not in data:
            return {'results': []}
        
        # 解析返回数据
        # 格式: var suggestdata="sh600000,11,浦发银行,sh600000,浦发银行,,浦发银行,0,1,,,;..."
        # 每条记录字段: 市场+代码,类型,名称,市场+代码,名称,拼音,市场,类型,...
        matches = re.findall(r'"([^"]+)"', data)
        results = []
        
        for match in matches:
            # 按分号分割每条股票记录
            stock_records = match.split(';')
            for record in stock_records:
                parts = record.split(',')
                if len(parts) >= 7:
                    # 格式: 名称,类型,纯代码,完整代码,名称,...
                    # 如: 安诺其,11,300067,sz300067,安诺其,,安诺其,99,1,,,
                    found_stock_name = parts[0]  # 名称在第1个字段
                    stock_type = parts[1]  # 类型：11=股票，12=基金
                    full_code = parts[3]  # 完整代码在第4个字段（如 sz300067）
                    
                    # 只处理股票（type=11），不处理基金（type=12）
                    if stock_type != '11':
                        continue
                    
                    # 去掉市场前缀获取纯代码
                    if full_code.startswith(('sh', 'sz')):
                        code = full_code[2:]
                    else:
                        code = full_code
                    
                    # 过滤有效的A股代码（6位数字）
                    if code.isdigit() and len(code) == 6:
                        # A股代码范围：
                        # 600xxx-603xxx: 上海主板
                        # 688xxx: 科创板
                        # 000xxx-001xxx: 深圳主板
                        # 002xxx: 中小板
                        # 300xxx: 创业板
                        is_valid_a_stock = (
                            code.startswith('600') or  # 上海主板
                            code.startswith('601') or  # 上海主板
                            code.startswith('603') or  # 上海主板
                            code.startswith('688') or  # 科创板
                            code.startswith('000') or  # 深圳主板
                            code.startswith('001') or  # 深圳主板
                            code.startswith('002') or  # 中小板
                            code.startswith('003') or  # 深圳主板
                            code.startswith('300')    # 创业板
                        )
                        
                        # 过滤指数（000xxx开头的通常包含指数）
                        is_index = code.startswith('000') and len(code) == 6
                        
                        if is_valid_a_stock and not is_index:
                            results.append({
                                'stock_code': code,
                                'stock_name': found_stock_name
                            })
        
        return {'results': results}
    except Exception as e:
        return {'results': [], 'error': str(e)}


@app.route('/api/brokers')
def api_brokers():
    """获取券商列表"""
    brokers = get_brokers()
    return {
        'brokers': brokers,
        'config_file': 'config/brokers.json'
    }


@app.route('/api/brokers/<broker_id>')
def api_broker_by_id(broker_id):
    """根据ID获取单个券商信息"""
    broker = get_broker_by_id(broker_id)
    if broker:
        return broker
    return {'error': '券商不存在'}, 404


@app.route('/api/stock/minute')
def api_stock_minute():
    """获取股票分时数据或日K数据"""
    stock_code = request.args.get('code', '').strip()
    if not stock_code or len(stock_code) != 6:
        return {'error': '请提供6位股票代码'}, 400
    
    try:
        import urllib.request
        import json
        from datetime import datetime, timedelta
        
        # 新浪财经分时数据接口
        if stock_code.startswith(('6', '9')):
            sina_code = 'sh' + stock_code
        else:
            sina_code = 'sz' + stock_code
        
        # 获取当前时间
        now = datetime.now()
        current_hour = now.hour
        
        # 判断是否交易时间 (9:30-11:30, 13:00-15:00)
        is_trading_time = (
            (current_hour == 9 and now.minute >= 30) or
            (current_hour == 10) or
            (current_hour == 11 and now.minute <= 30) or
            (current_hour == 13) or
            (current_hour == 14 and now.minute < 50)
        )
        
        # 如果是交易时间，优先获取分时数据
        if is_trading_time:
            # 分时数据URL (5分钟K线数据)
            url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={sina_code}&scale=5&ma=no&datalen=48'
            
            req = urllib.request.Request(url, headers={
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0'
            })
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = response.read().decode('gbk')
                
                minute_data = json.loads(data)
                
                if minute_data and isinstance(minute_data, list) and len(minute_data) > 0:
                    times = []
                    prices = []
                    
                    for item in minute_data:
                        if isinstance(item, dict):
                            times.append(item.get('day', '')[:5])  # 取时间部分 HH:MM
                            prices.append(float(item.get('close', 0)))
                    
                    stock_info = get_stock_info(stock_code)
                    stock_name = stock_info.get('stock_name', stock_code) if stock_info else stock_code
                    prev_close = stock_info.get('closing_price', 0) if stock_info else 0
                    
                    return {
                        'code': stock_code,
                        'name': stock_name,
                        'type': 'minute',
                        'prev_close': prev_close,
                        'current_price': prices[-1] if prices else 0,
                        'times': times,
                        'prices': prices,
                    }
            except Exception as e:
                logger.warning(f"获取分时数据失败，尝试获取日K: {e}")
        
        # 非交易时间或分时数据获取失败，获取日K数据
        # 获取最近30个交易日的日K数据
        daily_url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={sina_code}&scale=240&ma=no&datalen=30'
        
        req = urllib.request.Request(daily_url, headers={
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk')
        
        daily_data = json.loads(data)
        
        if not daily_data or not isinstance(daily_data, list) or len(daily_data) == 0:
            return {'error': '暂无K线数据'}, 404
        
        times = []
        prices = []
        volumes = []
        
        for item in daily_data:
            if isinstance(item, dict):
                day_str = item.get('day', '')
                # 转换日期格式为 MM-DD
                if len(day_str) >= 10:
                    times.append(day_str[5:10])  # MM-DD
                else:
                    times.append(day_str[:5])
                prices.append(float(item.get('close', 0)))
                volumes.append(int(float(item.get('volume', 0)) / 100))  # 转换为万手
        
        # 获取当前股票信息
        stock_info = get_stock_info(stock_code)
        stock_name = stock_info.get('stock_name', stock_code) if stock_info else stock_code
        prev_close = stock_info.get('closing_price', 0) if stock_info else 0
        
        # 获取最后一天的开高低收
        last_day = daily_data[-1] if daily_data else {}
        open_price = float(last_day.get('open', 0))
        high_price = float(last_day.get('high', 0))
        low_price = float(last_day.get('low', 0))
        close_price = float(last_day.get('close', 0))
        
        return {
            'code': stock_code,
            'name': stock_name,
            'type': 'daily',
            'prev_close': prev_close or open_price,
            'current_price': close_price,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'times': times,
            'prices': prices,
            'volumes': volumes,
            'is_holiday': not is_trading_time,
        }
    except Exception as e:
        logger.error(f"获取K线数据失败: {e}")
        return {'error': str(e)}, 500


@app.route('/api/stock/identify')
def api_stock_identify():
    """根据股票/基金代码识别资产类型（股票还是基金）"""
    code = request.args.get('code', '').strip()
    if not code or len(code) != 6:
        return {'type': 'unknown'}
    
    try:
        import urllib.request
        import urllib.parse
        
        # 基金代码通常以 5 开头（如 510300 是沪深300ETF）
        # A股股票代码范围：600-603, 688, 000-003, 002, 300
        if code.startswith('5') or code.startswith('15'):
            # 基金（ETF、LOF等）
            return {'type': 'fund', 'code': code}
        elif code.startswith(('6', '688', '000', '001', '002', '003', '300')):
            return {'type': 'stock', 'code': code}
        else:
            return {'type': 'unknown'}
    except Exception as e:
        return {'type': 'unknown'}


@app.route('/api/stock/realtime')
def api_stock_realtime():
    """获取股票实时行情（包含分时数据）"""
    stock_code = request.args.get('code', '').strip()
    if not stock_code or len(stock_code) != 6:
        return {'error': '请提供6位股票代码'}, 400
    
    try:
        import urllib.request
        # 新浪财经实时行情接口
        if stock_code.startswith(('6', '9')):
            sina_code = 'sh' + stock_code
        else:
            sina_code = 'sz' + stock_code
        
        url = f'http://hq.sinajs.cn/list={sina_code}'
        req = urllib.request.Request(url, headers={
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        })
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read().decode('gbk')
        
        if not data or '=' not in data:
            return {'error': '无法获取数据'}, 500
        
        parts = data.split('"')
        if len(parts) < 2:
            return {'error': '数据格式错误'}, 500
        
        values = parts[1].split(',')
        if len(values) < 32:
            return {'error': '数据不完整'}, 500
        
        stock_name = values[0]
        open_price = float(values[1]) if values[1] else 0
        prev_close = float(values[2]) if values[2] else 0
        current_price = float(values[3]) if values[3] else 0
        high_price = float(values[4]) if values[4] else 0
        low_price = float(values[5]) if values[5] else 0
        volume = int(values[8]) if values[8] else 0  # 成交量（手）
        amount = float(values[9]) if values[9] else 0  # 成交额（元）
        
        # 计算涨跌幅
        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close > 0 else 0
        
        return {
            'code': stock_code,
            'name': stock_name,
            'open': open_price,
            'prev_close': prev_close,
            'current': current_price,
            'high': high_price,
            'low': low_price,
            'volume': volume,
            'amount': amount,
            'change': round(change, 3),
            'change_pct': round(change_pct, 2),
            'time': values[30] + ' ' + values[31] if len(values) > 31 else ''
        }
    except Exception as e:
        logger.error(f"获取实时行情失败: {e}")
        return {'error': str(e)}, 500


@app.route('/api/position/pnl')
def api_position_pnl():
    """获取指定股票的持仓盈亏数据"""
    stock_code = request.args.get('stock_code', '').strip()
    
    if not stock_code:
        return {'error': '股票代码不能为空', 'positions': []}, 400
    
    try:
        # 获取该股票所有买入记录（按时间正序）
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        buy_records = conn.execute('''
            SELECT id, trade_time, quantity, trade_price, commission_fee
            FROM trade_records
            WHERE stock_code = ? AND trade_type = 'buy'
            ORDER BY trade_time ASC
        ''', (stock_code,)).fetchall()
        
        sell_records = conn.execute('''
            SELECT id, trade_time, quantity, trade_price
            FROM trade_records
            WHERE stock_code = ? AND trade_type = 'sell'
            ORDER BY trade_time ASC
        ''', (stock_code,)).fetchall()
        conn.close()
        
        # 获取实时价格
        try:
            realtime_url = f'http://hq.sinajs.cn/list=sh{stock_code},sz{stock_code}'
            req = urllib.request.Request(realtime_url, headers={'Referer': 'https://finance.sina.com.cn'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read().decode('gbk')
                if '="ERROR"' in data or '="INVALID"' in data:
                    current_price = 0
                else:
                    parts = data.split('="')[1].split(',')
                    current_price = float(parts[3]) if len(parts) > 3 and parts[3] else 0
        except Exception:
            current_price = 0
        
        # 计算持仓和盈亏
        positions = []
        total_cost = 0
        total_shares = 0
        remaining_shares = 0
        avg_cost = 0  # 初始化默认值
        
        for record in buy_records:
            shares = record['quantity']
            price = record['trade_price']
            cost = shares * price + (record['commission_fee'] or 0)
            avg_cost = cost / shares if shares > 0 else 0
            total_cost += cost
            total_shares += shares
            
            # 模拟计算：买入时盈亏为0
            pnl = 0
            pnl_rate = 0
            
            positions.append({
                'trade_time': record['trade_time'],
                'trade_type': 'buy',
                'quantity': shares,
                'cost_price': round(avg_cost, 3),
                'current_price': current_price,
                'pnl': round(pnl, 2),
                'pnl_rate': round(pnl_rate, 2)
            })
            remaining_shares += shares
        
        # 计算卖出的影响
        for record in sell_records:
            shares = record['quantity']
            price = record['trade_price']
            
            # 卖出时计算已实现盈亏
            if total_shares > 0:
                avg_cost = total_cost / total_shares
                pnl = (price - avg_cost) * shares
                pnl_rate = (price - avg_cost) / avg_cost * 100 if avg_cost > 0 else 0
            else:
                pnl = 0
                pnl_rate = 0
                avg_cost = 0
            
            total_cost -= shares * avg_cost
            total_shares -= shares
            remaining_shares -= shares
            
            positions.append({
                'trade_time': record['trade_time'],
                'trade_type': 'sell',
                'quantity': shares,
                'cost_price': round(avg_cost, 3),
                'current_price': current_price,
                'pnl': round(pnl, 2),
                'pnl_rate': round(pnl_rate, 2)
            })
        
        return {
            'stock_code': stock_code,
            'current_price': current_price,
            'positions': positions,
            'remaining_shares': remaining_shares
        }
        
    except Exception as e:
        logger.error(f"获取持仓盈亏失败: {e}")
        return {'error': str(e), 'positions': []}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
