#!/usr/bin/env python3
"""
播客处理系统配置文件
支持环境变量和 .env 文件配置
"""

import os
import sys
import json
from pathlib import Path

# ==================== 环境变量配置加载 ====================

def load_env_config():
    """
    加载环境变量配置
    优先级：系统环境变量 > .env 文件 > 默认值
    """
    config = {}
    
    # 尝试加载 .env 文件（如果存在）
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            # 简单的 .env 文件解析
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            # 移除引号
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                            os.environ.setdefault(key, value)
                            config[key] = value
            print("✅ 从 .env 文件加载配置")
        except Exception as e:
            print(f"⚠️  加载 .env 文件失败: {e}")
    
    # 从环境变量加载配置
    env_vars = [
        "OPENAI_API_KEY",
        "DEEPGRAM_API_KEY", 
        "ANTHROPIC_API_KEY",
        "DEVELOPMENT_MODE",
        "LOG_LEVEL",
        "TEST_PODCASTS_JSON",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "DATABASE_PATH"
    ]
    
    for env_var in env_vars:
        value = os.environ.get(env_var)
        if value:
            config[env_var] = value
    
    # 解析JSON格式的配置
    if "TEST_PODCASTS_JSON" in config:
        try:
            config["TEST_PODCASTS"] = json.loads(config["TEST_PODCASTS_JSON"])
        except json.JSONDecodeError:
            print(f"⚠️  无法解析 TEST_PODCASTS_JSON: {config['TEST_PODCASTS_JSON']}")
            config["TEST_PODCASTS"] = []
    else:
        config["TEST_PODCASTS"] = []
    
    # 检查关键配置
    if not config.get("OPENAI_API_KEY"):
        print("⚠️  未找到 OpenAI API 密钥，AI总结功能将不可用")
        print("   配置方法: 创建 .env 文件或设置 OPENAI_API_KEY 环境变量")
        print("   参考模板: cp .env.example .env")
    
    return config

# 加载环境配置
ENV_CONFIG = load_env_config()

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

# ==================== 转录配置 ====================

# 转录模式选择（按优先级顺序尝试）:
# 1. "openai_api" - OpenAI Whisper API（需要API key）
# 2. "faster_whisper" - 本地faster-whisper（需要安装）
# 3. "whisper_cpp" - whisper.cpp（纯CPU，需要编译）
# 4. "simplified" - 简化模式（仅下载，不转录）
TRANSCRIPTION_MODE = "simplified"

# OpenAI API配置（如果使用openai_api模式）
OPENAI_API_KEY = ENV_CONFIG.get("OPENAI_API_KEY", "")
OPENAI_WHISPER_MODEL = "whisper-1"

# faster-whisper配置
FASTER_WHISPER_MODEL_SIZE = "base"  # tiny, base, small, medium, large
FASTER_WHISPER_DEVICE = "cpu"  # cpu 或 cuda
FASTER_WHISPER_COMPUTE_TYPE = "int8"  # int8, int16, float16, float32

# 转录语言（zh, en, ja等）
TRANSCRIPT_LANGUAGE = "zh"

# ==================== AI总结配置 ====================

AI_SUMMARY_ENABLED = False
AI_MODEL = "gpt-3.5-turbo"
AI_MAX_TOKENS = 1000

# ==================== 音频下载配置 ====================

# 下载超时时间（秒）
DOWNLOAD_TIMEOUT = 30

# 最大重试次数
DOWNLOAD_MAX_RETRIES = 3

# 临时文件保留时间（小时）
TEMP_FILE_MAX_AGE_HOURS = 24

# 支持的文件格式（用于验证）
SUPPORTED_AUDIO_FORMATS = [".mp3", ".m4a", ".wav", ".ogg", ".flac", ".aac"]

# ==================== 播客源配置 ====================

# 默认播客订阅（可以在运行时覆盖）
# 优先使用环境变量中的测试播客，如果没有则使用默认
TEST_PODCASTS = ENV_CONFIG.get("TEST_PODCASTS", [])
if TEST_PODCASTS:
    DEFAULT_SUBSCRIPTIONS = TEST_PODCASTS
else:
    DEFAULT_SUBSCRIPTIONS = [
        {"name": "测试播客", "rss": "https://example.com/podcast.rss", "enabled": True}
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
    warnings = []

    # 检查Obsidian目录
    if not os.path.exists(OBSIDIAN_VAULT):
        errors.append(f"Obsidian知识库不存在: {OBSIDIAN_VAULT}")

    # 创建必要的目录
    directories = [
        PODCASTS_DIR,
        os.path.join(PROJECT_ROOT, "logs"),
        os.path.join(PROJECT_ROOT, "templates"),
        TEMP_DIR,
    ]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            errors.append(f"无法创建目录 {directory}: {e}")

    # 检查API密钥配置
    if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
        warnings.append("OpenAI API密钥未配置，AI总结和Whisper API功能将不可用")
        warnings.append("  配置方法: 创建 .env 文件或设置 OPENAI_API_KEY 环境变量")
        warnings.append("  参考模板: cp .env.example .env")
    
    # 检查环境配置文件是否存在
    env_file = os.path.join(PROJECT_ROOT, ".env")
    if not os.path.exists(env_file):
        warnings.append("环境配置文件不存在: .env")
        warnings.append("  创建模板: cp .env.example .env")
        warnings.append("  然后编辑 .env 填入你的API密钥")

    return errors, warnings


def get_config_summary():
    """获取配置摘要"""
    return {
        "obsidian_vault": OBSIDIAN_VAULT,
        "podcasts_dir": PODCASTS_DIR,
        "project_root": PROJECT_ROOT,
        "db_path": DB_PATH,
        "temp_dir": TEMP_DIR,
        "default_limit": DEFAULT_PROCESS_LIMIT,
        "transcription_mode": TRANSCRIPTION_MODE,
        "language": TRANSCRIPT_LANGUAGE,
        "ai_summary_enabled": AI_SUMMARY_ENABLED,
        "download_timeout": DOWNLOAD_TIMEOUT,
        "download_max_retries": DOWNLOAD_MAX_RETRIES,
        "temp_file_max_age_hours": TEMP_FILE_MAX_AGE_HOURS,
    }


if __name__ == "__main__":
    # 测试配置
    errors, warnings = validate_config()
    
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠️  配置警告:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors:
        print("\n✅ 基础配置验证通过")
        summary = get_config_summary()
        print("\n📋 配置摘要:")
        for key, value in summary.items():
            if "key" in key.lower() and value:
                # 隐藏API密钥的具体值
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***隐藏***"
                print(f"  {key}: {masked_value}")
            else:
                print(f"  {key}: {value}")
        
        # 显示环境配置状态
        print("\n🔒 环境配置状态:")
        print(f"  OpenAI API密钥: {'✅ 已配置' if OPENAI_API_KEY and OPENAI_API_KEY.strip() else '❌ 未配置'}")
        print(f"  测试播客数量: {len(TEST_PODCASTS)}")
        print(f"  开发模式: {ENV_CONFIG.get('DEVELOPMENT_MODE', '未设置')}")
        print(f"  日志级别: {ENV_CONFIG.get('LOG_LEVEL', '未设置')}")
        
        # 安全建议
        print("\n💡 安全建议:")
        print("  1. 确保 .env 文件不在Git版本控制中")
        print("  2. 定期轮换API密钥")
        print("  3. 生产环境使用系统环境变量")
