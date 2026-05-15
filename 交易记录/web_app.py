import os

from flask import Flask, flash, redirect, render_template, request, url_for

from trade_service import (
    add_trade_record,
    bulk_delete_records,
    bulk_update_records,
    count_records,
    delete_trade_record,
    format_trade_time,
    get_record_by_id,
    get_stock_info,
    get_stock_summary,
    init_database,
    query_records,
    update_trade_record,
)

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
                    full_code = parts[3]  # 完整代码在第4个字段（如 sz300067）
                    
                    # 去掉市场前缀获取纯代码
                    if full_code.startswith(('sh', 'sz')):
                        code = full_code[2:]
                    else:
                        code = full_code
                    
                    # 过滤有效的A股代码（6位数字）
                    if code.isdigit() and len(code) == 6:
                        # 过滤指数（以000/399开头的通常是指数）
                        if not (code.startswith('000') or code.startswith('399')):
                            results.append({
                                'stock_code': code,
                                'stock_name': found_stock_name
                            })
        
        return {'results': results}
    except Exception as e:
        return {'results': [], 'error': str(e)}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
