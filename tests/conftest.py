# -*- coding: utf-8 -*-
"""
pytest 测试配置

提供测试所需的 fixtures 和配置
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.database import init_database, get_db_connection


@pytest.fixture(scope='session')
def app():
    """创建测试用的 Flask 应用实例"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture(scope='session')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_connection():
    """提供数据库连接的 fixture"""
    with get_db_connection() as conn:
        yield conn


@pytest.fixture(scope='function', autouse=True)
def setup_database():
    """每个测试前初始化数据库"""
    init_database()
    yield
    # 测试后清理（如果需要）


@pytest.fixture
def sample_trade_data():
    """提供示例交易数据"""
    return {
        'stock_code': '600000',
        'stock_name': '浦发银行',
        'trade_type': 'buy',
        'quantity': 100,
        'trade_price': 10.5,
        'commission_fee': 3.15,
        'trade_basis': '技术分析买入',
        'trade_time': '2024-01-15 10:30:00'
    }