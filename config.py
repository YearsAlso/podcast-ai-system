#!/usr/bin/env python3
"""
播客处理系统配置文件
"""

import os

# ==================== 路径配置 ====================

# Obsidian知识库路径
OBSIDIAN_VAULT = "/Volumes/MxStore/Project/YearsAlso"

# 播客笔记保存目录（在Obsidian中）
PODCASTS_DIR = os.path.join(OBSIDIAN_VAULT, "Podcasts")

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, "podcasts.db")

# 临时文件目录
TEMP_DIR = "/tmp/podcast_processor"

# ==================== 处理配置 ====================

# 默认处理最新几期
DEFAULT_PROCESS_LIMIT = 3

# 转录模型大小（base, small, medium, large）
WHISPER_MODEL_SIZE = "base"

# 转录语言（zh, en, ja等）
TRANSCRIPT_LANGUAGE = "zh"

# AI总结配置
AI_SUMMARY_ENABLED = False
AI_MODEL = "gpt-3.5-turbo"
AI_MAX_TOKENS = 1000

# ==================== 播客源配置 ====================

# 默认播客订阅（可以在运行时覆盖）
DEFAULT_SUBSCRIPTIONS = [
    {
        "name": "测试播客",
        "rss": "https://example.com/podcast.rss",
        "enabled": True
    }
]

# ==================== 输出配置 ====================

# Markdown模板文件
TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "templates", "podcast_note.md")

# 日志文件
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "podcast_processor.log")

# ==================== 验证配置 ====================

def validate_config():
    """验证配置是否有效"""
    errors = []
    
    # 检查Obsidian目录
    if not os.path.exists(OBSIDIAN_VAULT):
        errors.append(f"Obsidian知识库不存在: {OBSIDIAN_VAULT}")
    
    # 创建必要的目录
    directories = [
        PODCASTS_DIR,
        os.path.join(PROJECT_ROOT, "logs"),
        os.path.join(PROJECT_ROOT, "templates"),
        TEMP_DIR
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            errors.append(f"无法创建目录 {directory}: {e}")
    
    return errors

def get_config_summary():
    """获取配置摘要"""
    return {
        "obsidian_vault": OBSIDIAN_VAULT,
        "podcasts_dir": PODCASTS_DIR,
        "project_root": PROJECT_ROOT,
        "db_path": DB_PATH,
        "temp_dir": TEMP_DIR,
        "default_limit": DEFAULT_PROCESS_LIMIT,
        "whisper_model": WHISPER_MODEL_SIZE,
        "language": TRANSCRIPT_LANGUAGE,
        "ai_summary_enabled": AI_SUMMARY_ENABLED
    }

if __name__ == "__main__":
    # 测试配置
    errors = validate_config()
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ 配置验证通过")
        summary = get_config_summary()
        print("\n📋 配置摘要:")
        for key, value in summary.items():
            print(f"  {key}: {value}")