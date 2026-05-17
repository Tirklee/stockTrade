# -*- coding: utf-8 -*-
"""
交易服务测试

测试交易记录的增删改查功能
"""
import pytest
from app.services.trade_service import TradeService
from app.database import get_db_connection


class TestTradeService:
    """交易服务测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前初始化"""
        self.service = TradeService()
    
    def test_add_trade_success(self, sample_trade_data):
        """测试添加交易记录成功"""
        success, message = self.service.add_trade(sample_trade_data)
        assert success is True
        assert "成功" in message
    
    def test_add_trade_minimal_data(self):
        """测试最小数据添加"""
        data = {
            'stock_name': '测试股票',
            'trade_type': 'buy',
            'quantity': 100,
            'trade_price': 10.0,
            'trade_basis': '测试'
        }
        success, message = self.service.add_trade(data)
        assert success is True
    
    def test_add_trade_invalid_type(self):
        """测试无效的交易类型"""
        data = {
            'stock_name': '测试股票',
            'trade_type': 'invalid',
            'quantity': 100,
            'trade_price': 10.0,
            'trade_basis': '测试'
        }
        success, message = self.service.add_trade(data)
        assert success is False
    
    def test_get_trades_empty(self):
        """测试获取空列表"""
        trades, total = self.service.get_trades(page=1, per_page=10)
        assert isinstance(trades, list)
        assert total >= 0
    
    def test_get_trades_with_data(self, sample_trade_data):
        """测试获取有数据的列表"""
        # 先添加数据
        self.service.add_trade(sample_trade_data)
        
        trades, total = self.service.get_trades(page=1, per_page=10)
        assert len(trades) > 0
        assert total >= 1
    
    def test_get_trades_pagination(self):
        """测试分页功能"""
        trades, total = self.service.get_trades(page=1, per_page=5)
        assert len(trades) <= 5
        
        trades, total = self.service.get_trades(page=2, per_page=5)
        assert isinstance(trades, list)
    
    def test_update_trade_not_found(self):
        """测试更新不存在的记录"""
        data = {
            'stock_name': '修改后的名称',
            'trade_type': 'buy',
            'quantity': 100,
            'trade_price': 10.0,
            'trade_basis': '测试'
        }
        success, message = self.service.update_trade(99999, data)
        assert success is False
    
    def test_delete_trade_not_found(self):
        """测试删除不存在的记录"""
        success, message = self.service.delete_trade(99999)
        assert success is False


class TestTradeServicePNL:
    """持仓盈亏计算测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """初始化"""
        self.service = TradeService()
    
    def test_calculate_position_pnl_empty(self):
        """测试空持仓计算"""
        result = self.service.calculate_position_pnl('NONEXISTENT')
        assert result['position_qty'] == 0
        assert result['total_buy'] == 0
    
    def test_calculate_position_pnl_with_data(self, sample_trade_data):
        """测试有数据的持仓计算"""
        # 添加买入记录
        self.service.add_trade(sample_trade_data)
        
        result = self.service.calculate_position_pnl('600000')
        assert result['position_qty'] >= 0
        assert 'positions' in result


class TestTradeServiceBulk:
    """批量操作测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """初始化"""
        self.service = TradeService()
    
    def test_bulk_delete_empty(self):
        """测试批量删除空列表"""
        success, message = self.service.bulk_delete([])
        assert success is False
    
    def test_bulk_delete_invalid_ids(self):
        """测试批量删除无效ID"""
        success, message = self.service.bulk_delete([99999, 99998])
        assert success is True  # 即使ID不存在也返回成功
    
    def test_bulk_update_empty(self):
        """测试批量更新空列表"""
        success, message = self.service.bulk_update([], {'trade_basis': 'test'})
        assert success is False