#!/usr/bin/env python3
"""
最简单的播客转文字AI总结脚本
OpenClaw可以直接调用此脚本
"""

import argparse
import os
import sys
from datetime import datetime

# 配置
OBSIDIAN_VAULT = "/Volumes/MxStore/Project/YearsAlso"
DEFAULT_OUTPUT_DIR = os.path.join(OBSIDIAN_VAULT, "Podcasts")


def setup_environment():
    """检查环境依赖"""
    try:
        import whisper  # noqa: F401

        print("✅ Whisper已安装")
    except ImportError:
        print("❌ 需要安装Whisper: pip install openai-whisper")
        return False

    # 检查FFmpeg
    ffmpeg_check = os.system("which ffmpeg > /dev/null 2>&1")
    if ffmpeg_check != 0:
        print("❌ 需要安装FFmpeg: brew install ffmpeg (macOS)")
        return False

    print("✅ 环境检查通过")
    return True


def download_audio(url, output_path):
    """下载音频文件（简单版本）"""
    import requests

    print(f"📥 下载音频: {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"✅ 下载完成: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False


def transcribe_audio(audio_path, model_size="base"):
    """使用Whisper转录音频"""
    print(f"🎤 开始转文字: {audio_path}")

    try:
        # 加载模型（第一次运行会下载模型）
        model = whisper.load_model(model_size)  # noqa: F821

        # 转录音频
        result = model.transcribe(
            audio_path, language="zh", fp16=False  # 中文  # CPU模式
        )

        transcript = result["text"]
        print(f"✅ 转文字完成，长度: {len(transcript)} 字符")
        return transcript
    except Exception as e:
        print(f"❌ 转文字失败: {e}")
        return None


def simple_summary(transcript, max_length=4000):
    """简单的文本总结（如果没配置OpenAI，就返回摘要）"""

    # 如果没有OpenAI API key，使用简单摘要
    transcript_preview = (
        transcript[:500] + "..." if len(transcript) > 500 else transcript
    )

    summary = f"""
## 内容摘要
（OpenAI API未配置，使用简单摘要）

**主要内容预览**:
{transcript_preview}

**关键信息**:
- 音频时长: 需要配置Whisper详细模式获取
- 文字长度: {len(transcript)} 字符
- 处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**使用建议**:
1. 配置OpenAI API key以获得AI总结
2. 或手动阅读转录文字提取重点
"""
    return summary


def create_obsidian_note(transcript, summary, metadata, output_path):
    """创建Obsidian笔记"""

    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 构建Markdown内容
    content = f"""---
podcast: "{metadata.get('podcast', '未知播客')}"
episode: "{metadata.get('episode', '未知期数')}"
date: {metadata.get('date', datetime.now().strftime('%Y-%m-%d'))}
processed_date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
source: "{metadata.get('source', '手动处理')}"
status: "已转录"
tags: [播客, 转录]
---

## 🎧 播客信息
- **播客名称**: {metadata.get('podcast', '未知')}
- **期数标题**: {metadata.get('episode', '未知')}
- **处理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **原始链接**: {metadata.get('url', '无')}

## 📝 文字转录
（共 {len(transcript)} 字符）

{transcript}

## 🧠 总结

{summary}

## 💡 使用说明
1. 此文件由OpenClaw播客处理脚本生成
2. 如需AI总结，请配置OpenAI API key
3. 可以在下方添加个人笔记

## 📋 个人笔记
<!-- 在这里添加你的思考和笔记 -->

"""

    # 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📝 Obsidian笔记已保存: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="播客转文字AI总结工具")
    parser.add_argument("--url", help="播客音频URL")
    parser.add_argument("--file", help="本地音频文件路径")
    parser.add_argument("--podcast", default="未命名播客", help="播客名称")
    parser.add_argument("--episode", default="未命名期数", help="期数标题")
    parser.add_argument("--output", help="输出文件路径（可选）")

    args = parser.parse_args()

    # 检查环境
    if not setup_environment():
        return 1

    # 确定音频文件
    audio_path = None
    if args.file and os.path.exists(args.file):
        audio_path = args.file
        print(f"📁 使用本地文件: {audio_path}")
    elif args.url:
        # 下载音频
        temp_dir = "/tmp/podcast_processor"
        os.makedirs(temp_dir, exist_ok=True)
        audio_path = os.path.join(
            temp_dir, f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )

        if not download_audio(args.url, audio_path):
            return 1
    else:
        print("❌ 请提供 --url 或 --file 参数")
        return 1

    # 转文字
    transcript = transcribe_audio(audio_path)
    if not transcript:
        return 1

    # 生成总结
    summary = simple_summary(transcript)

    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        # 默认路径
        safe_name = args.podcast.replace(" ", "_").replace("/", "_")
        safe_episode = args.episode.replace(" ", "_").replace("/", "_")[:50]
        filename = (
            f"{datetime.now().strftime('%Y-%m-%d')}_{safe_name}_{safe_episode}.md"
        )
        output_path = os.path.join(DEFAULT_OUTPUT_DIR, safe_name, filename)

    # 创建Obsidian笔记
    metadata = {
        "podcast": args.podcast,
        "episode": args.episode,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "url": args.url if args.url else args.file,
    }

    note_path = create_obsidian_note(transcript, summary, metadata, output_path)

    print("\n" + "=" * 50)
    print("🎉 处理完成!")
    print(f"📁 输出文件: {note_path}")
    print(f"📊 转录长度: {len(transcript)} 字符")
    print("=" * 50)

    # 清理临时文件
    if args.url and os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"🧹 已清理临时文件: {audio_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
