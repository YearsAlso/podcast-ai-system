#!/usr/bin/env python3
"""
安全配置模板 - 请复制此文件为 config_secrets.py 并填写你的API密钥
此文件已添加到 .gitignore，不会上传到GitHub
"""

# ==================== API密钥配置 ====================

# OpenAI API密钥（用于AI总结和Whisper API转录）
# 获取地址：https://platform.openai.com/api-keys
OPENAI_API_KEY = "sk-你的OpenAI API密钥"

# 可选：其他API密钥（如果需要）
# DEEPGRAM_API_KEY = "你的Deepgram API密钥"  # 用于替代Whisper的转录服务
# ANTHROPIC_API_KEY = "你的Anthropic API密钥"  # 用于Claude AI总结

# ==================== 测试播客配置 ====================

# 测试用的播客RSS链接（用于开发和测试）
TEST_PODCASTS = [
    {
        "name": "测试播客1",
        "rss": "https://example.com/podcast1.rss",
        "enabled": True
    },
    {
        "name": "测试播客2", 
        "rss": "https://example.com/podcast2.rss",
        "enabled": True
    }
]

# ==================== 环境特定配置 ====================

# 开发环境设置
DEVELOPMENT_MODE = True  # 设置为False进入生产模式

# 代理设置（如果需要）
# PROXY_SETTINGS = {
#     "http": "http://your-proxy:port",
#     "https": "https://your-proxy:port",
# }

# ==================== 使用说明 ====================

"""
使用步骤：
1. 复制此文件：cp config_secrets_template.py config_secrets.py
2. 编辑 config_secrets.py 文件，填入你的API密钥
3. 系统会自动加载 config_secrets.py 中的配置

安全提示：
- 永远不要将 config_secrets.py 上传到GitHub
- 定期轮换API密钥
- 使用环境变量作为备选方案
"""

if __name__ == "__main__":
    print("🔒 安全配置模板")
    print("=" * 60)
    print("请复制此文件为 config_secrets.py 并填写你的API密钥")
    print("此文件已添加到 .gitignore，不会上传到GitHub")