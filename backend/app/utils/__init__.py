# -*- coding: utf-8 -*-
"""
日志配置
"""
import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """配置日志"""
    # 设置日志级别
    app.logger.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 文件处理器
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)

    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加处理器
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)

    return app.logger