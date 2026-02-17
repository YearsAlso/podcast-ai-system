#!/usr/bin/env python3
"""
播客处理系统 - 主脚本
使用新的配置结构
"""

import argparse
import os
import sys
import sqlite3
import time
from datetime import datetime

# 导入配置
from config import (
    PODCASTS_DIR,
    PROJECT_ROOT,
    DB_PATH,
    TEMP_DIR,
    validate_config,
)

# 导入转录模块
try:
    from transcription import transcribe_audio, get_transcription_info

    TRANSCRIPTION_AVAILABLE = True
except ImportError:
    TRANSCRIPTION_AVAILABLE = False
    print("⚠️  转录模块不可用，使用简化模式")

# 导入音频下载模块
try:
    from audio_downloader import download_audio, get_audio_info, cleanup_temp_files
    from config import DOWNLOAD_TIMEOUT, TEMP_FILE_MAX_AGE_HOURS

    AUDIO_DOWNLOAD_AVAILABLE = True
except ImportError:
    AUDIO_DOWNLOAD_AVAILABLE = False
    print("⚠️  音频下载模块不可用，使用模拟下载")

# 导入RSS解析模块
try:
    from rss_parser import parse_rss_feed, get_latest_episodes
    from markdown_generator import save_episode_to_markdown, save_feed_summary_to_markdown

    RSS_PARSER_AVAILABLE = True
except ImportError:
    RSS_PARSER_AVAILABLE = False
    print("⚠️  RSS解析模块不可用，使用模拟数据")


def setup_environment():
    """设置环境"""
    print("🔧 设置环境...")

    # 验证配置
    errors, warnings = validate_config()
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"  - {error}")
        return False

    if warnings:
        print("⚠️  配置警告:")
        for warning in warnings:
            print(f"  - {warning}")

    # 创建数据库
    setup_database()

    print("✅ 环境设置完成")
    return True


def setup_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 已处理播客表
    cursor.execute("""
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
    """)

    # 播客订阅表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS podcast_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        rss_url TEXT NOT NULL,
        enabled BOOLEAN DEFAULT 1,
        last_checked TIMESTAMP,
        last_episode_date TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print(f"✅ 数据库已初始化: {DB_PATH}")


def add_subscription(name, rss_url):
    """添加播客订阅"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
        INSERT OR REPLACE INTO podcast_subscriptions (name, rss_url, enabled)
        VALUES (?, ?, 1)
        """,
            (name, rss_url),
        )

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

    cursor.execute("""
    SELECT id, name, rss_url, enabled, last_checked, last_episode_date
    FROM podcast_subscriptions
    ORDER BY name
    """)

    subscriptions = cursor.fetchall()
    conn.close()

    return subscriptions


def process_single_episode(podcast_name, episode_info, test_mode=False):
    """处理单个播客期数（支持多种转录模式）"""

    episode_title = episode_info.get("title", "未知标题")
    print(f"\n🎬 处理: {episode_title}")

    # 检查是否已处理
    if check_if_processed(episode_info.get("audio_url", "")):
        print("⏭️  已处理过，跳过")
        return None

    # 显示转录模式信息
    if TRANSCRIPTION_AVAILABLE:
        try:
            info = get_transcription_info()
            print(f"📋 转录模式: {info['current_mode']}")
            print(f"   可用模式: {', '.join(info['available_modes'])}")
        except:
            pass

    # 处理步骤
    steps_completed = []

    # 步骤1: 下载音频
    print("  📥 下载音频...")
    temp_audio_path = None
    audio_url = episode_info.get("audio_url", "")

    if audio_url and AUDIO_DOWNLOAD_AVAILABLE and not test_mode:
        try:
            # 真正的音频下载
            temp_audio_path = download_audio(
                audio_url, podcast_name, episode_title, timeout=DOWNLOAD_TIMEOUT
            )

            # 获取文件信息
            if temp_audio_path and os.path.exists(temp_audio_path):
                file_info = get_audio_info(temp_audio_path)
                if file_info:
                    print(
                        f"    ✅ 下载成功: {file_info['size_formatted']}, 格式: {file_info['extension']}"
                    )
                    steps_completed.append(
                        f"📥 音频下载 ({file_info['size_formatted']})"
                    )
                else:
                    steps_completed.append("📥 音频下载")
            else:
                print("    ⚠️  下载失败: 文件不存在")
                steps_completed.append("📥 下载失败")

        except Exception as e:
            print(f"    ❌ 下载失败: {e}")
            temp_audio_path = None
            steps_completed.append("📥 下载失败")

            # 创建模拟文件作为备用
            temp_audio_path = os.path.join(
                TEMP_DIR, f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            os.makedirs(TEMP_DIR, exist_ok=True)

            with open(temp_audio_path, "w", encoding="utf-8") as f:
                f.write(f"模拟音频文件（实际下载失败）\n")
                f.write(f"播客: {podcast_name}\n")
                f.write(f"期数: {episode_title}\n")
                f.write(f"原始URL: {audio_url}\n")
                f.write(f"错误: {e}\n")
                f.write(f"时间: {datetime.now()}\n")

            print(f"    ℹ️  创建模拟文件: {temp_audio_path}")
    else:
        # 没有URL或测试模式，创建模拟文件
        temp_audio_path = os.path.join(
            TEMP_DIR, f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        os.makedirs(TEMP_DIR, exist_ok=True)

        with open(temp_audio_path, "w", encoding="utf-8") as f:
            if test_mode:
                f.write(f"测试模式音频文件\n")
            elif not audio_url:
                f.write(f"无音频URL的模拟文件\n")
            else:
                f.write(f"音频下载模块不可用的模拟文件\n")

            f.write(f"播客: {podcast_name}\n")
            f.write(f"期数: {episode_title}\n")
            if audio_url:
                f.write(f"原始URL: {audio_url}\n")
            f.write(f"时间: {datetime.now()}\n")

        if test_mode:
            steps_completed.append("📥 测试模式")
        elif not audio_url:
            steps_completed.append("📥 无音频URL")
        else:
            steps_completed.append("📥 模拟下载")

    # 步骤2: 转文字
    print("  🎤 转文字...")
    transcript = ""
    if TRANSCRIPTION_AVAILABLE and not test_mode and temp_audio_path:
        try:
            transcript = transcribe_audio(temp_audio_path, podcast_name, episode_title)
            steps_completed.append("🎤 文字转录")
        except Exception as e:
            print(f"  ⚠️  转录失败: {e}")
            transcript = f"转录失败: {e}\n\n请检查转录配置。"
            steps_completed.append("🎤 转录失败")
    else:
        if test_mode:
            transcript = (
                f"测试模式 - 跳过实际转录\n播客: {podcast_name}\n期数: {episode_title}"
            )
            steps_completed.append("🎤 测试模式")
        elif not temp_audio_path:
            transcript = (
                f"无音频文件 - 无法转录\n播客: {podcast_name}\n期数: {episode_title}"
            )
            steps_completed.append("🎤 无音频文件")
        else:
            transcript = f"转录模块不可用\n播客: {podcast_name}\n期数: {episode_title}"
            steps_completed.append("🎤 转录不可用")

    # 步骤3: AI总结（待实现）
    print("  🧠 AI总结...")
    summary = (
        f"AI总结功能需要配置OpenAI API key\n在config.py中设置AI_SUMMARY_ENABLED = True"
    )
    steps_completed.append("🧠 AI总结待配置")

    # 步骤4: 保存笔记
    print("  📝 保存笔记...")
    output_path = create_obsidian_note_with_transcript(
        podcast_name, episode_info, transcript, summary
    )

    if output_path:
        steps_completed.append("📝 笔记保存")
        print(f"  📁 笔记已保存: {output_path}")

        # 记录到数据库
        record_processed_episode(
            podcast_name, episode_info, output_path, len(transcript)
        )

        # 清理临时文件
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                # 如果是.txt模拟文件，直接删除
                if temp_audio_path.endswith(".txt"):
                    os.remove(temp_audio_path)
                    print(f"    🧹 清理模拟文件: {os.path.basename(temp_audio_path)}")
                # 如果是真实音频文件，可以保留供后续使用或由定期清理任务处理
                else:
                    print(f"    💾 保留音频文件: {os.path.basename(temp_audio_path)}")
                    print(f"      路径: {temp_audio_path}")
            except Exception as e:
                print(f"    ⚠️  清理文件失败: {e}")

        # 显示完成状态
        print(f"\n✅ 处理完成!")
        print(f"   完成步骤: {', '.join(steps_completed)}")
        return output_path
    else:
        print("❌ 保存笔记失败")
        return None


def check_if_processed(episode_url):
    """检查是否已处理"""
    if not episode_url:
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM processed_podcasts WHERE episode_url = ? AND status = 'completed'",
        (episode_url,),
    )

    count = cursor.fetchone()[0]
    conn.close()

    return count > 0


def create_obsidian_note_simple(podcast_name, episode_info):
    """创建简单的Obsidian笔记（兼容旧版本）"""
    return create_obsidian_note_with_transcript(podcast_name, episode_info, "", "")


def create_obsidian_note_with_transcript(
    podcast_name, episode_info, transcript, summary
):
    """创建包含转录文字的Obsidian笔记"""

    # 创建播客目录
    safe_name = podcast_name.replace(" ", "_").replace("/", "_")
    podcast_dir = os.path.join(PODCASTS_DIR, safe_name)
    os.makedirs(podcast_dir, exist_ok=True)

    # 生成文件名
    safe_title = (
        episode_info.get("title", "未知标题").replace(" ", "_").replace("/", "_")[:50]
    )
    date_str = episode_info.get("pub_date", datetime.now().strftime("%Y-%m-%d"))
    filename = f"{date_str}_{safe_name}_{safe_title}.md"
    output_path = os.path.join(podcast_dir, filename)

    # 获取转录模式信息
    transcription_mode = "未知"
    if TRANSCRIPTION_AVAILABLE:
        try:
            info = get_transcription_info()
            transcription_mode = info["current_mode"]
        except:
            transcription_mode = "检测失败"

    # 构建内容
    content = f"""---
podcast: "{podcast_name}"
episode: "{episode_info.get('title', '未知标题')}"
date: {date_str}
processed_date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
source: "播客处理系统"
audio_url: "{episode_info.get('audio_url', '')}"
duration: "{episode_info.get('duration', '未知')}"
transcription_mode: "{transcription_mode}"
transcript_length: {len(transcript)}
status: "已处理"
tags: [播客, 转录]
---

## 📋 播客信息
- **播客名称**: {podcast_name}
- **期数标题**: {episode_info.get('title', '未知标题')}
- **发布时间**: {date_str}
- **音频时长**: {episode_info.get('duration', '未知')}
- **转录模式**: {transcription_mode}
- **转录长度**: {len(transcript)} 字符
- **原始链接**: {episode_info.get('audio_url', '')}

## 📝 描述
{episode_info.get('description', '无描述')}

## 🎤 文字转录
{transcript if transcript else '*转录功能未启用或转录失败*'}

## 🧠 AI总结
{summary if summary else '*AI总结功能需要配置OpenAI API key*'}

## 🔧 系统状态

### 📊 转录模式: {transcription_mode}

**可用选项**:
1. **openai_api** - OpenAI Whisper API（在线，需要API key）
2. **faster_whisper** - 本地轻量版（需要安装）
3. **whisper_cpp** - 纯CPU版本（需要编译）
4. **simplified** - 简化模式（仅下载，不转录）

**配置方法**:
在 `config.py` 中修改 `TRANSCRIPTION_MODE` 设置

### 🚀 功能状态
- ✅ 系统框架
- ✅ 数据库管理
- ✅ Obsidian集成
- ✅ 订阅管理
- {'✅' if transcript and '转录失败' not in transcript else '🔄'} 文字转录 ({transcription_mode})
- 🔄 AI智能总结（需要OpenAI API）
- 🔄 RSS解析（需要feedparser）
- 🔄 音频下载（需要实现）

## 📋 个人笔记
<!-- 在这里添加你的思考和笔记 -->

---
*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*转录模式: {transcription_mode}*
"""

    # 保存文件
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path
    except Exception as e:
        print(f"❌ 保存笔记失败: {e}")
        return None


def record_processed_episode(
    podcast_name, episode_info, output_path, transcript_length=0
):
    """记录已处理的播客"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    INSERT INTO processed_podcasts
    (podcast_name, episode_title, episode_url, output_path, status, transcript_length)
    VALUES (?, ?, ?, ?, 'completed', ?)
    """,
        (
            podcast_name,
            episode_info.get("title", "未知标题"),
            episode_info.get("audio_url", ""),
            output_path,
            transcript_length,
        ),
    )

    conn.commit()
    conn.close()


def list_processed_episodes(limit=10):
    """列出已处理的播客"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT podcast_name, episode_title, processed_date, output_path
    FROM processed_podcasts
    WHERE status = 'completed'
    ORDER BY processed_date DESC
    LIMIT ?
    """,
        (limit,),
    )

    episodes = cursor.fetchall()
    conn.close()

    return episodes


# ==================== RSS处理函数 ====================

def handle_rss_parse(args):
    """处理RSS解析命令"""
    print("=" * 60)
    print("📡 RSS解析")
    print("=" * 60)
    
    try:
        # 解析RSS feed
        feed_data = parse_rss_feed(args.url)
        feed_info = feed_data["feed_info"]
        episodes = feed_data["episodes"]
        
        # 显示feed信息
        print(f"\n🎙️  播客: {feed_info['title']}")
        print(f"📝 描述: {feed_info['description'][:150]}..." if len(feed_info['description']) > 150 else f"📝 描述: {feed_info['description']}")
        print(f"🌐 平台: {feed_info['platform']}")
        print(f"🗣️  语言: {feed_info['language']}")
        print(f"📊 总期数: {len(episodes)}")
        
        # 显示最新剧集
        print(f"\n📋 最新 {args.limit} 期:")
        for i, episode in enumerate(episodes[:args.limit], 1):
            print(f"\n  {i}. {episode['title']}")
            print(f"     发布日期: {episode['published']}")
            if episode.get('episode_number'):
                print(f"     期号: 第{episode['episode_number']}期")
            if episode.get('duration'):
                print(f"     时长: {episode['duration']}")
            if episode.get('audio_url'):
                audio_url = episode['audio_url']
                print(f"     音频: {audio_url[:80]}..." if len(audio_url) > 80 else f"     音频: {audio_url}")
        
        # 保存为JSON文件
        if args.save_json:
            import json
            with open(args.save_json, "w", encoding="utf-8") as f:
                json.dump(feed_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n💾 已保存为JSON文件: {args.save_json}")
        
        # 保存为Markdown文件
        if args.save_md:
            # 保存feed摘要
            summary_path = save_feed_summary_to_markdown(feed_data)
            print(f"\n📄 已保存feed摘要: {summary_path}")
            
            # 保存最新一期
            if episodes:
                latest_episode = episodes[0]
                episode_path = save_episode_to_markdown(feed_info, latest_episode)
                print(f"📄 已保存最新一期: {episode_path}")
        
        print("\n" + "=" * 60)
        print("✅ RSS解析完成")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ RSS解析失败: {e}")
        print("\n💡 故障排除:")
        print("1. 检查URL是否正确")
        print("2. 检查网络连接")
        print("3. 确认RSS feed可公开访问")
        return 1


def handle_rss_test(args):
    """处理RSS测试命令"""
    print("=" * 60)
    print("🧪 RSS功能测试")
    print("=" * 60)
    
    try:
        # 解析RSS feed
        print(f"\n📡 解析RSS feed: {args.url[:80]}..." if len(args.url) > 80 else f"📡 解析RSS feed: {args.url}")
        feed_data = parse_rss_feed(args.url)
        feed_info = feed_data["feed_info"]
        episodes = feed_data["episodes"]
        
        if not episodes:
            print("❌ 没有找到剧集")
            return 1
        
        # 选择要测试的剧集
        if args.episode < 0 or args.episode >= len(episodes):
            print(f"⚠️  剧集索引 {args.episode} 无效，使用最新一期")
            episode_idx = 0
        else:
            episode_idx = args.episode
        
        episode = episodes[episode_idx]
        print(f"\n🎯 测试剧集: {episode['title']}")
        print(f"   发布日期: {episode.get('published', '未知')}")
        
        # 保存为Markdown文件
        print("\n📄 生成Markdown文件...")
        md_path = save_episode_to_markdown(feed_info, episode)
        print(f"✅ 已保存: {md_path}")
        
        # 测试音频下载
        if args.download and AUDIO_DOWNLOAD_AVAILABLE and episode.get('audio_url'):
            print("\n📥 测试音频下载...")
            try:
                audio_url = episode['audio_url']
                audio_path = download_audio(
                    audio_url,
                    podcast_name=feed_info['title'],
                    episode_title=episode['title'],
                    timeout=DOWNLOAD_TIMEOUT
                )
                print(f"✅ 音频下载成功: {audio_path}")
                
                # 获取文件信息
                file_info = get_audio_info(audio_path)
                if file_info:
                    print(f"📊 文件信息: {file_info['size_formatted']}, 格式: {file_info['extension']}")
                
            except Exception as e:
                print(f"❌ 音频下载失败: {e}")
        
        print("\n" + "=" * 60)
        print("✅ RSS功能测试完成")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ RSS测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def handle_rss_batch(args):
    """处理批量处理命令"""
    print("=" * 60)
    print("🔄 批量处理订阅")
    print("=" * 60)
    
    try:
        # 获取所有订阅
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, rss_url FROM subscriptions WHERE enabled = 1")
        subscriptions = cursor.fetchall()
        conn.close()
        
        if not subscriptions:
            print("📭 没有启用的订阅")
            return 0
        
        print(f"\n📋 找到 {len(subscriptions)} 个订阅:")
        for name, rss_url in subscriptions:
            print(f"  - {name}: {rss_url[:80]}..." if len(rss_url) > 80 else f"  - {name}: {rss_url}")
        
        total_processed = 0
        
        for name, rss_url in subscriptions:
            print(f"\n{'='*40}")
            print(f"🎙️  处理: {name}")
            print(f"{'='*40}")
            
            try:
                # 解析RSS feed
                feed_data = parse_rss_feed(rss_url)
                feed_info = feed_data["feed_info"]
                episodes = feed_data["episodes"][:args.limit]
                
                print(f"📊 找到 {len(episodes)} 期（处理最新 {args.limit} 期）")
                
                for i, episode in enumerate(episodes, 1):
                    print(f"\n  {i}. {episode['title']}")
                    
                    # 保存为Markdown文件
                    md_path = save_episode_to_markdown(feed_info, episode)
                    print(f"     📄 已保存: {os.path.basename(md_path)}")
                    
                    # 下载音频
                    if args.download and AUDIO_DOWNLOAD_AVAILABLE and episode.get('audio_url'):
                        try:
                            audio_path = download_audio(
                                episode['audio_url'],
                                podcast_name=name,
                                episode_title=episode['title'],
                                timeout=DOWNLOAD_TIMEOUT
                            )
                            print(f"     📥 音频下载: {os.path.basename(audio_path)}")
                        except Exception as e:
                            print(f"     ❌ 音频下载失败: {e}")
                    
                    total_processed += 1
                
            except Exception as e:
                print(f"❌ 处理失败: {e}")
                continue
        
        print("\n" + "=" * 60)
        print(f"✅ 批量处理完成")
        print(f"📊 总计处理: {total_processed} 期")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 批量处理失败: {e}")
        return 1


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
    
    # 清理命令
    cleanup_parser = subparsers.add_parser("cleanup", help="清理临时文件")
    cleanup_parser.add_argument(
        "--age", type=int, default=24, help="清理超过指定小时的文件（默认:24）"
    )
    cleanup_parser.add_argument(
        "--dry-run", action="store_true", help="模拟运行，不实际删除"
    )
    
    # RSS解析命令
    if RSS_PARSER_AVAILABLE:
        rss_parser = subparsers.add_parser("rss", help="RSS解析功能")
        rss_subparsers = rss_parser.add_subparsers(dest="rss_command", help="RSS子命令")
        
        # 解析RSS feed
        parse_parser = rss_subparsers.add_parser("parse", help="解析RSS feed")
        parse_parser.add_argument("--url", required=True, help="RSS feed URL")
        parse_parser.add_argument("--limit", type=int, default=5, help="显示最新几期")
        parse_parser.add_argument("--save-json", help="保存为JSON文件")
        parse_parser.add_argument("--save-md", action="store_true", help="保存为Markdown文件")
        
        # 测试RSS feed
        test_parser = rss_subparsers.add_parser("test", help="测试RSS feed")
        test_parser.add_argument("--url", required=True, help="RSS feed URL")
        test_parser.add_argument("--episode", type=int, default=0, help="测试第几期（0=最新）")
        test_parser.add_argument("--download", action="store_true", help="测试音频下载")
        
        # 批量处理
        batch_parser = rss_subparsers.add_parser("batch", help="批量处理订阅")
        batch_parser.add_argument("--limit", type=int, default=3, help="每个播客处理几期")
        batch_parser.add_argument("--download", action="store_true", help="下载音频")
        batch_parser.add_argument("--transcribe", action="store_true", help="转录音频")
        batch_parser.add_argument("--summary", action="store_true", help="生成AI总结")

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
                "duration": "10:00",
            }

            output_path = process_single_episode(args.name, episode_info)

            if output_path:
                print("\n✅ 测试完成！")
                print(f"📁 笔记已创建: {output_path}")
                print("💡 这是一个框架测试文件，实际功能需要进一步配置。")
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

    elif args.command == "cleanup":
        # 清理临时文件
        print(f"🧹 清理临时文件 (超过 {args.age} 小时)")
        print(f"  目录: {TEMP_DIR}")

        if args.dry_run:
            print("  模式: 模拟运行（不实际删除）")

        if AUDIO_DOWNLOAD_AVAILABLE:
            try:
                if args.dry_run:
                    # 模拟运行：只列出文件
                    print("\n📋 将清理的文件:")
                    current_time = time.time()
                    max_age_seconds = args.age * 3600

                    deleted_count = 0
                    total_size = 0

                    for filename in os.listdir(TEMP_DIR):
                        filepath = os.path.join(TEMP_DIR, filename)
                        if os.path.isfile(filepath):
                            file_age = current_time - os.path.getmtime(filepath)
                            if file_age > max_age_seconds:
                                file_size = os.path.getsize(filepath)
                                print(
                                    f"   - {filename} ({file_size} 字节, {file_age/3600:.1f} 小时前)"
                                )
                                deleted_count += 1
                                total_size += file_size

                    if deleted_count > 0:
                        print(
                            f"\n📊 模拟结果: 将删除 {deleted_count} 个文件, 释放 {total_size} 字节"
                        )
                    else:
                        print("\nℹ️  没有需要清理的文件")

                else:
                    # 实际清理
                    deleted_count, total_size = cleanup_temp_files(args.age)
                    print(
                        f"\n✅ 清理完成: 删除 {deleted_count} 个文件, 释放 {total_size} 字节"
                    )

            except Exception as e:
                print(f"❌ 清理失败: {e}")
        else:
            print("❌ 音频下载模块不可用，无法执行清理")
    
    elif args.command == "rss" and RSS_PARSER_AVAILABLE:
        # RSS解析功能
        if not hasattr(args, "rss_command") or not args.rss_command:
            print("❌ 请指定RSS子命令")
            print("  可用子命令: parse, test, batch")
            return 1
        
        if args.rss_command == "parse":
            # 解析RSS feed
            return handle_rss_parse(args)
        
        elif args.rss_command == "test":
            # 测试RSS feed
            return handle_rss_test(args)
        
        elif args.rss_command == "batch":
            # 批量处理
            return handle_rss_batch(args)
        
        else:
            print(f"❌ 未知的RSS子命令: {args.rss_command}")
            return 1
    
    elif args.command == "rss" and not RSS_PARSER_AVAILABLE:
        print("❌ RSS解析模块不可用")
        print("💡 请安装 feedparser: pip install feedparser")
        return 1

    else:
        # 显示帮助
        parser.print_help()
        print("\n📋 快速开始:")
        print("  1. 添加订阅: podcast_processor.py add --name '播客名' --rss 'RSS地址'")
        print("  2. 测试处理: podcast_processor.py process --name '播客名' --test")
        print("  3. 查看配置: podcast_processor.py config")
        print("  4. 查看历史: podcast_processor.py history")
        print("  5. 清理文件: podcast_processor.py cleanup [--age 24] [--dry-run]")
        if RSS_PARSER_AVAILABLE:
            print("  6. RSS解析: podcast_processor.py rss parse --url <RSS地址>")
            print("  7. RSS测试: podcast_processor.py rss test --url <RSS地址>")

    return 0


if __name__ == "__main__":
    sys.exit(main())
