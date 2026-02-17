#!/bin/bash
# 播客处理系统安装脚本

set -e

echo "🎙️ 播客处理系统安装"
echo "========================"

# 项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "项目目录: $PROJECT_DIR"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要Python 3.8+，请先安装Python"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 创建虚拟环境（可选）
read -p "是否创建Python虚拟环境？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🐍 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装基础依赖
echo "📦 安装Python依赖..."
pip3 install requests feedparser

# 安装转录相关依赖（可选）
echo "🎤 转录方案选择:"
echo "  1. OpenAI Whisper API（推荐，需要API key）"
echo "  2. faster-whisper（本地轻量版）"
echo "  3. 简化模式（默认，无需安装）"
read -p "选择转录方案 (1/2/3，默认3): " -n 1 -r
echo

if [[ $REPLY =~ ^[1]$ ]]; then
    echo "🔗 安装OpenAI Whisper API支持..."
    pip3 install openai
    echo "✅ OpenAI库已安装"
    echo "💡 需要在 config.py 中设置 OPENAI_API_KEY"
    
elif [[ $REPLY =~ ^[2]$ ]]; then
    echo "⚡ 安装faster-whisper..."
    pip3 install faster-whisper
    echo "✅ faster-whisper已安装"
    echo "💡 建议同时安装FFmpeg以支持更多音频格式"
fi

# 设置执行权限
echo "🔧 设置脚本权限..."
chmod +x "$PROJECT_DIR"/*.py

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/templates"

# 检查Obsidian目录
OBSIDIAN_VAULT="/Volumes/MxStore/Project/YearsAlso"
if [ ! -d "$OBSIDIAN_VAULT" ]; then
    echo "⚠️  Obsidian知识库不存在: $OBSIDIAN_VAULT"
    echo "   请确保Obsidian知识库路径正确"
else
    echo "✅ Obsidian知识库: $OBSIDIAN_VAULT"
    
    # 创建播客目录
    PODCASTS_DIR="$OBSIDIAN_VAULT/Podcasts"
    mkdir -p "$PODCASTS_DIR"
    echo "✅ 播客笔记目录: $PODCASTS_DIR"
fi

# 测试配置
echo "⚙️ 测试配置..."
python3 "$PROJECT_DIR/config.py"

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 下一步:"
echo "1. 测试系统: python3 podcast_processor.py --help"
echo "2. 添加测试订阅: python3 podcast_processor.py add --name '测试' --rss 'https://example.com/rss'"
echo "3. 测试处理: python3 podcast_processor.py process --name '测试' --test"
echo "4. 查看配置: python3 podcast_processor.py config"
echo ""
echo "💡 提示:"
echo "- 系统代码在: $PROJECT_DIR"
echo "- 生成的笔记在: $PODCASTS_DIR"
echo "- 需要进一步配置Whisper和AI总结功能"
echo ""
echo "🔧 转录功能配置:"
echo "  - 当前模式: 简化模式（默认）"
echo "  - 可选方案: OpenAI API / faster-whisper / whisper.cpp"
echo "  - 配置方法: 修改 config.py 中的 TRANSCRIPTION_MODE"
echo ""
echo "🔧 其他待配置功能:"
echo "  - AI总结: 需要配置OpenAI API"
echo "  - RSS解析: 需要实现真正的解析逻辑"
echo "  - 音频下载: 需要实现下载功能"