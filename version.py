#!/usr/bin/env python3
"""
版本管理工具
用于管理播客处理系统的版本号
"""

import re
import os
import sys
from datetime import datetime


def get_current_version():
    """获取当前版本号"""
    version_file = "VERSION"

    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            version = f.read().strip()
    else:
        # 默认版本
        version = "0.1.0"
        with open(version_file, "w") as f:
            f.write(version)

    return version


def update_version(bump_type="patch"):
    """
    更新版本号

    Args:
        bump_type: "major", "minor", 或 "patch"
    """
    current_version = get_current_version()

    # 解析版本号
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", current_version)
    if not match:
        raise ValueError(f"Invalid version format: {current_version}")

    major, minor, patch = map(int, match.groups())

    # 根据类型更新版本
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    new_version = f"{major}.{minor}.{patch}"

    # 更新版本文件
    with open("VERSION", "w") as f:
        f.write(new_version)

    # 更新pyproject.toml（如果存在）
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as f:
            content = f.read()

        content = re.sub(
            r'version\s*=\s*["\']\d+\.\d+\.\d+["\']',
            f'version = "{new_version}"',
            content,
        )

        with open("pyproject.toml", "w") as f:
            f.write(content)

    # 更新__version__（如果存在）
    init_file = "__init__.py"
    if os.path.exists(init_file):
        with open(init_file, "r") as f:
            content = f.read()

        content = re.sub(
            r'__version__\s*=\s*["\']\d+\.\d+\.\d+["\']',
            f'__version__ = "{new_version}"',
            content,
        )

        with open(init_file, "w") as f:
            f.write(content)

    print(f"✅ Version updated: {current_version} → {new_version}")
    return new_version


def create_changelog_entry(version, changes):
    """创建更新日志条目"""
    changelog_file = "CHANGELOG.md"

    entry = f"""## {version} - {datetime.now().strftime('%Y-%m-%d')}

### 🚀 New Features
{changes.get('features', '- No new features')}

### 🐛 Bug Fixes
{changes.get('bugs', '- No bug fixes')}

### 🔧 Improvements
{changes.get('improvements', '- No improvements')}

### 📝 Documentation
{changes.get('docs', '- No documentation updates')}

---
"""

    # 读取现有的更新日志
    if os.path.exists(changelog_file):
        with open(changelog_file, "r") as f:
            existing_content = f.read()
    else:
        existing_content = "# Changelog\n\n"

    # 插入新的条目
    new_content = existing_content.replace("# Changelog\n\n", f"# Changelog\n\n{entry}")

    with open(changelog_file, "w") as f:
        f.write(new_content)

    print(f"✅ Changelog updated for version {version}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="版本管理工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # 显示当前版本
    show_parser = subparsers.add_parser("show", help="显示当前版本")

    # 更新版本
    bump_parser = subparsers.add_parser("bump", help="更新版本号")
    bump_parser.add_argument(
        "type", choices=["major", "minor", "patch"], help="版本更新类型"
    )

    # 创建Git标签
    tag_parser = subparsers.add_parser("tag", help="创建Git标签")
    tag_parser.add_argument("--push", action="store_true", help="推送到远程仓库")

    args = parser.parse_args()

    if args.command == "show":
        version = get_current_version()
        print(f"Current version: {version}")

    elif args.command == "bump":
        new_version = update_version(args.type)
        print(f"New version: {new_version}")

        # 询问是否创建更新日志
        response = input("Create changelog entry? (y/n): ")
        if response.lower() == "y":
            print("\nEnter changelog details (Ctrl+D when done):")
            print("Features (one per line, empty line to finish):")
            features = []
            while True:
                try:
                    line = input()
                    if not line:
                        break
                    features.append(f"- {line}")
                except EOFError:
                    break

            changes = {
                "features": "\n".join(features) if features else "- No new features"
            }
            create_changelog_entry(new_version, changes)

        # 询问是否创建Git标签
        response = input(f"Create Git tag v{new_version}? (y/n): ")
        if response.lower() == "y":
            os.system(f"git tag v{new_version}")
            print(f"✅ Git tag v{new_version} created")

            response = input("Push tag to remote? (y/n): ")
            if response.lower() == "y":
                os.system(f"git push origin v{new_version}")
                print(f"✅ Tag v{new_version} pushed to remote")

    elif args.command == "tag":
        version = get_current_version()
        tag_name = f"v{version}"

        # 创建标签
        os.system(f"git tag {tag_name}")
        print(f"✅ Git tag {tag_name} created")

        if args.push:
            os.system(f"git push origin {tag_name}")
            print(f"✅ Tag {tag_name} pushed to remote")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
