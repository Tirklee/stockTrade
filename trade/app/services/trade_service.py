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
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN trade_type='buy' THEN quantity * trade_price ELSE 0 END) as total_buy,
                SUM(CASE WHEN trade_type='sell' THEN quantity * trade_price ELSE 0 END) as total_sell,
                SUM(CASE WHEN trade_type='buy' THEN quantity ELSE 0 END) as buy_qty,
                SUM(CASE WHEN trade_type='sell' THEN quantity ELSE 0 END) as sell_qty
            FROM trade_records WHERE stock_code = ?
        ''', (stock_code.upper(),))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'total_buy': row[0] or 0,
                'total_sell': row[1] or 0,
                'position_qty': (row[2] or 0) - (row[3] or 0)
            }
        return {'total_buy': 0, 'total_sell': 0, 'position_qty': 0}