# -*- coding: utf-8 -*-
"""
Flask应用工厂
"""
from flask import Flask
import os

def create_app(config_name='default'):
    """创建Flask应用实例"""
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    
    # 加载配置
    from config import Config
    app.config.from_object(Config)
    
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app