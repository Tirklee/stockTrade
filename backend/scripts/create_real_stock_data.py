# -*- coding: utf-8 -*-
"""
生成真实股票代码的模拟数据
使用沪深交易所公开的真实股票代码
"""
import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import TradeRecord, Position, Broker


# 真实A股股票代码列表（按行业分类）
REAL_STOCKS = {
    # 白酒
    '600519': '贵州茅台', '000858': '五粮液', '000568': '泸州老窖', '000596': '古井贡酒',
    '603589': '口子窖', '603369': '今世缘', '000799': '酒鬼酒', '600809': '山西汾酒',
    '600197': '伊力特', '002304': '洋河股份',

    # 银行
    '600000': '浦发银行', '600036': '招商银行', '601166': '兴业银行', '601398': '工商银行',
    '601939': '建设银行', '601288': '农业银行', '601988': '中国银行', '600016': '民生银行',
    '600919': '江苏银行', '600926': '杭州银行', '002142': '宁波银行', '002807': '江阴银行',
    '002948': '青岛银行', '600908': '无锡银行', '600928': '西安银行',

    # 证券
    '600030': '中信证券', '600837': '海通证券', '601211': '国泰君安', '601688': '华泰证券',
    '000776': '广发证券', '000166': '申万宏源', '600999': '招商证券', '601108': '财通证券',
    '000712': '锦龙股份', '000686': '东北证券', '600369': '西南证券', '601555': '东吴证券',

    # 保险
    '601318': '中国平安', '601628': '中国人寿', '601601': '中国太保', '601336': '新华保险',

    # 科技/芯片
    '600584': '长电科技', '002185': '华天科技', '002456': '欧菲光', '000725': '京东方A',
    '002049': '紫光国微', '603986': '兆易创新', '688981': '中芯国际', '002371': '北方华创',
    '300782': '卓胜微', '688256': '寒武纪', '688008': '澜起科技', '002230': '科大讯飞',

    # 新能源
    '300750': '宁德时代', '002594': '比亚迪', '600438': '通威股份', '601012': '隆基绿能',
    '002129': '中环股份', '300014': '亿纬锂能', '300274': '阳光电源', '600089': '特变电工',

    # 医药
    '600276': '恒瑞医药', '000538': '云南白药', '300760': '迈瑞医疗', '688180': '君实生物',
    '603259': '药明康德', '000661': '长春高新', '002007': '华兰生物', '300015': '爱尔眼科',
    '300003': '乐普医疗', '600196': '复星医药',

    # 食品消费
    '000895': '双汇发展', '603288': '海天味业', '600887': '伊利股份', '002714': '牧原股份',
    '002311': '海大集团', '603517': '绝味食品', '000876': '新希望', '002507': '涪陵榨菜',

    # 白电/家电
    '000333': '美的集团', '000651': '格力电器', '600690': '海尔智家', '002032': '苏泊尔',
    '002242': '九阳股份', '000521': '长虹美菱', '600839': '四川长虹',

    # 房地产
    '000002': '万科A', '001979': '招商蛇口', '600048': '保利发展', '600383': '金地集团',
    '600606': '绿地控股', '000402': '金融街', '600663': '陆家嘴', '600376': '首开股份',

    # 基建/建筑
    '601668': '中国建筑', '601390': '中国中铁', '601186': '中国铁建', '601766': '中国中车',
    '601618': '中国中冶', '600170': '上海建工', '600320': '振华重工',

    # 电力/能源
    '600900': '长江电力', '600905': '三峡能源', '600025': '华能水电', '600886': '国投电力',
    '600795': '国电电力', '601985': '中国核电', '600642': '申能股份',

    # 汽车
    '600104': '上汽集团', '000625': '长安汽车', '600660': '福耀玻璃', '002126': '银轮股份',
    '601238': '广汽集团', '000550': '江铃汽车', '002488': '金固股份',

    # 通信
    '601728': '中国电信', '600050': '中国联通', '000063': '中兴通讯', '600498': '烽火通信',
    '002465': '海格通信', '300136': '信维通信',

    # 化工
    '600309': '万华化学', '002601': '龙佰集团', '600352': '浙江龙盛', '000830': '鲁西化工',
    '601216': '君正集团', '002092': '中泰化学',

    # 军工
    '600893': '航发动力', '600316': '洪都航空', '600760': '中航沈飞', '600765': '中航重机',
    '000738': '航发控制', '002013': '中航机电', '600038': '中直股份',

    # 交通运输
    '601021': '春秋航空', '600115': '东方航空', '600029': '南方航空', '601111': '中国国航',
    '601333': '广深铁路', '601006': '大秦铁路', '600018': '上港集团', '601018': '宁波港',

    # 传媒/互联网
    '300059': '东方财富', '300124': '汇川技术', '002027': '分众传媒', '603444': '吉比特',
    '300033': '同花顺', '002558': '巨人网络', '300226': '上海钢联',

    # 机械设备
    '601100': '恒立液压', '002097': '山河智能', '600582': '天地科技', '002048': '宁波华翔',
    '002202': '金风科技', '601369': '陕鼓动力',

    # 煤炭
    '601088': '中国神华', '600188': '兖矿能源', '600971': '恒源煤电', '000552': '靖远煤电',
    '601001': '晋控煤业', '600395': '盘江股份',

    # 钢铁
    '600019': '宝钢股份', '000898': '鞍钢股份', '002110': '三钢闽光', '000709': '河钢股份',
    '600022': '山东钢铁', '601969': '海南矿业',

    # 白酒龙头和稀缺
    '000001': '平安银行', '600036': '招商银行', '601318': '中国平安',
}


def create_real_stock_data(record_count=10000):
    """创建使用真实股票代码的模拟数据"""
    app = create_app()

    with app.app_context():
        print("开始创建真实股票代码的模拟数据...")

        # 清空现有数据
        db.session.query(TradeRecord).delete()
        db.session.query(Position).delete()
        db.session.commit()
        print("已清空现有数据")

        # 获取真实股票列表
        stocks = [{'code': code, 'name': name} for code, name in REAL_STOCKS.items()]
        print(f"已加载 {len(stocks)} 只真实股票")

        # 获取券商ID
        broker = Broker.query.first()
        broker_id = broker.id if broker else 1

        # 交易理由库
        trade_reasons = [
            '价值投资', '成长性强', '行业龙头', '估值合理', '技术突破',
            '业绩预增', '政策利好', '市场份额提升', '技术护城河', '现金流充沛',
            '分红优厚', '重组预期', '产能扩张', '出口增长', '国产替代',
            '消费升级', '产业整合', '技术领先', '资源稀缺', '政策支持'
        ]

        print(f"开始生成 {record_count} 条交易记录...")

        # 批量创建交易记录
        batch_size = 1000
        for batch_start in range(0, record_count, batch_size):
            batch_end = min(batch_start + batch_size, record_count)
            batch_trades = []

            for _ in range(batch_start, batch_end):
                stock = random.choice(stocks)
                trade_type = random.choice(['buy', 'buy', 'buy', 'sell'])  # 买入更多
                days_ago = random.randint(0, 365)
                # 随机股数
                quantity = random.choice([100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000])
                # 根据股票类型确定合理价格范围
                base_prices = {
                    '600519': 1600, '000858': 140, '600036': 35, '601318': 45,
                    '000001': 12, '300750': 200, '688981': 50, '000725': 4,
                }
                base_price = base_prices.get(stock['code'], random.uniform(5.0, 300.0))
                # 添加一些随机波动
                unit_price = round(base_price * random.uniform(0.85, 1.15), 2)
                total_amount = round(unit_price * quantity, 2)
                commission = max(5.0, total_amount * 0.0003)
                stamp_tax = total_amount * 0.001 if trade_type == 'sell' else 0
                transfer_fee = total_amount * 0.00002

                trade = TradeRecord(
                    trade_time=datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23)),
                    stock_code=stock['code'],
                    stock_name=stock['name'],
                    asset_type='stock',
                    trade_type=trade_type,
                    quantity=quantity,
                    unit_price=Decimal(str(unit_price)),
                    total_amount=Decimal(str(total_amount)),
                    commission=Decimal(str(round(commission, 2))),
                    stamp_tax=Decimal(str(round(stamp_tax, 2))),
                    transfer_fee=Decimal(str(round(transfer_fee, 4))),
                    total_fee=Decimal(str(round(commission + stamp_tax + transfer_fee, 2))),
                    broker_id=broker_id,
                    trade_basis=random.choice(trade_reasons)
                )
                batch_trades.append(trade)

            db.session.bulk_save_objects(batch_trades)
            db.session.commit()
            print(f"  已创建 {batch_end} 条交易记录")

        total_trades = TradeRecord.query.count()
        print(f"交易记录总数: {total_trades}")

        # 汇总股票买入数量，计算持仓
        print("正在计算持仓数据...")

        from sqlalchemy import func, case

        net_qty = func.sum(
            case((TradeRecord.trade_type == 'buy', TradeRecord.quantity), else_=-TradeRecord.quantity)
        ).label('net_quantity')

        stock_summary = db.session.query(
            TradeRecord.stock_code,
            TradeRecord.stock_name,
            net_qty,
            func.avg(TradeRecord.unit_price).label('avg_price')
        ).group_by(
            TradeRecord.stock_code,
            TradeRecord.stock_name
        ).having(net_qty > 0).all()

        print(f"共有 {len(stock_summary)} 只股票有持仓")

        # 创建持仓数据
        for summary in stock_summary:
            # 从真实股票数据中获取当前价格的合理估算
            base_prices = {
                '600519': 1650, '000858': 145, '600036': 35, '601318': 45,
                '000001': 12, '300750': 205, '688981': 52, '000725': 4.2,
                '600000': 8, '601166': 17, '601398': 5.8, '000568': 180,
                '600030': 21, '603288': 75, '000895': 30, '600690': 28,
                '000333': 60, '000651': 40, '600104': 14, '002594': 260,
                '600584': 28, '002185': 12, '002049': 120, '603986': 110,
                '600438': 38, '601012': 28, '002129': 10, '300274': 90,
                '600276': 48, '000538': 55, '300760': 280, '603259': 85,
            }
            base_price = base_prices.get(summary.stock_code, float(summary.avg_price) if summary.avg_price else 50)
            current_price = round(base_price * random.uniform(0.98, 1.02), 2)
            total_quantity = summary.net_quantity
            total_cost = round(float(summary.avg_price) * total_quantity, 2)
            current_value = round(current_price * total_quantity, 2)
            unrealized_pnl = round(current_value - total_cost, 2)
            unrealized_pnl_rate = round((unrealized_pnl / total_cost * 100), 2) if total_cost > 0 else 0

            position = Position(
                stock_code=summary.stock_code,
                stock_name=summary.stock_name,
                asset_type='stock',
                total_quantity=total_quantity,
                available_quantity=total_quantity,
                frozen_quantity=0,
                avg_cost=Decimal(str(round(summary.avg_price, 2))),
                total_cost=Decimal(str(total_cost)),
                current_price=Decimal(str(current_price)),
                current_value=Decimal(str(current_value)),
                unrealized_pnl=Decimal(str(unrealized_pnl)),
                unrealized_pnl_rate=Decimal(str(unrealized_pnl_rate))
            )
            db.session.add(position)

        db.session.commit()
        print("持仓数据已创建")

        print("\n" + "=" * 60)
        print("模拟数据创建完成！")
        print("=" * 60)


if __name__ == '__main__':
    create_real_stock_data()