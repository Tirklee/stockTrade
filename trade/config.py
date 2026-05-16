# -*- coding: utf-8 -*-
"""
股票交易录入服务配置模块
"""
import os

class Config:
    """基础配置"""
    # 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'stock_trades.db')
    
    # 分页默认设置
    DEFAULT_PER_PAGE = 10
    MAX_PER_PAGE = 1000
    
    # 券商佣金配置
    BROKER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'broker_config.json')
    
    # API超时设置
    STOCK_API_TIMEOUT = 10
    STOCK_API_RETRY = 3
    
    # 股票数据缓存时间(秒)
    STOCK_DATA_CACHE_TIME = 300

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}