# -*- coding: utf-8 -*-
"""
应用入口
"""
import os
from app import create_app

# 获取环境配置
config_name = os.environ.get('FLASK_ENV', 'development')

# 导入配置模块
from config import config

app = create_app(config.get(config_name, config['development']))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)