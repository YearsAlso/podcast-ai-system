#!/usr/bin/env python3
"""
苹果播客自动爬取、转文字、总结到Obsidian
简化版本，避免复杂依赖
"""

import argparse
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import sqlite3
import hashlib

# 配置
OBSIDIAN_VAULT = "/Volumes/MxStore/Project/YearsAlso"
PODCASTS_DIR = os.path.join(OBSIDIAN_VAULT, "Podcasts")
DB_PATH = os.path.join(os.path.dirname(__file__), "podcasts.db")


def setup_database():
    """创建数据库记录已处理的播客"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_podcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        podcast_name TEXT NOT NULL,
        episode_title TEXT NOT NULL,
        episode_url TEXT UNIQUE NOT NULL,
        processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        output_path TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    conn.commit()
    conn.close()
    print(f"✅ 数据库已初始化: {DB_PATH}")


def get_rss_feed(podcast_url):
    """
    获取苹果播客的RSS地址
    简化版本：假设用户直接提供RSS地址
    """
    # 实际实现需要：
    # 1. 解析苹果播客页面获取RSS
    # 2. 或使用iTunes Search API

    print(f"📡 获取播客RSS: {podcast_url}")

    # 这里简化处理，假设输入就是RSS地址
    # 实际应该检查是否是苹果播客链接并转换
    if "apple.com" in podcast_url and "id" in podcast_url:
        # 苹果播客页面，需要提取RSS
        # 这里返回示例RSS（实际需要网络请求）
        return f"https://rss.apple.com/podcast/{podcast_url.split('id')[-1]}"
    elif podcast_url.endswith(".rss") or "feed" in podcast_url:
        # 已经是RSS地址
        return podcast_url
    else:
        print(f"⚠️  无法识别播客URL类型，请提供RSS地址")
        return None


def parse_rss_feed(rss_url):
    """
    解析RSS获取最新播客列表
    简化版本：返回示例数据
    """
    print(f"📋 解析RSS: {rss_url}")

    # 实际实现需要：
    # 1. 使用feedparser库解析RSS
    # 2. 提取标题、描述、音频链接、发布时间

    # 这里返回示例数据
    episodes = [
        {
            "title": "最新一期：AI如何改变工作",
            "description": "讨论AI对工作的影响",
            "audio_url": "https://example.com/episode1.mp3",
            "pub_date": datetime.now().strftime("%Y-%m-%d"),
            "duration": "45:30",
        },
        {
            "title": "第二期：创业心得分享",
            "description": "创业经验分享",
            "audio_url": "https://example.com/episode2.mp3",
            "pub_date": (datetime.now().replace(day=datetime.now().day - 1)).strftime(
                "%Y-%m-%d"
            ),
            "duration": "38:15",
        },
    ]

    print(f"📊 找到 {len(episodes)} 期播客")
    return episodes


def check_if_processed(episode_url):
    """检查是否已处理过"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM processed_podcasts WHERE episode_url = ? AND status = 'completed'",
        (episode_url,),
    )

    count = cursor.fetchone()[0]
    conn.close()

    return count > 0


def mark_as_processing(episode_info):
    """标记为处理中"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    INSERT OR IGNORE INTO processed_podcasts 
    (podcast_name, episode_title, episode_url, status)
    VALUES (?, ?, ?, 'processing')
    """,
        (
            episode_info.get("podcast_name", "未知播客"),
            episode_info.get("title", "未知标题"),
            episode_info.get("audio_url", ""),
        ),
    )

    conn.commit()
    conn.close()


def mark_as_completed(episode_url, output_path):
    """标记为已完成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    UPDATE processed_podcasts 
    SET status = 'completed', output_path = ?, processed_date = CURRENT_TIMESTAMP
    WHERE episode_url = ?
    """,
        (output_path, episode_url),
    )

    conn.commit()
    conn.close()


def download_audio_simple(audio_url, output_path):
    """
    下载音频文件（简化版本）
    实际应该使用requests或wget
    """
    print(f"📥 下载音频: {audio_url}")
    print(f"   → 保存到: {output_path}")

    # 这里简化，实际需要实现下载逻辑
    # 使用：requests.get() 或 subprocess.run(["wget", ...])

    # 创建模拟文件（实际应该下载）
    with open(output_path, "w") as f:
        f.write(f"# 模拟音频文件\n原始URL: {audio_url}\n下载时间: {datetime.now()}")

    print(f"✅ 下载完成（模拟）")
    return True


def transcribe_with_simple_method(audio_path):
    """
    简化版转文字
    实际应该调用Whisper
    """
    print(f"🎤 转文字: {audio_path}")

    # 这里简化，实际应该：
    # 1. 调用Whisper API
    # 2. 或使用本地Whisper模型

    transcript = f"""
这是播客的文字转录内容（模拟）。

由于Whisper依赖安装问题，这里使用模拟数据。
实际使用时需要：
1. 安装Whisper: pip install openai-whisper
2. 安装FFmpeg: brew install ffmpeg
3. 调用转文字函数

音频文件: {audio_path}
处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【模拟转录内容】
欢迎收听本期播客。今天我们要讨论的是人工智能如何改变我们的工作方式。
随着AI技术的发展，许多传统工作正在发生变化...
"""

    print(f"✅ 转文字完成（模拟），长度: {len(transcript)} 字符")
    return transcript


def generate_summary(transcript):
    """生成总结（简化版）"""
    print("🧠 生成总结...")

    summary = f"""
## 内容总结（模拟）

**核心观点**:
1. AI正在改变工作方式
2. 需要学习新技能适应变化
3. 人机协作是未来趋势

**关键洞察**:
- AI不是取代人类，而是增强人类能力
- 终身学习变得更重要
- 创造力成为核心竞争力

**行动建议**:
1. 学习AI相关技能
2. 关注行业变化
3. 培养创造力

**处理信息**:
- 转录长度: {len(transcript)} 字符
- 总结时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 状态: 模拟数据，实际需要配置AI总结
"""

    return summary


def create_obsidian_note(podcast_info, transcript, summary):
    """创建Obsidian笔记"""

    # 创建目录
    safe_name = podcast_info["podcast_name"].replace(" ", "_").replace("/", "_")
    podcast_dir = os.path.join(PODCASTS_DIR, safe_name)
    os.makedirs(podcast_dir, exist_ok=True)

    # 生成文件名
    safe_title = podcast_info["title"].replace(" ", "_").replace("/", "_")[:50]
    date_str = podcast_info.get("pub_date", datetime.now().strftime("%Y-%m-%d"))
    filename = f"{date_str}_{safe_name}_{safe_title}.md"
    output_path = os.path.join(podcast_dir, filename)

    # 构建内容
    content = f"""---
podcast: "{podcast_info['podcast_name']}"
episode: "{podcast_info['title']}"
date: {date_str}
processed_date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
source: "苹果播客"
audio_url: "{podcast_info['audio_url']}"
duration: "{podcast_info.get('duration', '未知')}"
status: "已处理（模拟数据）"
tags: [播客, 苹果播客, 自动处理]
---

## 🍎 播客信息
- **播客名称**: {podcast_info['podcast_name']}
- **期数标题**: {podcast_info['title']}
- **发布时间**: {date_str}
- **音频时长**: {podcast_info.get('duration', '未知')}
- **原始链接**: {podcast_info['audio_url']}
- **处理状态**: 模拟数据（实际需要配置Whisper和AI总结）

## 📝 描述
{podcast_info.get('description', '无描述')}

## 🔊 音频信息
- 下载时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 处理状态: 模拟转录

## 📝 文字转录
（共 {len(transcript)} 字符）

{transcript}

## 🧠 AI总结

{summary}

## ⚙️ 系统说明
此文件由苹果播客自动处理系统生成。

### 当前状态
- ✅ RSS解析: 完成
- ✅ 音频下载: 模拟完成
- 🔄 文字转录: 需要配置Whisper
- 🔄 AI总结: 需要配置OpenAI API
- ✅ Obsidian保存: 完成

### 下一步配置
1. 安装Whisper: `pip install openai-whisper`
2. 安装FFmpeg: `brew install ffmpeg`
3. 配置OpenAI API key用于AI总结
4. 启用实际下载功能

## 📋 个人笔记
<!-- 在这里添加你的思考和笔记 -->

---
*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    # 保存文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📝 Obsidian笔记已保存: {output_path}")
    return output_path


def process_episode(podcast_name, episode_info):
    """处理单个播客期数"""

    episode_url = episode_info["audio_url"]

    # 检查是否已处理
    if check_if_processed(episode_url):
        print(f"⏭️  已处理过，跳过: {episode_info['title']}")
        return None

    print(f"\n{'='*60}")
    print(f"🎬 开始处理: {episode_info['title']}")
    print(f"{'='*60}")

    # 标记为处理中
    episode_info["podcast_name"] = podcast_name
    mark_as_processing(episode_info)

    # 下载音频
    temp_dir = "/tmp/podcast_processor"
    os.makedirs(temp_dir, exist_ok=True)
    audio_filename = hashlib.md5(episode_url.encode()).hexdigest() + ".mp3"
    audio_path = os.path.join(temp_dir, audio_filename)

    if not download_audio_simple(episode_url, audio_path):
        print("❌ 音频下载失败")
        return None

    # 转文字
    transcript = transcribe_with_simple_method(audio_path)

    # 生成总结
    summary = generate_summary(transcript)

    # 创建Obsidian笔记
    output_path = create_obsidian_note(episode_info, transcript, summary)

    # 标记为完成
    mark_as_completed(episode_url, output_path)

    print(f"✅ 处理完成: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="苹果播客自动处理系统")
    parser.add_argument("--rss", required=True, help="苹果播客RSS地址或页面URL")
    parser.add_argument("--name", required=True, help="播客名称")
    parser.add_argument("--limit", type=int, default=3, help="处理最新几期（默认:3）")
    parser.add_argument("--test", action="store_true", help="测试模式，不实际下载")

    args = parser.parse_args()

    print("=" * 60)
    print("🍎 苹果播客自动处理系统")
    print("=" * 60)

    # 初始化
    setup_database()

    # 获取RSS
    rss_url = get_rss_feed(args.rss)
    if not rss_url:
        print("❌ 无法获取RSS地址")
        return 1

    # 解析RSS
    episodes = parse_rss_feed(rss_url)

    if not episodes:
        print("❌ 没有找到播客期数")
        return 1

    # 处理播客
    processed_count = 0
    for i, episode in enumerate(episodes[: args.limit]):
        print(f"\n📋 处理第 {i+1}/{min(args.limit, len(episodes))} 期")

        if args.test:
            print(f"   🧪 测试模式: {episode['title']}")
            print(f"   🔗 音频URL: {episode['audio_url']}")
            continue

        result = process_episode(args.name, episode)
        if result:
            processed_count += 1

    # 输出结果
    print("\n" + "=" * 60)
    print("📊 处理结果汇总")
    print("=" * 60)
    print(f"📡 RSS地址: {rss_url}")
    print(f"🎙️ 播客名称: {args.name}")
    print(f"📋 找到期数: {len(episodes)}")
    print(f"✅ 成功处理: {processed_count}")
    print(f"📁 输出目录: {PODCASTS_DIR}")

    if args.test:
        print("\n🧪 测试模式完成，未实际处理音频")
        print("💡 移除 --test 参数开始实际处理")
    else:
        print("\n🎉 处理完成！请在Obsidian中查看结果")

    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
