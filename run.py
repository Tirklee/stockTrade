# -*- coding: utf-8 -*-
"""
股票交易管理 - 应用入口
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)