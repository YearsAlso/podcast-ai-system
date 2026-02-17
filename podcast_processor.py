#!/usr/bin/env python3
"""
播客处理系统 - 主脚本
使用新的配置结构
"""

import argparse
import os
import sys
import sqlite3
from datetime import datetime

# 导入配置
from config import (
    OBSIDIAN_VAULT,
    PODCASTS_DIR,
    PROJECT_ROOT,
    DB_PATH,
    TEMP_DIR,
    DEFAULT_PROCESS_LIMIT,
    validate_config
)

def setup_environment():
    """设置环境"""
    print("🔧 设置环境...")
    
    # 验证配置
    errors = validate_config()
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # 创建数据库
    setup_database()
    
    print("✅ 环境设置完成")
    return True

def setup_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 已处理播客表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processed_podcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        podcast_name TEXT NOT NULL,
        episode_title TEXT NOT NULL,
        episode_url TEXT UNIQUE NOT NULL,
        audio_path TEXT,
        processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        output_path TEXT,
        status TEXT DEFAULT 'pending',
        transcript_length INTEGER,
        summary_length INTEGER
    )
    ''')
    
    # 播客订阅表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS podcast_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        rss_url TEXT NOT NULL,
        enabled BOOLEAN DEFAULT 1,
        last_checked TIMESTAMP,
        last_episode_date TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库已初始化: {DB_PATH}")

def add_subscription(name, rss_url):
    """添加播客订阅"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO podcast_subscriptions (name, rss_url, enabled)
        VALUES (?, ?, 1)
        ''', (name, rss_url))
        
        conn.commit()
        print(f"✅ 已添加订阅: {name}")
        return True
    except Exception as e:
        print(f"❌ 添加订阅失败: {e}")
        return False
    finally:
        conn.close()

def list_subscriptions():
    """列出所有订阅"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, name, rss_url, enabled, last_checked, last_episode_date
    FROM podcast_subscriptions
    ORDER BY name
    ''')
    
    subscriptions = cursor.fetchall()
    conn.close()
    
    return subscriptions

def process_single_episode(podcast_name, episode_info):
    """处理单个播客期数（简化版）"""
    
    print(f"\n🎬 处理: {episode_info.get('title', '未知标题')}")
    
    # 检查是否已处理
    if check_if_processed(episode_info.get('audio_url', '')):
        print("⏭️  已处理过，跳过")
        return None
    
    # 模拟处理步骤
    steps = [
        ("📥 下载音频", True),
        ("🎤 转文字", True),
        ("🧠 AI总结", False),  # 需要配置
        ("📝 保存笔记", True)
    ]
    
    for step_name, implemented in steps:
        status = "✅" if implemented else "⚠️ （待实现）"
        print(f"  {status} {step_name}")
    
    # 创建Obsidian笔记
    output_path = create_obsidian_note_simple(podcast_name, episode_info)
    
    if output_path:
        print(f"📁 笔记已保存: {output_path}")
        return output_path
    
    return None

def check_if_processed(episode_url):
    """检查是否已处理"""
    if not episode_url:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT COUNT(*) FROM processed_podcasts WHERE episode_url = ? AND status = 'completed'",
        (episode_url,)
    )
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0

def create_obsidian_note_simple(podcast_name, episode_info):
    """创建简单的Obsidian笔记"""
    
    # 创建播客目录
    safe_name = podcast_name.replace(" ", "_").replace("/", "_")
    podcast_dir = os.path.join(PODCASTS_DIR, safe_name)
    os.makedirs(podcast_dir, exist_ok=True)
    
    # 生成文件名
    safe_title = episode_info.get('title', '未知标题').replace(" ", "_").replace("/", "_")[:50]
    date_str = episode_info.get('pub_date', datetime.now().strftime("%Y-%m-%d"))
    filename = f"{date_str}_{safe_name}_{safe_title}.md"
    output_path = os.path.join(podcast_dir, filename)
    
    # 构建内容
    content = f"""---
podcast: "{podcast_name}"
episode: "{episode_info.get('title', '未知标题')}"
date: {date_str}
processed_date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
source: "播客处理系统"
audio_url: "{episode_info.get('audio_url', '')}"
duration: "{episode_info.get('duration', '未知')}"
status: "框架测试"
tags: [播客, 待处理]
---

## 📋 播客信息
- **播客名称**: {podcast_name}
- **期数标题**: {episode_info.get('title', '未知标题')}
- **发布时间**: {date_str}
- **音频时长**: {episode_info.get('duration', '未知')}
- **原始链接**: {episode_info.get('audio_url', '')}

## 📝 描述
{episode_info.get('description', '无描述')}

## 🔧 处理状态
此文件由播客处理系统框架生成。

### 当前功能状态
- ✅ 系统框架: 已完成
- ✅ 数据库记录: 已完成  
- ✅ Obsidian集成: 已完成
- 🔄 音频下载: 待实现
- 🔄 文字转录: 待实现（需要配置Whisper）
- 🔄 AI总结: 待实现（需要配置OpenAI API）

### 下一步操作
1. 配置Whisper进行音频转文字
2. 实现音频下载功能
3. 配置AI总结功能
4. 添加真正的RSS解析

## 💡 使用说明
1. 系统代码位于: `~/Project/podcast-ai-system/`
2. 生成的笔记在此目录: `{PODCASTS_DIR}/`
3. 可以在下方添加个人笔记

## 📋 个人笔记
<!-- 在这里添加你的思考和笔记 -->

---
*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 记录到数据库
        record_processed_episode(podcast_name, episode_info, output_path)
        
        return output_path
    except Exception as e:
        print(f"❌ 保存笔记失败: {e}")
        return None

def record_processed_episode(podcast_name, episode_info, output_path):
    """记录已处理的播客"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO processed_podcasts 
    (podcast_name, episode_title, episode_url, output_path, status)
    VALUES (?, ?, ?, ?, 'completed')
    ''', (
        podcast_name,
        episode_info.get('title', '未知标题'),
        episode_info.get('audio_url', ''),
        output_path
    ))
    
    conn.commit()
    conn.close()

def list_processed_episodes(limit=10):
    """列出已处理的播客"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT podcast_name, episode_title, processed_date, output_path
    FROM processed_podcasts
    WHERE status = 'completed'
    ORDER BY processed_date DESC
    LIMIT ?
    ''', (limit,))
    
    episodes = cursor.fetchall()
    conn.close()
    
    return episodes

def main():
    parser = argparse.ArgumentParser(description="播客处理系统")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 添加订阅命令
    add_parser = subparsers.add_parser("add", help="添加播客订阅")
    add_parser.add_argument("--name", required=True, help="播客名称")
    add_parser.add_argument("--rss", required=True, help="RSS地址")
    
    # 列出订阅命令
    subparsers.add_parser("list", help="列出所有订阅")
    
    # 处理命令
    process_parser = subparsers.add_parser("process", help="处理播客")
    process_parser.add_argument("--name", required=True, help="播客名称")
    process_parser.add_argument("--test", action="store_true", help="测试模式")
    
    # 列出已处理命令
    history_parser = subparsers.add_parser("history", help="查看处理历史")
    history_parser.add_argument("--limit", type=int, default=10, help="显示数量")
    
    # 配置命令
    subparsers.add_parser("config", help="显示配置")
    
    args = parser.parse_args()
    
    # 设置环境
    if not setup_environment():
        return 1
    
    if args.command == "add":
        # 添加订阅
        add_subscription(args.name, args.rss)
        
    elif args.command == "list":
        # 列出订阅
        subscriptions = list_subscriptions()
        
        if not subscriptions:
            print("📭 暂无订阅")
        else:
            print("📋 播客订阅列表:")
            print("-" * 80)
            for sub in subscriptions:
                id, name, rss, enabled, last_checked, last_episode = sub
                status = "✅ 启用" if enabled else "❌ 禁用"
                print(f"{id:3} | {name:20} | {status}")
                print(f"    RSS: {rss[:60]}...")
                if last_checked:
                    print(f"    最后检查: {last_checked}")
                print()
    
    elif args.command == "process":
        # 处理播客
        print(f"🎙️ 处理播客: {args.name}")
        
        if args.test:
            # 测试模式：创建示例笔记
            episode_info = {
                "title": "测试期：系统框架验证",
                "description": "这是用于测试系统框架的示例播客",
                "audio_url": "https://example.com/test.mp3",
                "pub_date": datetime.now().strftime("%Y-%m-%d"),
                "duration": "10:00"
            }
            
            output_path = process_single_episode(args.name, episode_info)
            
            if output_path:
                print(f"\n✅ 测试完成！")
                print(f"📁 笔记已创建: {output_path}")
                print(f"💡 这是一个框架测试文件，实际功能需要进一步配置。")
            else:
                print("❌ 测试失败")
        
        else:
            # 实际处理模式（需要实现）
            print("🔧 实际处理功能需要:")
            print("1. 配置Whisper进行音频转文字")
            print("2. 实现RSS解析和音频下载")
            print("3. 配置AI总结功能")
            print("\n💡 建议先使用 --test 参数测试框架")
    
    elif args.command == "history":
        # 查看处理历史
        episodes = list_processed_episodes(args.limit)
        
        if not episodes:
            print("📭 暂无处理记录")
        else:
            print(f"📜 最近 {len(episodes)} 条处理记录:")
            print("-" * 80)
            for episode in episodes:
                podcast_name, episode_title, processed_date, output_path = episode
                print(f"🎙️ {podcast_name}")
                print(f"   📝 {episode_title}")
                print(f"   ⏰ {processed_date}")
                print(f"   📁 {output_path}")
                print()
    
    elif args.command == "config":
        # 显示配置
        from config import get_config_summary
        summary = get_config_summary()
        
        print("⚙️ 系统配置:")
        print("-" * 60)
        for key, value in summary.items():
            print(f"{key:20}: {value}")
        
        print("\n📁 目录结构:")
        print(f"  项目代码: {PROJECT_ROOT}")
        print(f"  Obsidian笔记: {PODCASTS_DIR}")
        print(f"  数据库: {DB_PATH}")
        print(f"  临时文件: {TEMP_DIR}")
    
    else:
        # 显示帮助
        parser.print_help()
        print("\n📋 快速开始:")
        print("  1. 添加订阅: podcast_processor.py add --name '播客名' --rss 'RSS地址'")
        print("  2. 测试处理: podcast_processor.py process --name '播客名' --test")
        print("  3. 查看配置: podcast_processor.py config")
        print("  4. 查看历史: podcast_processor.py history")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())