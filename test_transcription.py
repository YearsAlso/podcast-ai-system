#!/usr/bin/env python3
"""
测试转录模块
演示多种转录方案的使用
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transcription import get_transcription_info, transcribe_audio


def test_transcription_modes():
    """测试各种转录模式"""
    print("=" * 60)
    print("🎤 播客转录方案测试")
    print("=" * 60)

    # 获取当前配置信息
    print("\n📋 当前转录配置:")
    info = get_transcription_info()
    for key, value in info.items():
        if isinstance(value, list):
            print(f"  {key}: {', '.join(value)}")
        else:
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)

    # 创建测试音频文件
    print("\n📁 创建测试音频文件...")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        test_audio_path = f.name
        f.write("""这是测试音频文件的内容。
用于演示播客转录功能。

系统支持多种转录方案：
1. OpenAI Whisper API（在线）
2. faster-whisper（本地轻量版）
3. whisper.cpp（纯CPU）
4. 简化模式（默认）

当前系统会自动选择可用的最佳方案。
""")

    try:
        # 测试转录
        print(f"\n🎬 开始转录测试...")
        print(f"   文件: {Path(test_audio_path).name}")
        print(f"   模式: {info['current_mode']}")

        transcript = transcribe_audio(
            test_audio_path, podcast_name="测试播客", episode_title="转录方案演示"
        )

        print("\n✅ 转录完成!")
        print("=" * 60)
        print("\n📝 转录结果预览:")
        print("-" * 40)
        print(transcript[:500] + ("..." if len(transcript) > 500 else ""))
        print("-" * 40)
        print(f"总长度: {len(transcript)} 字符")

        # 显示建议
        print("\n" + "=" * 60)
        print("💡 使用建议:")

        current_mode = info["current_mode"]
        available_modes = info["available_modes"]

        if current_mode == "simplified":
            print("当前使用简化模式，建议启用完整转录:")

            if "openai_api" in available_modes:
                print(
                    "1. ✅ OpenAI API 已配置，可以设置: TRANSCRIPTION_MODE = 'openai_api'"
                )
            else:
                print("1. 🔄 配置OpenAI API key以使用在线转录")

            if "faster_whisper" in available_modes:
                print(
                    "2. ✅ faster-whisper 已安装，可以设置: TRANSCRIPTION_MODE = 'faster_whisper'"
                )
            else:
                print("2. 🔄 安装faster-whisper: pip install faster-whisper")

            if "whisper_cpp" in available_modes:
                print(
                    "3. ✅ whisper.cpp 已安装，可以设置: TRANSCRIPTION_MODE = 'whisper_cpp'"
                )
            else:
                print("3. 🔄 安装whisper.cpp: https://github.com/ggerganov/whisper.cpp")

        elif current_mode == "openai_api":
            print("✅ 正在使用OpenAI Whisper API，这是推荐方案")
            print("   确保API key有足够的额度")

        elif current_mode == "faster_whisper":
            print("✅ 正在使用faster-whisper，本地轻量方案")
            print("   可以尝试不同的模型大小: tiny, base, small, medium, large")

        elif current_mode == "whisper_cpp":
            print("✅ 正在使用whisper.cpp，纯CPU方案")
            print("   适合没有GPU的环境")

    except Exception as e:
        print(f"\n❌ 转录测试失败: {e}")
        print("\n💡 故障排除:")
        print("1. 检查 config.py 中的配置")
        print("2. 确保依赖已安装")
        print("3. 查看详细错误信息")

    finally:
        # 清理临时文件
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)

    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    print("=" * 60)


def main():
    """主函数"""
    try:
        test_transcription_modes()
        return 0
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 测试程序错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
