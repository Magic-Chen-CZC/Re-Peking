#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

# 直接查询数据库获取列定义
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'trip_stops'
        AND column_name IN ('arrived_at', 'completed_at')
        ORDER BY ordinal_position
    """))
    
    print("直接从 information_schema 查询：")
    print("-" * 70)
    rows = list(result)
    for row in rows:
        print(f"{row[0]:20s} {row[1]:30s} nullable={row[2]}")
    print("-" * 70)
    
    # 检查是否是 timestamp with time zone
    has_tz = any('timestamp with time zone' in row[1].lower() for row in rows)
    
    if has_tz:
        print("\n✅ 列类型包含 'timestamp with time zone'")
    else:
        print("\n❌ 列类型不包含 'timestamp with time zone'")
        print("当前类型是:", [row[1] for row in rows])
