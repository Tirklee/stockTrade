# -*- coding: utf-8 -*-
"""
股票数据服务层
"""
import os
import urllib.request
import urllib.error
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# 数据源可用性检测
try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    bs = None
    BAOSTOCK_AVAILABLE = False


class StockService:
    """股票数据服务类"""
    
    def __init__(self):
        self.timeout = 10
    
    def _get_stock_code_baostock(self, stock_code: str) -> str:
        """将股票代码转换为baostock格式"""
        code = stock_code.strip().lower()
        if code.startswith(('sh', 'sz')):
            return code
        if code.startswith(('6', '9')):
            return 'sh.' + code
        else:
            return 'sz.' + code
    
    def _fetch_from_baostock(self, stock_code: str) -> Optional[Dict]:
        """从Baostock获取股票数据"""
        if not BAOSTOCK_AVAILABLE:
            return None
        try:
            bs_code = self._get_stock_code_baostock(stock_code)
            lg = bs.login()
            if lg.error_code != '0':
                return None
            
            from datetime import timedelta
            today = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,preClose,volume,amount,pctChg",
                start_date=start_date,
                end_date=today,
                frequency="d",
                adjustflag="3"
            )
            
            if rs.error_code != '0':
                bs.logout()
                return None
            
            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())
            
            bs.logout()
            
            if not data_list:
                return None
            
            latest = data_list[-1]
            return {
                'stock_code': stock_code.upper(),
                'stock_name': stock_code,
                'opening_price': float(latest[1]) if latest[1] else 0.0,
                'closing_price': float(latest[4]) if latest[4] else 0.0,
                'high_price': float(latest[2]) if latest[2] else 0.0,
                'low_price': float(latest[3]) if latest[3] else 0.0,
                'price_change_pct': float(latest[8]) if latest[8] else 0.0,
            }
        except Exception as e:
            logger.warning(f"Baostock获取数据失败: {e}")
            return None
    
    def _fetch_from_sina(self, stock_code: str) -> Optional[Dict]:
        """从新浪财经API获取股票数据"""
        try:
            code = stock_code.strip().upper()
            if code.startswith(('SH', 'SZ')):
                sina_code = code.lower()
            elif code.startswith(('6', '9')):
                sina_code = 'sh' + code
            else:
                sina_code = 'sz' + code
            
            url = f'http://hq.sinajs.cn/list={sina_code}'
            req = urllib.request.Request(url, headers={
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0'
            })
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = response.read().decode('gbk')
            
            if '=' not in data:
                return None
            
            parts = data.split('"')
            if len(parts) < 2:
                return None
            
            values = parts[1].split(',')
            if len(values) < 32:
                return None
            
            stock_name = values[0]
            opening_price = float(values[1]) if values[1] else 0.0
            prev_close = float(values[2]) if values[2] else 0.0
            current_price = float(values[3]) if values[3] else 0.0
            high_price = float(values[4]) if values[4] else 0.0
            low_price = float(values[5]) if values[5] else 0.0
            
            change_pct = 0.0
            if prev_close > 0:
                change_pct = round((current_price - prev_close) / prev_close * 100, 2)
            
            return {
                'stock_code': stock_code.upper(),
                'stock_name': stock_name,
                'opening_price': opening_price,
                'closing_price': prev_close,
                'current_price': current_price,
                'high_price': high_price,
                'low_price': low_price,
                'price_change_pct': change_pct,
            }
        except Exception as e:
            logger.warning(f"新浪财经获取数据失败: {e}")
            return None
    
    def get_stock_info(self, stock_code: str) -> Dict:
        """获取股票信息"""
        if not stock_code:
            return {}
        
        # 优先使用baostock
        if BAOSTOCK_AVAILABLE:
            result = self._fetch_from_baostock(stock_code)
            if result:
                return result
        
        # 备选新浪财经
        result = self._fetch_from_sina(stock_code)
        if result:
            return result
        
        return {}
    
    def get_realtime_data(self, code: str) -> Dict:
        """获取实时行情"""
        return self.get_stock_info(code)
    
    def identify_stock_type(self, code: str) -> Dict:
        """识别股票类型"""
        code = code.strip().upper()
        if code.startswith(('6', '9')):
            return {'type': 'stock', 'market': 'sh', 'code': code}
        elif code.startswith(('0', '3')):
            return {'type': 'stock', 'market': 'sz', 'code': code}
        elif code.startswith('5') and len(code) == 6:
            return {'type': 'fund', 'market': 'sh', 'code': code}
        elif code.startswith('1') and len(code) == 6:
            return {'type': 'fund', 'market': 'sz', 'code': code}
        return {'type': 'stock', 'market': 'unknown', 'code': code}
    
    def search_stocks(self, name: str) -> List[Dict]:
        """搜索股票"""
        # 新浪搜索API
        try:
            url = f'https://suggest3.sinajs.cn/suggest/type=11,12,13,14,15,17,18,19,20,21,22,23,24,25,31,41&key={name}&encoding=gbk'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read().decode('gbk')
            
            results = []
            if '=' in data:
                parts = data.split('"')
                if len(parts) >= 2:
                    items = parts[1].split(';')
                    for item in items:
                        if item.strip():
                            fields = item.split(',')
                            if len(fields) >= 3:
                                results.append({
                                    'stock_code': fields[2],
                                    'stock_name': fields[3] if len(fields) > 3 else fields[2],
                                    'type': fields[0] if len(fields) > 0 else ''
                                })
            return results[:20]
        except Exception as e:
            logger.warning(f"股票搜索失败: {e}")
            return []