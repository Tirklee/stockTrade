# -*- coding: utf-8 -*-
"""
财经新闻服务
"""
import requests
from datetime import datetime
from flask import current_app


class NewsService:
    """财经新闻服务 - 通过后端代理获取数据解决CORS问题"""

    # 新浪财经新闻接口
    SINA_NEWS_URL = 'https://finance.sina.com.cn/js/{}.js'

    # 东方财富快讯
    EAST_MONEY_KUAIXUN = 'https://newsapi.eastmoney.com/kuaixun/v1/getnewslist.aspx'

    # 同花顺财经
    THS_NEWS_URL = 'https://news.10jqka.com.cn/tapp/news/push/stock/?page=1&tag=&track=website&pagesize=20'

    @classmethod
    def _format_timestamp(cls, timestamp):
        """将时间戳转换为可读日期格式"""
        if not timestamp:
            return ''
        try:
            # 如果是数字字符串，转为int
            if isinstance(timestamp, str):
                timestamp = int(timestamp)
            # 10位时间戳（秒）
            if timestamp > 1e12:
                timestamp = timestamp // 1000
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return str(timestamp)

    @classmethod
    def get_financial_news(cls, news_type='news', page=1, page_size=10):
        """
        获取财经新闻（通过后端代理避免CORS问题）

        Args:
            news_type: news-财经新闻, policy-政策, economic-经济数据
            page: 页码
            page_size: 每页数量

        Returns:
            新闻列表
        """
        try:
            # 使用同花顺新闻接口（相对稳定）
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://news.10jqka.com.cn',
                'Accept': 'application/json, text/plain, */*'
            }

            url = f'https://news.10jqka.com.cn/tapp/news/push/stock/?page=1&tag=&track=website&pagesize={page_size}'

            if news_type == 'policy':
                url = f'https://news.10jqka.com.cn/tapp/news/push/policy/?page=1&tag=&track=website&pagesize={page_size}'
            elif news_type == 'economic':
                url = f'https://news.10jqka.com.cn/tapp/news/push/macro/?page=1&tag=&track=website&pagesize={page_size}'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                news_list = []

                items = result.get('data', {}).get('list', []) or result.get('data', []) or []

                for item in items:
                    # 统一处理不同接口的数据格式
                    raw_date = item.get('ctime', item.get('publish_time', ''))
                    news_list.append({
                        'title': item.get('title', item.get('z_title', '')),
                        'source': item.get('media', item.get('author', '同花顺')),
                        'date': cls._format_timestamp(raw_date),
                        'url': item.get('url', item.get('artical_url', '#')),
                        'digest': item.get('summary', item.get('digest', ''))
                    })

                return {
                    'success': True,
                    'data': news_list,
                    'total': len(news_list)
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }

        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def get_important_events(cls):
        """
        获取影响股市的重大事件（公告、研报等）
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            # 使用东方财富公告接口
            url = 'https://np-anotice-stock.eastmoney.com/api/security/ann'
            params = {
                'sr': '-1',
                'page_size': 20,
                'page_index': 1,
                'ann_type': 'A,SH,sz,sse,bse,cjs',
                'client_source': 'web'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                events = []

                for item in result.get('data', {}).get('list', []):
                    events.append({
                        'title': item.get('title', ''),
                        'source': item.get('sim_src', '公告'),
                        'date': item.get('notice_date', '')[:10] if item.get('notice_date') else '',
                        'url': f"https://data.eastmoney.com/notices/{item.get('id', '')}.html"
                    })

                return {'success': True, 'data': events}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    @classmethod
    def get_market_news(cls):
        """
        获取市场动态新闻（涨停、跌停、板块热点等）
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            # 使用东方财富市场快讯
            url = 'https://newsapi.eastmoney.com/kuaixun/v1/getnewslist.aspx'
            params = {
                'page': 1,
                'pageSize': 20,
                'type': '',
                '_': int(datetime.now().timestamp() * 1000)
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                news_list = []

                for item in result.get('result', {}).get('items', []):
                    news_list.append({
                        'title': item.get('title', ''),
                        'source': item.get('source', '东方财富'),
                        'date': item.get('showtime', ''),
                        'url': item.get('url', ''),
                        'digest': item.get('digest', '')
                    })

                return {'success': True, 'data': news_list}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}