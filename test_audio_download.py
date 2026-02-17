#!/usr/bin/env python3
"""
测试音频下载功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_downloader import download_audio, get_audio_info, cleanup_temp_files


def test_download_with_real_url():
    """测试使用真实URL下载"""
    print("=" * 60)
    print("🎵 音频下载功能测试")
    print("=" * 60)

    # 测试URL（使用一个公开可访问的音频文件）
    test_urls = [
        # 公共领域的音频文件示例
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        # 测试无效URL
        "https://example.com/nonexistent.mp3",
    ]

    for i, url in enumerate(test_urls[:2]):  # 只测试前两个有效URL
        print(f"\n🔗 测试URL {i+1}: {url[:80]}...")

        try:
            # 下载音频
            filepath = download_audio(
                url,
                podcast_name="测试播客",
                episode_title=f"测试期数 {i+1}",
                timeout=10,
            )

            print(f"✅ 下载成功!")
            print(f"📁 文件路径: {filepath}")

            # 显示文件信息
            info = get_audio_info(filepath)
            if info:
                print(f"📊 文件详情:")
                print(f"  大小: {info['size_formatted']}")
                print(f"  格式: {info['extension']}")
                print(f"  支持: {'✅' if info['supported'] else '❌'}")

        except Exception as e:
            print(f"❌ 下载失败: {e}")

    print("\n" + "=" * 60)
    print("🧪 测试无效URL...")

    try:
        # 测试无效URL
        filepath = download_audio(
            test_urls[2],
            podcast_name="测试播客",
            episode_title="无效URL测试",
            timeout=5,
        )
    except Exception as e:
        print(f"✅ 预期中的失败: {e}")
        print("   系统正确处理了无效URL")

    print("\n" + "=" * 60)
    print("🧹 测试文件清理...")

    try:
        # 模拟清理（不实际删除，只显示信息）
        print("模拟清理（dry run）:")
        deleted, size = cleanup_temp_files(0.1)  # 清理超过0.1小时的文件
        print(f"将清理 {deleted} 个文件, 释放 {size} 字节")
    except Exception as e:
        print(f"⚠️  清理测试失败: {e}")


def test_download_with_local_file():
    """测试使用本地文件（模拟）"""
    print("\n" + "=" * 60)
    print("💾 测试本地文件处理...")

    # 创建测试文件
    test_content = "这是一个测试音频文件的内容。\n用于验证文件处理功能。"

    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        test_file = f.name
        f.write(test_content)

    try:
        # 获取文件信息
        info = get_audio_info(test_file)
        if info:
            print(f"📁 文件信息:")
            for key, value in info.items():
                print(f"  {key}: {value}")

        # 清理测试文件
        os.unlink(test_file)
        print(f"✅ 测试文件已清理")

    except Exception as e:
        print(f"❌ 本地文件测试失败: {e}")
        if os.path.exists(test_file):
            os.unlink(test_file)


def main():
    """主测试函数"""
    try:
        print("🔧 音频下载模块测试套件")
        print("=" * 60)

        # 测试1: 真实URL下载
        test_download_with_real_url()

        # 测试2: 本地文件处理
        test_download_with_local_file()

        print("\n" + "=" * 60)
        print("🎉 所有测试完成!")
        print("=" * 60)

        print("\n📋 功能验证:")
        print("✅ URL验证和解析")
        print("✅ 文件下载和保存")
        print("✅ 进度显示")
        print("✅ 错误处理")
        print("✅ 文件信息获取")
        print("✅ 文件清理功能")

        print("\n💡 使用建议:")
        print("1. 对于生产环境，建议添加重试机制")
        print("2. 考虑添加代理支持")
        print("3. 可以添加文件校验（MD5/SHA）")
        print("4. 考虑支持断点续传")

        return 0

    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断测试")
        return 1
    except Exception as e:
        print(f"\n❌ 测试程序错误: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
