# -*- coding: utf-8 -*-
"""
应用配置模块

统一管理应用的所有配置信息
"""
import os
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """基础配置类"""
    
    # Flask 配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-stocktrade')
    DEBUG = True
    
    # 数据库配置
    DATABASE_PATH = BASE_DIR / 'stock_trades.db'
    
    # 券商配置
    BROKERS_CONFIG_PATH = BASE_DIR / 'config' / 'brokers.json'
    
    # 股票数据服务配置
    STOCK_DATA_TIMEOUT = 10  # 请求超时时间（秒）
    STOCK_DATA_RETRY = 3      # 重试次数
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 券商默认配置
    DEFAULT_BROKERS = [
        {"id": "guotai", "name": "国泰君安", "rate": 2.5, "min_fee": 5, "description": "万2.5, 最低5元"},
        {"id": "huarun", "name": "华泰证券", "rate": 1.8, "min_fee": 5, "description": "万1.8, 最低5元"},
        {"id": "zhongxin", "name": "中信证券", "rate": 1.5, "min_fee": 5, "description": "万1.5, 最低5元"},
        {"id": "guangda", "name": "光大证券", "rate": 1.2, "min_fee": 5, "description": "万1.2, 最低5元"},
        {"id": "yongtai", "name": "甬兴证券", "rate": 1.0, "min_fee": 1, "description": "万1.0, 最低1元"},
        {"id": "zheshang", "name": "浙商证券", "rate": 0.854, "min_fee": 1, "description": "万0.854, 最低1元"},
        {"id": "pingan", "name": "平安证券", "rate": 2.5, "min_fee": 5, "description": "万2.5, 最低5元"},
        {"id": "citic", "name": "中信建投", "rate": 1.2, "min_fee": 5, "description": "万1.2, 最低5元"},
    ]
    
    @classmethod
    def get_db_path(cls) -> str:
        """获取数据库路径"""
        return str(cls.DATABASE_PATH)
    
    @classmethod
    def get_brokers_config_path(cls) -> str:
        """获取券商配置路径"""
        return str(cls.BROKERS_CONFIG_PATH)
    
    @classmethod
    def ensure_config_dir_exists(cls) -> None:
        """确保配置目录存在"""
        cls.BROKERS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


# 配置字典，用于根据环境切换配置
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}