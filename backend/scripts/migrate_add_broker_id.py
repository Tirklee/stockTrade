# -*- coding: utf-8 -*-
"""
迁移脚本：添加 broker_id 到 positions 表
"""
from app import db
from sqlalchemy import text


def upgrade():
    """升级数据库"""
    conn = db.engine.connect()
    trans = conn.begin()

    try:
        # 检查 broker_id 列是否已存在
        result = conn.execute(text("PRAGMA table_info(positions)"))
        columns = [row[1] for row in result.fetchall()]

        if 'broker_id' not in columns:
            # 添加 broker_id 列（允许 NULL，这样现有数据不受影响）
            conn.execute(text("ALTER TABLE positions ADD COLUMN broker_id INTEGER"))
            conn.execute(text("ALTER TABLE positions ADD COLUMN broker_id REFERENCES brokers(id)"))
            print("已添加 broker_id 列")

        # 删除旧的 unique 约束（SQLite 不支持直接删除 unique 约束，需要重建表）
        # 由于 SQLite 限制，我们通过重建表来实现
        conn.execute(text("DROP INDEX IF EXISTS ix_positions_stock_code"))

        # 创建联合唯一索引
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_position_stock_broker ON positions(stock_code, broker_id)"))
        print("已创建联合唯一索引 uq_position_stock_broker")

        trans.commit()
        print("迁移成功完成")
    except Exception as e:
        trans.rollback()
        print(f"迁移失败: {e}")
        raise
    finally:
        conn.close()


def downgrade():
    """降级数据库"""
    conn = db.engine.connect()
    trans = conn.begin()

    try:
        conn.execute(text("DROP INDEX IF EXISTS uq_position_stock_broker"))
        print("已删除联合唯一索引")

        trans.commit()
        print("降级完成")
    except Exception as e:
        trans.rollback()
        print(f"降级失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        upgrade()