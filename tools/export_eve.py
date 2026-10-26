#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 聊天记录导出脚本（智能自动识别版 v2）
用法: python3 export_eve.py <数据库文件或文件夹> [输出格式]
输出格式: txt / json / csv（默认 txt）

特性:
- 自动扫描库里所有表，智能识别哪张是"消息表"
- 自动匹配常见字段名（角色/正文/时间/会话ID），不用手动改配置
- 识别不到时给出清晰提示，引导用 explore_db 查看
- 支持单个 .db/.sqlite 文件，或包含多个库的文件夹
- 加密库(SQLCipher)会直接报错并给出提示
"""
import sqlite3
import sys
import os
import json
import csv
from datetime import datetime

# ===== 字段别名库（小写匹配，覆盖常见命名）=====
ROLE_ALIASES = {
    'role', 'sender', 'sendertype', 'type', 'msg_type', 'msgtype',
    'is_from_me', 'direction', 'who', 'author', 'from_user', 'from_role',
    'speaker', 'identity', 'user_type', 'is_ai', 'is_user', 'source',
}
CONTENT_ALIASES = {
    'content', 'text', 'message', 'msg', 'body', 'data', 'content_text',
    'raw_content', 'message_content', 'chat_content', 'reply', 'answer',
    'question', 'prompt', 'response', 'utterance', 'value', 'detail',
}
TIME_ALIASES = {
    'timestamp', 'time', 'created_at', 'create_time', 'createtime',
    'date', 'datetime', 'send_time', 'sendtime', 'updated_at', 'update_time',
    'updatetime', 'ctime', 'mtime', 'created', 'ts', 'add_time', 'addtime',
    'msg_time', 'msgtime', 'timeline',
}
CONV_ALIASES = {
    'conversation_id', 'session_id', 'chat_id', 'chatid', 'conv_id',
    'thread_id', 'dialog_id', 'room_id', 'sessionid', 'conversationid',
    'group_id', 'topic_id', 'channel_id', 'dialogid', 'friend_id',
    'target_id', 'peer_id', 'contact_id',
}

# 明显不是消息表的关键词（排除用）
NON_MESSAGE_TABLE_KEYWORDS = {
    'android_metadata', 'sqlite_', 'room_master_table', 'schema_version',
    'fts', 'search_index', 'cache', 'config', 'setting', 'user_profile',
    'avatar', 'emoji', 'sticker', 'gift', 'recharge', 'order', 'payment',
    'wallet', 'token', 'auth', 'login', 'device', 'push', 'notification',
}


def score_table(table_name, columns, row_count):
    """给一张表打分，判断它像不像消息表。分数越高越像。"""
    name_lower = table_name.lower()
    for kw in NON_MESSAGE_TABLE_KEYWORDS:
        if kw in name_lower:
            return -100
    score = 0.0
    col_lower = {c.lower() for c in columns}
    if col_lower & CONTENT_ALIASES:
        score += 3
    if col_lower & TIME_ALIASES:
        score += 2
    if col_lower & ROLE_ALIASES:
        score += 2
    if col_lower & CONV_ALIASES:
        score += 1
    score += min(row_count / 100.0, 5.0)
    if any(k in name_lower for k in ['message', 'chat', 'conversation', 'dialog', 'talk', 'record', 'history']):
        score += 2
    return score


def match_field(columns, aliases):
    """从列名里匹配别名，先精确后模糊。返回匹配到的列名或 None。"""
    for c in columns:
        if c.lower() in aliases:
            return c
    for c in columns:
        cl = c.lower()
        for a in aliases:
            if a in cl:
                return c
    return None


def find_message_table(cursor):
    """扫描所有表，返回最可能的消息表信息。"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    candidates = []
    for t in tables:
        try:
            cursor.execute(f"PRAGMA table_info('{t}')")
            cols = [r[1] for r in cursor.fetchall()]
            cursor.execute(f"SELECT COUNT(*) FROM '{t}'")
            cnt = cursor.fetchone()[0]
            s = score_table(t, cols, cnt)
            candidates.append((s, t, cols, cnt))
        except Exception:
            continue
    candidates.sort(key=lambda x: x[0], reverse=True)
    if candidates and candidates[0][0] >= 3.0:
        s, t, cols, cnt = candidates[0]
        mapping = {
            'role': match_field(cols, ROLE_ALIASES),
            'content': match_field(cols, CONTENT_ALIASES),
            'time': match_field(cols, TIME_ALIASES),
            'conversation': match_field(cols, CONV_ALIASES),
        }
        return t, cols, cnt, mapping, candidates
    return None, None, None, None, candidates


def format_time(val):
    if val is None:
        return ''
    try:
        ts = float(val)
        if ts > 1e12:
            ts = ts / 1000.0
        if ts > 1e9:
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, OSError):
        pass
    return str(val)


def normalize_role(val):
    """把角色字段归一化。数字(0/1/2)因 app 含义不同，保留原值不瞎猜。"""
    if val is None:
        return ''
    s = str(val).strip().lower()
    if s in ('user', 'me', 'from_user', 'human', '主人'):
        return '你'
    if s in ('assistant', 'ai', 'bot', 'from_ai', 'model', '机器人'):
        return 'AI'
    return str(val)


def export_txt(messages, path):
    with open(path, 'w', encoding='utf-8') as f:
        cur_conv = None
        for m in messages:
            conv = m.get('conversation', '')
            if conv != cur_conv:
                f.write(f"\n{'=' * 50}\n会话: {conv}\n{'=' * 50}\n\n")
                cur_conv = conv
            f.write(f"[{m.get('time', '')}] {m.get('role', '')}: {m.get('content', '')}\n")
    print(f"  已导出 txt: {path}")


def export_json(messages, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    print(f"  已导出 json: {path}")


def export_csv(messages, path):
    if not messages:
        print("  无数据，跳过 csv")
        return
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(messages[0].keys()))
        w.writeheader()
        w.writerows(messages)
    print(f"  已导出 csv: {path}")


def process_db(db_path, fmt, out_prefix):
    print(f"\n处理: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except sqlite3.DatabaseError as e:
        print(f"  打开失败: {e}")
        print("  提示: 如果提示 'file is not a database' 或 'file is encrypted'，")
        print("  说明这个库可能加密了(SQLCipher)，自助脚本解不开，请把 explore_db 的输出截图发我们确认。")
        return 0

    table, cols, cnt, mapping, candidates = find_message_table(cursor)
    if table is None:
        print("  未能自动识别消息表。库里的表:")
        for s, t, c, n in candidates[:8]:
            print(f"    - {t} ({n} 行, 字段: {', '.join(c[:6])}{'...' if len(c) > 6 else ''})")
        print("  请先运行: python explore_db.py " + db_path)
        print("  把输出发我们，我们帮你确认哪张是消息表。")
        conn.close()
        return 0

    print(f"  识别到消息表: {table} ({cnt} 行)")
    print(f"  字段匹配: 角色={mapping['role']}, 正文={mapping['content']}, "
          f"时间={mapping['time']}, 会话={mapping['conversation']}")

    if mapping['content'] is None:
        print("  警告: 没匹配到正文字段，导出内容可能为空。请用 explore_db 确认字段名。")

    order_col = mapping['time'] or mapping['content'] or cols[0]
    try:
        cursor.execute(f"SELECT * FROM '{table}' ORDER BY '{order_col}' ASC")
        rows = cursor.fetchall()
        col_names = [d[0] for d in cursor.description]
    except Exception as e:
        print(f"  查询失败: {e}，尝试无排序读取")
        cursor.execute(f"SELECT * FROM '{table}'")
        rows = cursor.fetchall()
        col_names = [d[0] for d in cursor.description]

    messages = []
    for row in rows:
        rec = dict(zip(col_names, row))
        messages.append({
            'time': format_time(rec.get(mapping['time'])) if mapping['time'] else '',
            'role': normalize_role(rec.get(mapping['role'])) if mapping['role'] else '',
            'content': str(rec.get(mapping['content'], '')) if mapping['content'] else '',
            'conversation': str(rec.get(mapping['conversation'], os.path.basename(db_path))) if mapping['conversation'] else os.path.basename(db_path),
        })
    conn.close()

    if not messages:
        print("  没有读取到消息")
        return 0

    base = f"{out_prefix}_{len(messages)}条"
    if fmt == 'json':
        export_json(messages, base + '.json')
    elif fmt == 'csv':
        export_csv(messages, base + '.csv')
    else:
        export_txt(messages, base + '.txt')
    print(f"  完成: 共 {len(messages)} 条")
    return len(messages)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 export_eve.py <数据库文件或文件夹> [txt|json|csv]")
        print("示例: python3 export_eve.py eve_db txt")
        print("      python3 export_eve.py chat.db json")
        sys.exit(1)

    target = sys.argv[1]
    fmt = sys.argv[2].lower() if len(sys.argv) > 2 else 'txt'
    if fmt not in ('txt', 'json', 'csv'):
        print(f"不支持的格式: {fmt}，用 txt")
        fmt = 'txt'

    db_files = []
    if os.path.isdir(target):
        for root, _, files in os.walk(target):
            for fn in files:
                if fn.endswith(('.db', '.sqlite', '.sqlite3')):
                    db_files.append(os.path.join(root, fn))
    elif os.path.isfile(target):
        db_files.append(target)
    else:
        print(f"找不到: {target}")
        sys.exit(1)

    if not db_files:
        print(f"在 {target} 里没找到 .db/.sqlite 文件")
        sys.exit(1)

    print(f"找到 {len(db_files)} 个数据库文件")
    out_prefix = os.path.splitext(os.path.basename(target.rstrip('/')))[0] or 'EVE聊天记录'
    total = 0
    for db in db_files:
        total += process_db(db, fmt, out_prefix)

    print(f"\n==== 全部完成，共导出 {total} 条 ====")
    if total == 0:
        print("提示: 一个都没导出来，大概率是库加密或表名特殊。")
        print("把 explore_db 的输出发我们，我们帮你看。")
        sys.exit(1)


if __name__ == '__main__':
    main()
