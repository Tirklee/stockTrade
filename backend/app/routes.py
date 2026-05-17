# -*- coding: utf-8 -*-
"""
Flask应用入口
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config

db = SQLAlchemy()


def create_app(config_name='default'):
    """创建应用实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 注册蓝图
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 初始化券商数据
        from app.services.broker_service import init_default_brokers
        init_default_brokers()

    return app


# 导入路由蓝图
from app.routes import api_bp