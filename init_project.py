# -*- coding: utf-8 -*-
"""
股票交易管理系统 - 项目初始化脚本

用于初始化项目环境和数据库
"""
import sys
import os
from pathlib import Path

def check_dependencies():
    """检查依赖项是否安装"""
    print("=" * 50)
    print("检查依赖项...")
    
    required = {
        'flask': 'Flask Web框架',
        'baostock': 'Baostock 股票数据服务'
    }
    
    missing = []
    for package, description in required.items():
        try:
            __import__(package)
            print(f"✓ {description} ({package})")
        except ImportError:
            print(f"✗ {description} ({package}) - 未安装")
            missing.append(package)
    
    if missing:
        print("\n请运行以下命令安装缺失的依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("\n✓ 所有依赖项已安装")
    return True


def init_database():
    """初始化数据库"""
    print("\n" + "=" * 50)
    print("初始化数据库...")
    
    try:
        # 导入数据库模块
        sys.path.insert(0, str(Path(__file__).parent))
        from app.database import init_database, get_database_info
        
        # 初始化数据库
        init_database()
        print("✓ 数据库初始化完成")
        
        # 显示数据库信息
        info = get_database_info()
        print(f"\n数据库信息:")
        print(f"  路径: {info['path']}")
        print(f"  大小: {info['size_mb']} MB")
        print(f"  表数量: {info['table_count']}")
        print(f"  记录数量: {info['record_count']}")
        
        return True
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False


def check_config_files():
    """检查配置文件"""
    print("\n" + "=" * 50)
    print("检查配置文件...")
    
    config_dir = Path(__file__).parent / 'config'
    config_dir.mkdir(exist_ok=True)
    
    brokers_file = config_dir / 'brokers.json'
    if not brokers_file.exists():
        print("✓ 券商配置文件已创建")
    else:
        print(f"✓ 券商配置文件已存在: {brokers_file}")
    
    return True


def print_usage():
    """打印使用说明"""
    print("\n" + "=" * 50)
    print("项目初始化完成！")
    print("=" * 50)
    print("\n启动服务:")
    print("  python run.py")
    print("\n访问地址:")
    print("  http://127.0.0.1:5000")
    print("\n运行测试:")
    print("  pytest tests/ -v")
    print("\n" + "=" * 50)


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("股票交易管理系统 - 项目初始化")
    print("=" * 50)
    
    # 检查依赖
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n✗ 依赖检查未通过，请先安装依赖")
        sys.exit(1)
    
    # 初始化数据库
    db_ok = init_database()
    if not db_ok:
        print("\n✗ 数据库初始化失败")
        sys.exit(1)
    
    # 检查配置文件
    check_config_files()
    
    # 打印使用说明
    print_usage()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())