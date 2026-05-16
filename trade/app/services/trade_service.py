# -*- coding: utf-8 -*-
"""
交易记录服务层
"""
import os
import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_FILE = os.path.join(BASE_DIR, 'stock_trades.db')


def init_database():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trade_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_time TIMESTAMP NOT NULL,
        stock_code TEXT,
        stock_name TEXT NOT NULL,
        asset_type TEXT NOT NULL DEFAULT 'stock',
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
    conn.commit()
    conn.close()


class TradeService:
    """交易记录服务类"""
    
    def __init__(self):
        init_database()
    
    def get_trades(self, stock_code: str = None, page: int = 1, per_page: int = 10) -> tuple:
        """获取交易记录列表"""
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        offset = (page - 1) * per_page
        params = []
        where = ""
        
        if stock_code:
            where = "WHERE stock_code LIKE ?"
            params = [f'%{stock_code.upper()}%']
        
        cursor.execute(f'''
            SELECT * FROM trade_records {where}
            ORDER BY trade_time DESC
            LIMIT ? OFFSET ?
        ''', params + [per_page, offset])
        
        trades = [dict(row) for row in cursor.fetchall()]
        
        # 统计总数
        cursor.execute(f'SELECT COUNT(*) FROM trade_records {where}', params)
        total = cursor.fetchone()[0]
        
        conn.close()
        return trades, total
    
    def get_trade(self, trade_id: int) -> Optional[Dict]:
        """获取单条记录"""
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM trade_records WHERE id = ?', (trade_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def add_trade(self, data: Dict) -> tuple:
        """添加交易记录"""
        try:
            trade_time = data.get('trade_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trade_records
                (trade_time, stock_code, stock_name, asset_type, trade_type, quantity,
                 opening_price, closing_price, high_price, low_price, trade_price, 
                 commission_fee, profit_loss, profit_loss_reason, trade_basis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_time,
                data.get('stock_code', '').upper() if data.get('stock_code') else None,
                data.get('stock_name', ''),
                data.get('asset_type', 'stock'),
                data.get('trade_type', '').lower(),
                int(data.get('quantity', 0)),
                float(data.get('opening_price') or 0),
                float(data.get('closing_price') or 0),
                float(data.get('high_price') or 0),
                float(data.get('low_price') or 0),
                float(data.get('trade_price', 0)),
                float(data.get('commission_fee', 0)),
                float(data.get('profit_loss') or 0),
                data.get('profit_loss_reason', ''),
                data.get('trade_basis', ''),
            ))
            conn.commit()
            conn.close()
            return True, "添加成功"
        except Exception as e:
            return False, str(e)
    
    def update_trade(self, trade_id: int, data: Dict) -> tuple:
        """更新交易记录"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE trade_records SET
                    trade_time = ?, stock_code = ?, stock_name = ?, asset_type = ?,
                    trade_type = ?, quantity = ?, opening_price = ?, closing_price = ?,
                    high_price = ?, low_price = ?, trade_price = ?, commission_fee = ?,
                    profit_loss = ?, profit_loss_reason = ?, trade_basis = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('trade_time'),
                data.get('stock_code', '').upper() if data.get('stock_code') else None,
                data.get('stock_name', ''),
                data.get('asset_type', 'stock'),
                data.get('trade_type', '').lower(),
                int(data.get('quantity', 0)),
                float(data.get('opening_price') or 0),
                float(data.get('closing_price') or 0),
                float(data.get('high_price') or 0),
                float(data.get('low_price') or 0),
                float(data.get('trade_price', 0)),
                float(data.get('commission_fee', 0)),
                float(data.get('profit_loss') or 0),
                data.get('profit_loss_reason', ''),
                data.get('trade_basis', ''),
                trade_id
            ))
            conn.commit()
            conn.close()
            return True, "更新成功"
        except Exception as e:
            return False, str(e)
    
    def delete_trade(self, trade_id: int) -> tuple:
        """删除交易记录"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM trade_records WHERE id = ?', (trade_id,))
            conn.commit()
            conn.close()
            return True, "删除成功"
        except Exception as e:
            return False, str(e)
    
    def bulk_delete(self, ids: List[int]) -> tuple:
        """批量删除"""
        try:
            if not ids:
                return False, "没有选中记录"
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(ids))
            cursor.execute(f'DELETE FROM trade_records WHERE id IN ({placeholders})', ids)
            conn.commit()
            conn.close()
            return True, f"删除了 {cursor.rowcount} 条记录"
        except Exception as e:
            return False, str(e)
    
    def bulk_update(self, ids: List[int], updates: Dict) -> tuple:
        """批量更新"""
        try:
            if not ids:
                return False, "没有选中记录"
            set_clauses = []
            params = []
            for key, value in updates.items():
                if value is not None:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            if not set_clauses:
                return False, "没有要更新的字段"
            
            params.extend(ids)
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(ids))
            cursor.execute(
                f'UPDATE trade_records SET {", ".join(set_clauses)} WHERE id IN ({placeholders})',
                params
            )
            conn.commit()
            conn.close()
            return True, f"更新了 {cursor.rowcount} 条记录"
        except Exception as e:
            return False, str(e)
    
    def calculate_position_pnl(self, stock_code: str) -> Dict:
        """计算持仓盈亏"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 获取所有交易记录
        cursor.execute('''
            SELECT id, trade_time, trade_type, quantity, trade_price, stock_name
            FROM trade_records 
            WHERE stock_code = ?
            ORDER BY trade_time ASC
        ''', (stock_code.upper(),))
        
        records = cursor.fetchall()
        
        if not records:
            conn.close()
            return {
                'total_buy': 0,
                'total_sell': 0,
                'position_qty': 0,
                'positions': [],
                'avg_cost': 0,
                'current_pnl': 0,
                'current_pnl_rate': 0
            }
        
        # 计算持仓
        total_buy = 0
        total_sell = 0
        buy_qty = 0
        sell_qty = 0
        positions = []
        
        for record in records:
            trade_id, trade_time, trade_type, quantity, trade_price, stock_name = record
            
            if trade_type == 'buy':
                total_buy += quantity * trade_price
                buy_qty += quantity
            else:
                total_sell += quantity * trade_price
                sell_qty += quantity
        
        # 计算持仓数量和平均成本
        position_qty = buy_qty - sell_qty
        avg_cost = total_buy / buy_qty if buy_qty > 0 else 0
        
        # 获取当前价格
        from app.services.stock_service import StockService
        stock_service = StockService()
        realtime = stock_service.get_realtime_data(stock_code.upper())
        current_price = realtime.get('current', avg_cost) if not realtime.get('error') else avg_cost
        
        # 计算持仓市值和盈亏
        position_value = position_qty * current_price
        total_cost = position_qty * avg_cost
        current_pnl = position_value - total_cost
        current_pnl_rate = (current_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # 生成持仓明细（按买入记录计算）
        cursor.execute('''
            SELECT id, trade_time, trade_type, quantity, trade_price
            FROM trade_records 
            WHERE stock_code = ? AND trade_type = 'buy'
            ORDER BY trade_time ASC
        ''', (stock_code.upper(),))
        
        buy_records = cursor.fetchall()
        remaining_qty = position_qty
        
        for record in buy_records:
            if remaining_qty <= 0:
                break
            trade_id, trade_time, trade_type, quantity, trade_price = record
            pos_qty = min(quantity, remaining_qty)
            cost_price = trade_price
            pnl = (current_price - cost_price) * pos_qty
            pnl_rate = ((current_price - cost_price) / cost_price * 100) if cost_price > 0 else 0
            
            positions.append({
                'trade_id': trade_id,
                'trade_time': trade_time[:10] if trade_time else '',
                'trade_type': trade_type,
                'quantity': pos_qty,
                'cost_price': cost_price,
                'current_price': current_price,
                'pnl': pnl,
                'pnl_rate': pnl_rate
            })
            
            remaining_qty -= pos_qty
        
        conn.close()
        
        return {
            'total_buy': total_buy,
            'total_sell': total_sell,
            'position_qty': position_qty,
            'avg_cost': avg_cost,
            'current_price': current_price,
            'position_value': position_value,
            'current_pnl': current_pnl,
            'current_pnl_rate': current_pnl_rate,
            'positions': positions,
            'stock_name': stock_name
        }
    
    def calculate_portfolio_summary(self) -> Dict:
        """计算总体账户盈亏"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 获取所有股票代码
        cursor.execute('SELECT DISTINCT stock_code FROM trade_records WHERE stock_code IS NOT NULL')
        stock_codes = [row[0] for row in cursor.fetchall()]
        
        total_assets = 0  # 持仓市值
        total_cost = 0    # 总成本
        total_pnl = 0     # 总盈亏
        
        from app.services.stock_service import StockService
        stock_service = StockService()
        
        for stock_code in stock_codes:
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN trade_type='buy' THEN quantity ELSE 0 END) as buy_qty,
                    SUM(CASE WHEN trade_type='buy' THEN quantity * trade_price ELSE 0 END) as buy_amount,
                    SUM(CASE WHEN trade_type='sell' THEN quantity ELSE 0 END) as sell_qty,
                    SUM(CASE WHEN trade_type='sell' THEN quantity * trade_price ELSE 0 END) as sell_amount
                FROM trade_records WHERE stock_code = ?
            ''', (stock_code,))
            
            row = cursor.fetchone()
            buy_qty = row[0] or 0
            buy_amount = row[1] or 0
            sell_qty = row[2] or 0
            sell_amount = row[3] or 0
            
            position_qty = buy_qty - sell_qty
            if position_qty <= 0:
                continue
            
            avg_cost = buy_amount / buy_qty if buy_qty > 0 else 0
            
            # 获取当前价格
            realtime = stock_service.get_realtime_data(stock_code)
            current_price = realtime.get('current', avg_cost) if not realtime.get('error') else avg_cost
            
            position_value = position_qty * current_price
            position_cost = position_qty * avg_cost
            
            total_assets += position_value
            total_cost += position_cost
        
        total_pnl = total_assets - total_cost
        pnl_rate = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        conn.close()
        
        return {
            'total_assets': total_assets,
            'total_cost': total_cost,
            'total_pnl': total_pnl,
            'pnl_rate': pnl_rate
        }
    
    def sell_stock(self, data: Dict) -> tuple:
        """卖出股票"""
        try:
            stock_code = data.get('stock_code', '').upper()
            stock_name = data.get('stock_name', '')
            quantity = int(data.get('quantity', 0))
            trade_price = float(data.get('trade_price', 0))
            commission_fee = float(data.get('commission_fee', 0))
            trade_basis = data.get('trade_basis', '')
            
            if not stock_code or quantity <= 0 or trade_price <= 0:
                return False, '参数错误', None
            
            trade_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trade_records
                (trade_time, stock_code, stock_name, asset_type, trade_type, quantity,
                 trade_price, commission_fee, profit_loss, trade_basis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_time,
                stock_code,
                stock_name,
                'stock',
                'sell',
                quantity,
                trade_price,
                commission_fee,
                0,  # 卖出时不计算盈亏
                trade_basis
            ))
            
            trade_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return True, '卖出成功', trade_id
        except Exception as e:
            logger.error(f'卖出失败: {e}')
            return False, str(e), None
