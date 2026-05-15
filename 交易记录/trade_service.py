import os
import sqlite3
import logging
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 如果没有处理器，添加控制台处理器
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# ====== 数据源可用性检测 ======

# 1. baostock - 推荐主数据源（免费稳定，专为A股设计）
try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    baostock = None
    BAOSTOCK_AVAILABLE = False

# 2. akshare - 备选数据源（部分接口已关闭但仍有可用接口）
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    ak = None
    AKSHARE_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'stock_trades.db')


def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trade_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_time TIMESTAMP NOT NULL,
        stock_code TEXT,
        stock_name TEXT NOT NULL,
        trade_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        opening_price REAL,
        closing_price REAL,
        high_price REAL,
        low_price REAL,
        trade_price REAL NOT NULL,
        commission_fee REAL NOT NULL DEFAULT 0,
        profit_loss REAL,
        profit_loss_reason TEXT,
        trade_basis TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code ON trade_records(stock_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_time ON trade_records(trade_time)')

    cursor.execute('PRAGMA table_info(trade_records)')
    existing_columns = {row[1] for row in cursor.fetchall()}
    if 'high_price' not in existing_columns:
        cursor.execute('ALTER TABLE trade_records ADD COLUMN high_price REAL')
    if 'low_price' not in existing_columns:
        cursor.execute('ALTER TABLE trade_records ADD COLUMN low_price REAL')

    conn.commit()
    conn.close()


def format_trade_time(raw_time: Optional[str]) -> Optional[str]:
    if raw_time is None:
        return None
    try:
        parsed = datetime.fromisoformat(raw_time)
        return parsed.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            parsed = datetime.strptime(raw_time, '%Y-%m-%d %H:%M:%S')
            return parsed.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return raw_time


def add_trade_record(
    stock_code: Optional[str],
    stock_name: str,
    trade_type: str,
    quantity: int,
    trade_price: float,
    commission_fee: float,
    trade_basis: str,
    trade_time: Optional[str] = None,
    opening_price: Optional[float] = None,
    closing_price: Optional[float] = None,
    high_price: Optional[float] = None,
    low_price: Optional[float] = None,
    profit_loss: Optional[float] = None,
    profit_loss_reason: Optional[str] = None,
) -> int:
    """添加交易记录"""
    if trade_time is None:
        trade_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        trade_time = format_trade_time(trade_time)

    if trade_type.lower() not in ['buy', 'sell']:
        raise ValueError("trade_type must be 'buy' or 'sell'")

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trade_records
            (trade_time, stock_code, stock_name, trade_type, quantity,
             opening_price, closing_price, high_price, low_price, trade_price, commission_fee,
             profit_loss, profit_loss_reason, trade_basis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_time,
            stock_code.upper() if stock_code else None,
            stock_name,
            trade_type.lower(),
            quantity,
            opening_price,
            closing_price,
            high_price,
            low_price,
            trade_price,
            commission_fee,
            profit_loss,
            profit_loss_reason,
            trade_basis,
        ))
        conn.commit()
        record_id = cursor.lastrowid
        logger.info(f"添加交易记录成功: ID={record_id}, 股票={stock_name}, 类型={trade_type}, 数量={quantity}")
        return record_id
    except Exception as e:
        logger.error(f"添加交易记录失败: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


def query_records(stock_code: Optional[str] = None, stock_name: Optional[str] = None, page: int = 1, per_page: int = 20) -> List[Dict]:
    """查询交易记录，支持股票代码和股票名称模糊查询"""
    if page < 1:
        page = 1
    offset = (page - 1) * per_page
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 构建查询条件和参数
    conditions = []
    params = []
    
    if stock_code:
        conditions.append('stock_code LIKE ?')
        params.append(f'%{stock_code.upper()}%')
    
    if stock_name:
        conditions.append('stock_name LIKE ?')
        params.append(f'%{stock_name}%')
    
    # 构建SQL
    where_clause = ''
    if conditions:
        where_clause = 'WHERE ' + ' AND '.join(conditions)
    
    sql = f'''
        SELECT * FROM trade_records
        {where_clause}
        ORDER BY trade_time DESC
        LIMIT ? OFFSET ?
    '''
    params.extend([per_page, offset])
    
    cursor.execute(sql, tuple(params))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    for row in rows:
        if 'trade_time' in row:
            row['trade_time'] = format_trade_time(row['trade_time'])
    return rows


def count_records(stock_code: Optional[str] = None, stock_name: Optional[str] = None) -> int:
    """统计记录数量，支持股票代码和股票名称模糊查询"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if stock_code:
        conditions.append('stock_code LIKE ?')
        params.append(f'%{stock_code.upper()}%')
    
    if stock_name:
        conditions.append('stock_name LIKE ?')
        params.append(f'%{stock_name}%')
    
    if conditions:
        where_clause = 'WHERE ' + ' AND '.join(conditions)
        cursor.execute(f'SELECT COUNT(*) FROM trade_records {where_clause}', tuple(params))
    else:
        cursor.execute('SELECT COUNT(*) FROM trade_records')
    
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_record_by_id(record_id: int) -> Optional[Dict]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trade_records WHERE id = ?', (record_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_trade_record(
    record_id: int,
    stock_code: Optional[str],
    stock_name: Optional[str],
    trade_type: Optional[str],
    quantity: Optional[int],
    trade_price: Optional[float],
    commission_fee: Optional[float],
    trade_basis: Optional[str],
    opening_price: Optional[float] = None,
    closing_price: Optional[float] = None,
    high_price: Optional[float] = None,
    low_price: Optional[float] = None,
    profit_loss: Optional[float] = None,
    profit_loss_reason: Optional[str] = None,
) -> int:
    """更新交易记录"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE trade_records
            SET stock_code = ?, stock_name = ?, trade_type = ?, quantity = ?,
                opening_price = ?, closing_price = ?, high_price = ?, low_price = ?, trade_price = ?,
                commission_fee = ?, profit_loss = ?, profit_loss_reason = ?,
                trade_basis = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            stock_code.upper() if stock_code else None,
            stock_name,
            trade_type.lower() if trade_type else None,
            quantity,
            opening_price,
            closing_price,
            high_price,
            low_price,
            trade_price,
            commission_fee,
            profit_loss,
            profit_loss_reason,
            trade_basis,
            record_id,
        ))
        conn.commit()
        logger.info(f"更新交易记录成功: ID={record_id}")
        return record_id
    except Exception as e:
        logger.error(f"更新交易记录失败: ID={record_id}, 错误: {e}")
        raise
    finally:
        conn.close()


def bulk_delete_records(record_ids: list[int]) -> int:
    """批量删除记录，增强安全性验证"""
    if not record_ids:
        return 0
    
    # 验证所有ID都是正整数
    validated_ids = []
    for record_id in record_ids:
        try:
            rid = int(record_id)
            if rid > 0:
                validated_ids.append(rid)
        except (TypeError, ValueError):
            continue
    
    if not validated_ids:
        return 0
    
    # 限制一次删除的记录数量，防止误操作
    if len(validated_ids) > 1000:
        raise ValueError("一次最多只能删除1000条记录")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        placeholders = ','.join('?' for _ in validated_ids)
        cursor.execute(f'DELETE FROM trade_records WHERE id IN ({placeholders})', tuple(validated_ids))
        deleted_count = cursor.rowcount
        conn.commit()
        logger.info(f"批量删除记录成功: 删除了 {deleted_count} 条记录")
        return deleted_count
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"批量删除记录失败: {e}")
        raise RuntimeError(f"批量删除失败: {e}")
    finally:
        conn.close()


def bulk_update_records(
    record_ids: list[int],
    stock_code: Optional[str] = None,
    stock_name: Optional[str] = None,
    trade_type: Optional[str] = None,
    quantity: Optional[int] = None,
    trade_price: Optional[float] = None,
    commission_fee: Optional[float] = None,
    trade_basis: Optional[str] = None,
) -> int:
    """批量更新记录，增强安全性验证"""
    if not record_ids:
        return 0
    
    # 验证所有ID都是正整数
    validated_ids = []
    for record_id in record_ids:
        try:
            rid = int(record_id)
            if rid > 0:
                validated_ids.append(rid)
        except (TypeError, ValueError):
            continue
    
    if not validated_ids:
        return 0
    
    # 限制一次更新的记录数量
    if len(validated_ids) > 1000:
        raise ValueError("一次最多只能更新1000条记录")
    
    updates = []
    params = []
    
    # 验证和规范化数据
    if stock_code is not None:
        stock_code = stock_code.strip().upper()
        if stock_code:
            updates.append('stock_code = ?')
            params.append(stock_code)
    
    if stock_name is not None:
        stock_name = stock_name.strip()
        if stock_name:
            updates.append('stock_name = ?')
            params.append(stock_name)
    
    if trade_type is not None:
        trade_type = trade_type.strip().lower()
        if trade_type in ['buy', 'sell']:
            updates.append('trade_type = ?')
            params.append(trade_type)
    
    if quantity is not None:
        if quantity > 0:
            updates.append('quantity = ?')
            params.append(quantity)
    
    if trade_price is not None:
        if trade_price > 0:
            updates.append('trade_price = ?')
            params.append(trade_price)
    
    if commission_fee is not None:
        if commission_fee >= 0:
            updates.append('commission_fee = ?')
            params.append(commission_fee)
    
    if trade_basis is not None:
        trade_basis = trade_basis.strip()
        if trade_basis:
            updates.append('trade_basis = ?')
            params.append(trade_basis)
    
    if not updates:
        raise ValueError('没有要更新的字段。')
    
    updates.append('updated_at = CURRENT_TIMESTAMP')
    placeholders = ','.join('?' for _ in validated_ids)
    sql = f'UPDATE trade_records SET {", ".join(updates)} WHERE id IN ({placeholders})'
    params.extend(validated_ids)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(sql, tuple(params))
        updated_count = cursor.rowcount
        conn.commit()
        logger.info(f"批量更新记录成功: 更新了 {updated_count} 条记录")
        return updated_count
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"批量更新记录失败: {e}")
        raise RuntimeError(f"批量更新失败: {e}")
    finally:
        conn.close()


def delete_trade_record(record_id: int) -> None:
    """删除交易记录"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM trade_records WHERE id = ?', (record_id,))
        conn.commit()
        logger.info(f"删除交易记录成功: ID={record_id}")
    except Exception as e:
        logger.error(f"删除交易记录失败: ID={record_id}, 错误: {e}")
        raise
    finally:
        conn.close()


def get_stock_summary(stock_code: str) -> Dict:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            MAX(stock_name) as stock_name,
            COUNT(*) as total_trades,
            SUM(CASE WHEN trade_type='buy' THEN 1 ELSE 0 END) as buy_count,
            SUM(CASE WHEN trade_type='sell' THEN 1 ELSE 0 END) as sell_count,
            SUM(CASE WHEN trade_type='buy' THEN quantity ELSE 0 END) as total_buy_qty,
            SUM(CASE WHEN trade_type='sell' THEN quantity ELSE 0 END) as total_sell_qty,
            SUM(commission_fee) as total_commission,
            SUM(profit_loss) as total_profit_loss
        FROM trade_records
        WHERE stock_code = ?
    ''', (stock_code.upper(),))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] is not None:
        return {
            'stock_code': stock_code.upper(),
            'stock_name': row[0],
            'total_trades': row[1] or 0,
            'buy_count': row[2] or 0,
            'sell_count': row[3] or 0,
            'total_buy_quantity': row[4] or 0,
            'total_sell_quantity': row[5] or 0,
            'total_commission': row[6] or 0.0,
            'total_profit_loss': row[7] or 0.0,
        }
    return {}


def _get_stock_code_baostock(stock_code: str) -> str:
    """将股票代码转换为baostock格式（sz/sh + 6位数字）"""
    code = stock_code.strip().lower()
    if code.startswith(('sh', 'sz')):
        return code
    if code.startswith(('6', '9')):
        return 'sh.' + code
    else:
        return 'sz.' + code


def _fetch_from_baostock(stock_code: str) -> Optional[Dict]:
    """从 Baostock 获取股票行情数据（推荐主数据源）"""
    if not BAOSTOCK_AVAILABLE:
        return None
    try:
        bs_code = _get_stock_code_baostock(stock_code)
        # 获取最近一个交易日的日K线数据
        today = datetime.now().strftime('%Y-%m-%d')
        # baostock需要登录
        lg = bs.login()
        if lg.error_code != '0':
            logger.warning(f"baostock登录失败: {lg.error_msg}")
            return None
        try:
            # 查询最近5天数据，确保能找到交易日数据
            start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,preClose,volume,amount,pctChg",
                start_date=start_date,
                end_date=today,
                frequency="d",
                adjustflag="3"  # 不复权
            )
            if rs.error_code != '0':
                logger.warning(f"baostock查询失败: {rs.error_msg}")
                return None
            
            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                logger.warning(f"baostock未找到 {stock_code} 的数据")
                return None
            
            # 最新交易日数据
            latest = data_list[-1]
            if latest[0] is None or latest[0] == '':
                return None
            
            # 获取股票名称
            name_rs = bs.query_stock_basic(bs_code)
            stock_name = stock_code  # 默认用代码
            if name_rs.error_code == '0':
                while name_rs.next():
                    name_data = name_rs.get_row_data()
                    if name_data[1]:
                        stock_name = name_data[1]
                        break
            
            return {
                'stock_code': stock_code.upper(),
                'stock_name': stock_name,
                'opening_price': float(latest[1]) if latest[1] else 0.0,
                'closing_price': float(latest[4]) if latest[4] else 0.0,  # 当日收盘价
                'high_price': float(latest[2]) if latest[2] else 0.0,
                'low_price': float(latest[3]) if latest[3] else 0.0,
                'price_change_pct': float(latest[8]) if latest[8] else 0.0,
            }
        finally:
            bs.logout()
    except Exception as e:
        logger.warning(f"baostock获取数据失败 ({stock_code}): {e}")
        return None


def _fetch_from_sina(stock_code: str) -> Optional[Dict]:
    """从新浪财经API获取股票行情数据（免费备选数据源）"""
    try:
        # 新浪财经API格式：sh600000 或 sz000001
        code = stock_code.strip().upper()
        if code.startswith('SH') or code.startswith('SZ'):
            sina_code = code.lower()
        elif code.startswith(('6', '9')):
            sina_code = 'sh' + code
        else:
            sina_code = 'sz' + code
        
        url = f'http://hq.sinajs.cn/list={sina_code}'
        req = urllib.request.Request(url, headers={
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read().decode('gbk')
        
        if not data or '=' not in data:
            return None
        
        # 解析新浪财经返回的数据
        parts = data.split('"')
        if len(parts) < 2:
            return None
        
        values = parts[1].split(',')
        if len(values) < 32:
            return None
        
        stock_name = values[0]
        opening_price = float(values[1]) if values[1] else 0.0
        prev_close = float(values[2]) if values[2] else 0.0  # 昨收（昨日收盘价）
        current_price = float(values[3]) if values[3] else 0.0  # 当前成交价/最新价
        high_price = float(values[4]) if values[4] else 0.0
        low_price = float(values[5]) if values[5] else 0.0
        
        # 判断交易时间：如果在交易时间内（9:30-15:00），收盘价应为昨收
        # 因为当天还未收盘，没有真正的收盘价
        now = datetime.now()
        is_trading_time = False
        if now.weekday() < 5:  # 周一到周五
            hour = now.hour
            minute = now.minute
            # 上午 9:30-11:30，下午 13:00-15:00
            if (hour == 9 and minute >= 30) or (hour == 10) or (hour == 11 and minute <= 30) or \
               (hour == 13) or (hour == 14) or (hour == 15 and minute == 0):
                is_trading_time = True
        
        # 收盘前使用昨收作为参考收盘价，收盘后使用当前价
        # 但严格来说，"收盘价"应该是昨收，直到当天收盘
        closing_price = prev_close  # 昨收（昨天收盘价）
        
        # 计算涨跌幅（基于昨收）
        change_pct = 0.0
        if prev_close > 0:
            change_pct = round((current_price - prev_close) / prev_close * 100, 2)
        
        logger.info(f"新浪财经获取数据成功: {stock_name}({stock_code}), 昨收:{prev_close}, 当前:{current_price}")
        
        return {
            'stock_code': stock_code.upper(),
            'stock_name': stock_name,
            'opening_price': opening_price,
            'closing_price': closing_price,  # 昨收（昨日收盘价）
            'current_price': current_price,  # 当前最新成交价
            'high_price': high_price,
            'low_price': low_price,
            'price_change_pct': change_pct,
        }
    except Exception as e:
        logger.warning(f"新浪财经获取数据失败 ({stock_code}): {e}")
        return None


def _fetch_from_akshare(stock_code: str) -> Optional[Dict]:
    """从 AKShare 获取股票行情数据（第三备选数据源）"""
    if not AKSHARE_AVAILABLE:
        return None
    try:
        formatted = stock_code
        if not stock_code.startswith(('sh', 'sz')):
            formatted = 'sh' + stock_code if stock_code.startswith('6') else 'sz' + stock_code
        
        data = ak.stock_zh_a_spot()
        row = data[data['代码'] == formatted]
        if row.empty:
            return None
        row = row.iloc[0]
        logger.info(f"AKShare获取数据成功: {row['名称']}({stock_code})")
        return {
            'stock_code': row['代码'],
            'stock_name': row['名称'],
            'opening_price': float(row['今开']),
            'closing_price': float(row['昨收']),
            'high_price': float(row['最高']),
            'low_price': float(row['最低']),
            'price_change_pct': float(row['涨跌幅']),
        }
    except Exception as e:
        logger.warning(f"AKShare获取数据失败 ({stock_code}): {e}")
        return None


def get_stock_info(stock_code: str) -> Dict:
    """
    获取股票行情信息（多数据源策略）
    
    数据源优先级：
    1. Baostock（推荐，专为A股设计，稳定免费）
    2. 新浪财经API（免费备选，简单HTTP请求）
    3. AKShare（第三备选，部分接口已关闭）
    
    Args:
        stock_code: 股票代码（如 600000）
    
    Returns:
        包含股票信息的字典，失败返回空字典
    """
    if not stock_code:
        return {}
    
    # 目标1: Baostock - 最稳定可靠
    if BAOSTOCK_AVAILABLE:
        result = _fetch_from_baostock(stock_code)
        if result:
            logger.info(f"✓ Baostock 获取数据成功: {result['stock_name']}({stock_code})")
            return result
        logger.warning(f"✗ Baostock 获取数据失败，尝试下一个数据源...")
    
    # 目标2: 新浪财经 - 无需安装，HTTP请求即可
    result = _fetch_from_sina(stock_code)
    if result:
        logger.info(f"✓ 新浪财经 获取数据成功: {result['stock_name']}({stock_code})")
        return result
    logger.warning(f"✗ 新浪财经 获取数据失败，尝试下一个数据源...")
    
    # 目标3: AKShare - 最后尝试
    if AKSHARE_AVAILABLE:
        result = _fetch_from_akshare(stock_code)
        if result:
            logger.info(f"✓ AKShare 获取数据成功: {result['stock_name']}({stock_code})")
            return result
        logger.warning(f"✗ AKShare 获取数据失败")
    
    logger.warning(f"所有数据源均无法获取 {stock_code} 的行情数据")
    return {}


def add_trade_with_market_data(
    stock_code: str,
    trade_type: str,
    quantity: int,
    trade_price: float,
    commission_fee: float,
    trade_basis: str,
    stock_name: Optional[str] = None,
) -> int:
    info = get_stock_info(stock_code)
    if not info:
        if not stock_name:
            raise ValueError('无法获取股票信息，请提供 stock_name')
        return add_trade_record(
            stock_code=stock_code,
            stock_name=stock_name,
            trade_type=trade_type,
            quantity=quantity,
            trade_price=trade_price,
            commission_fee=commission_fee,
            trade_basis=trade_basis,
        )
    return add_trade_record(
        stock_code=stock_code,
        stock_name=stock_name or info['stock_name'],
        trade_type=trade_type,
        quantity=quantity,
        trade_price=trade_price,
        commission_fee=commission_fee,
        trade_basis=trade_basis,
        opening_price=info['opening_price'],
        closing_price=info['closing_price'],
        high_price=info['high_price'],
        low_price=info['low_price'],
    )
