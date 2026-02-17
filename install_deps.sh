#!/bin/bash
# 安装播客处理系统的依赖

echo "🔧 安装播客处理系统依赖"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要Python3，请先安装Python3"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install openai-whisper

# 检查是否安装成功
if python3 -c "import whisper" &> /dev/null; then
    echo "✅ Whisper 安装成功"
else
    echo "❌ Whisper 安装失败"
    exit 1
fi

# 安装FFmpeg (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 检测到macOS，检查FFmpeg..."
    if ! command -v ffmpeg &> /dev/null; then
        echo "📥 安装FFmpeg..."
        brew install ffmpeg
    fi
    echo "✅ FFmpeg 已安装: $(ffmpeg -version | head -1)"
fi

# 安装requests（如果需要）
pip3 install requests

# 创建必要的目录
echo "📁 创建目录结构..."
OBSIDIAN_VAULT="/Volumes/MxStore/Project/YearsAlso"
mkdir -p "$OBSIDIAN_VAULT/Podcasts"
mkdir -p "$OBSIDIAN_VAULT/系统方案/播客处理系统"

# 设置脚本权限
chmod +x "$OBSIDIAN_VAULT/系统方案/播客处理系统/simple_podcast_processor.py"

echo ""
echo "🎉 依赖安装完成!"
echo ""
echo "📋 下一步:"
echo "1. 测试脚本: python3 simple_podcast_processor.py --help"
echo "2. 处理本地音频: python3 simple_podcast_processor.py --file /path/to/audio.mp3 --podcast '播客名' --episode '期数标题'"
echo "3. 处理在线音频: python3 simple_podcast_processor.py --url '音频链接' --podcast '播客名' --episode '期数标题'"
echo ""
echo "💡 提示:"
echo "- 第一次运行会下载Whisper模型（约100-300MB）"
echo "- 可以在Obsidian的Podcasts目录查看生成的文件"