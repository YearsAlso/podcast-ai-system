#!/usr/bin/env python3
"""
OpenClaw集成测试脚本
测试播客处理系统与OpenClaw的集成
"""

import subprocess
import os
import sys
from pathlib import Path


def test_environment():
    """测试环境依赖"""
    print("🔧 测试环境依赖...")

    tests = [
        ("Python3", ["python3", "--version"]),
        (
            "Whisper",
            [
                "python3",
                "-c",
                "import whisper; print('Whisper版本:', whisper.__version__)",
            ],
        ),
        ("FFmpeg", ["ffmpeg", "-version"]),
    ]

    all_passed = True
    for name, cmd in tests:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name}: 正常")
                # 打印版本信息
                output = result.stdout.strip()[:50]
                if output:
                    print(f"   📋 {output}")
            else:
                print(f"❌ {name}: 失败")
                print(f"   错误: {result.stderr[:100]}")
                all_passed = False
        except FileNotFoundError:
            print(f"❌ {name}: 未安装")
            all_passed = False

    return all_passed


def test_script_help():
    """测试脚本帮助功能"""
    print("\n📖 测试脚本帮助...")

    script_path = os.path.join(os.path.dirname(__file__), "simple_podcast_processor.py")

    try:
        result = subprocess.run(
            ["python3", script_path, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ 脚本帮助正常")
            # 提取帮助信息的关键部分
            help_lines = result.stdout.split("\n")[:10]
            for line in help_lines:
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print("❌ 脚本帮助失败")
            print(f"   错误: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 脚本帮助超时")
        return False
    except Exception as e:
        print(f"❌ 脚本帮助异常: {e}")
        return False


def test_obsidian_structure():
    """测试Obsidian目录结构"""
    print("\n📁 测试Obsidian目录结构...")

    obsidian_vault = "/Volumes/MxStore/Project/YearsAlso"
    podcasts_dir = os.path.join(obsidian_vault, "Podcasts")

    # 检查目录是否存在
    if os.path.exists(obsidian_vault):
        print(f"✅ Obsidian知识库: {obsidian_vault}")

        # 创建Podcasts目录（如果不存在）
        os.makedirs(podcasts_dir, exist_ok=True)
        print(f"✅ Podcasts目录: {podcasts_dir}")

        # 检查写入权限
        test_file = os.path.join(podcasts_dir, "test_permission.md")
        try:
            with open(test_file, "w") as f:
                f.write("# 测试文件\n测试写入权限")
            os.remove(test_file)
            print("✅ 目录可写入")
            return True
        except Exception as e:
            print(f"❌ 目录不可写入: {e}")
            return False
    else:
        print(f"❌ Obsidian知识库不存在: {obsidian_vault}")
        return False


def test_openclaw_integration():
    """测试OpenClaw集成命令"""
    print("\n🔌 测试OpenClaw集成命令...")

    # 模拟OpenClaw exec命令
    test_commands = [
        {
            "name": "查看帮助",
            "cmd": "cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 simple_podcast_processor.py --help",
        },
        {
            "name": "处理测试文件（模拟）",
            "cmd": "echo '这是模拟的OpenClaw命令' && cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && echo '测试完成'",
        },
    ]

    all_passed = True
    for test in test_commands:
        print(f"\n🧪 测试: {test['name']}")
        print(f"   💻 命令: {test['cmd'][:80]}...")

        try:
            # 在实际OpenClaw中，这里会是 exec() 调用
            # 现在我们用subprocess模拟
            result = subprocess.run(
                test["cmd"], shell=True, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                print(f"   ✅ 命令执行成功")
                # 显示部分输出
                output_preview = result.stdout.strip()[:100]
                if output_preview:
                    print(f"     输出: {output_preview}...")
            else:
                print(f"   ❌ 命令执行失败")
                print(f"     错误: {result.stderr[:200]}")
                all_passed = False

        except subprocess.TimeoutExpired:
            print(f"   ⚠️ 命令执行超时")
        except Exception as e:
            print(f"   ❌ 命令执行异常: {e}")
            all_passed = False

    return all_passed


def generate_openclaw_commands():
    """生成OpenClaw可用的命令"""
    print("\n📋 生成OpenClaw命令...")

    commands = {
        "处理本地播客": "cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 simple_podcast_processor.py --file '音频文件路径' --podcast '播客名称' --episode '期数标题'",
        "处理在线播客": "cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 simple_podcast_processor.py --url '音频URL' --podcast '播客名称' --episode '期数标题'",
        "查看帮助": "cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 simple_podcast_processor.py --help",
        "测试环境": "cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 test_integration.py",
    }

    print("以下命令可以在OpenClaw中直接使用：")
    print("-" * 60)

    for name, cmd in commands.items():
        print(f"\n🔹 {name}:")
        print(f"   ```bash")
        print(f"   {cmd}")
        print(f"   ```")

    print("-" * 60)

    return commands


def main():
    """主测试函数"""
    print("=" * 60)
    print("🎙️ OpenClaw播客处理系统集成测试")
    print("=" * 60)

    test_results = []

    # 运行测试
    test_results.append(("环境依赖", test_environment()))
    test_results.append(("脚本帮助", test_script_help()))
    test_results.append(("Obsidian结构", test_obsidian_structure()))
    test_results.append(("OpenClaw集成", test_openclaw_integration()))

    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    all_passed = True
    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！系统可以正常集成到OpenClaw。")

        # 生成OpenClaw命令
        generate_openclaw_commands()

        print("\n🚀 下一步：")
        print("1. 在OpenClaw中尝试执行上述命令")
        print("2. 处理一个测试音频文件")
        print("3. 在Obsidian中查看生成的文件")

    else:
        print("⚠️  部分测试失败，请检查问题：")
        print("1. 运行 ./install_deps.sh 安装依赖")
        print("2. 检查文件权限")
        print("3. 查看详细错误信息")

    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
