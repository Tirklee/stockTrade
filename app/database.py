# -*- coding: utf-8 -*-
"""
数据库初始化和管理模块

统一管理数据库的创建、初始化和连接
"""
import sqlite3
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from app.config import Config

logger = logging.getLogger(__name__)

# 数据库文件路径
DB_FILE = Config.get_db_path()


def init_database() -> None:
    """
    初始化数据库表
    
    创建必要的数据库表和索引
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # 创建交易记录表
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
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code ON trade_records(stock_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_time ON trade_records(trade_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_type ON trade_records(trade_type)')
        
        conn.commit()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        conn.close()


@contextmanager
def get_db_connection():
    """
    获取数据库连接的上下文管理器
    
    用法:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 执行数据库操作
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            conn.close()


def get_database_info() -> dict:
    """
    获取数据库信息
    
    Returns:
        包含数据库信息的字典
    """
    db_path = Path(DB_FILE)
    
    info = {
        'path': str(db_path),
        'exists': db_path.exists(),
        'size_bytes': 0,
        'size_mb': 0,
        'table_count': 0,
        'record_count': 0
    }
    
    if db_path.exists():
        info['size_bytes'] = db_path.stat().st_size
        info['size_mb'] = round(info['size_bytes'] / (1024 * 1024), 2)
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 获取表数量
                cursor.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                )
                info['table_count'] = cursor.fetchone()[0]
                
                # 获取记录数量
                cursor.execute(
                    "SELECT COUNT(*) FROM trade_records"
                )
                info['record_count'] = cursor.fetchone()[0]
        except Exception as e:
            logger.warning(f"获取数据库信息失败: {e}")
    
    return info


def backup_database(backup_path: Optional[str] = None) -> str:
    """
    备份数据库
    
    Args:
        backup_path: 备份文件路径，如果为None则自动生成
        
    Returns:
        备份文件的完整路径
    """
    import shutil
    from datetime import datetime
    
    if backup_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = str(Path(DB_FILE).parent / f'stock_trades_backup_{timestamp}.db')
    
    shutil.copy2(DB_FILE, backup_path)
    logger.info(f"数据库已备份到: {backup_path}")
    
    return backup_path


if __name__ == '__main__':
    # 初始化数据库
    print("初始化数据库...")
    init_database()
    
    # 显示数据库信息
    info = get_database_info()
    print(f"\n数据库信息:")
    print(f"  路径: {info['path']}")
    print(f"  大小: {info['size_mb']} MB")
    print(f"  表数量: {info['table_count']}")
    print(f"  记录数量: {info['record_count']}")