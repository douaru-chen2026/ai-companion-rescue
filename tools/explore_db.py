#!/usr/bin/env python3
"""
EVE聊天记录数据库探查脚本
用法: python3 explore_db.py <数据库文件路径>
作用: 查看数据库里有哪些表、每个表有哪些字段，方便后续写导出脚本
"""
import sqlite3
import sys

def explore(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 列出所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"数据库: {db_path}")
    print(f"共 {len(tables)} 张表")
    print("=" * 60)
    
    for table in tables:
        print(f"\n【表名】{table}")
        
        # 查看表结构
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"  字段 ({len(columns)}个):")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
        
        # 查看记录数
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  记录数: {count}")
        except:
            print(f"  记录数: 查询失败")
        
        # 查看前3条样例数据
        if count > 0:
            try:
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                print(f"  样例数据:")
                for i, row in enumerate(rows):
                    print(f"    第{i+1}条:")
                    for j, val in enumerate(row):
                        val_str = str(val)
                        if len(val_str) > 80:
                            val_str = val_str[:80] + "..."
                        print(f"      {col_names[j]} = {val_str}")
            except Exception as e:
                print(f"  样例数据: 查询失败 ({e})")
    
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 explore_db.py <数据库文件路径>")
        sys.exit(1)
    explore(sys.argv[1])
