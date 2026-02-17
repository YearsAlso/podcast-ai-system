#!/usr/bin/env python3
"""
基础测试文件
用于GitHub Actions中的自动化测试
"""

import sys
import os


def test_imports():
    """测试基础导入"""
    print("Testing imports...")

    try:
        import config

        print("✅ config module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False

    try:
        from config import OBSIDIAN_VAULT, PODCASTS_DIR

        print("✅ Config variables imported successfully")
        print(f"   Obsidian vault: {OBSIDIAN_VAULT}")
        print(f"   Podcasts dir: {PODCASTS_DIR}")
    except ImportError as e:
        print(f"❌ Failed to import config variables: {e}")
        return False

    return True


def test_config_validation():
    """测试配置验证"""
    print("\nTesting config validation...")

    try:
        from config import validate_config

        errors = validate_config()

        if errors:
            print("⚠️  Config validation warnings:")
            for error in errors:
                print(f"   - {error}")
            # 对于测试环境，警告是可以接受的
            return True
        else:
            print("✅ Config validation passed")
            return True
    except Exception as e:
        print(f"❌ Config validation failed: {e}")
        return False


def test_main_script():
    """测试主脚本"""
    print("\nTesting main script...")

    try:
        # 模拟命令行参数
        import argparse

        # 测试帮助命令
        print("Testing --help command...")
        import subprocess

        result = subprocess.run(
            [sys.executable, "podcast_processor.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ --help command works")
            return True
        else:
            print(f"❌ --help command failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Main script test failed: {e}")
        return False


def test_docker_build():
    """测试Docker构建（如果Docker可用）"""
    print("\nTesting Docker build...")

    try:
        import subprocess

        # 检查Docker是否可用
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠️  Docker not available, skipping Docker tests")
            return True  # 跳过不是错误

        # 测试Dockerfile语法
        print("Checking Dockerfile syntax...")
        result = subprocess.run(
            ["docker", "build", "--no-cache", "-t", "test-podcast", "."],
            capture_output=True,
            text=True,
            timeout=300,  # 5分钟超时
        )

        if result.returncode == 0:
            print("✅ Docker build successful")

            # 清理测试镜像
            subprocess.run(["docker", "rmi", "test-podcast"], capture_output=True)
            return True
        else:
            print(f"❌ Docker build failed: {result.stderr[:500]}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Docker build timed out")
        return False
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Running Podcast AI System Tests")
    print("=" * 60)

    tests = [
        ("Import tests", test_imports),
        ("Config validation", test_config_validation),
        ("Main script", test_main_script),
        ("Docker build", test_docker_build),
    ]

    all_passed = True
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} raised exception: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
