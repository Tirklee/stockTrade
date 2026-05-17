# -*- coding: utf-8 -*-
"""
Flask应用工厂

创建和配置Flask应用实例
"""
from flask import Flask
import os
from pathlib import Path

# 导入配置
from app.config import Config


def create_app(config_name='default'):
    """
    创建Flask应用实例
    
    Args:
        config_name: 配置名称，可选 'development' 或 'production'
    
    Returns:
        Flask应用实例
    """
    # 获取项目根目录
    base_dir = Path(__file__).resolve().parent.parent
    
    app = Flask(__name__,
                template_folder=str(base_dir / 'templates'),
                static_folder=str(base_dir / 'static'),
                static_url_path='/static')
    
    # 加载配置
    app.config.from_object(Config)
    
    # 注册自定义 Jinja2 过滤器
    @app.template_filter('decimal3')
    def decimal3_filter(value):
        """将数值格式化为3位小数的字符串"""
        if value is None:
            return '0.000'
        try:
            return f"{float(value):.3f}"
        except (ValueError, TypeError):
            return '0.000'
    
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app