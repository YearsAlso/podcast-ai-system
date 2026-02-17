# 🎙️ OpenClaw 播客处理系统

最简单的播客转文字AI总结方案，专为OpenClaw设计。

## 🚀 快速开始

### 1. 安装依赖
```bash
cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统
chmod +x install_deps.sh
./install_deps.sh
```

### 2. 基本使用

#### 处理本地音频文件
```bash
python3 simple_podcast_processor.py \
  --file "/path/to/your/audio.mp3" \
  --podcast "播客名称" \
  --episode "第XX期：标题"
```

#### 处理在线音频
```bash
python3 simple_podcast_processor.py \
  --url "https://example.com/podcast.mp3" \
  --podcast "播客名称" \
  --episode "第XX期：标题"
```

### 3. OpenClaw集成

#### 方法一：直接exec调用
```python
# 在OpenClaw中执行
exec("cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 simple_podcast_processor.py --file 'audio.mp3' --podcast '测试播客' --episode '测试期数'")
```

#### 方法二：创建快捷命令
在OpenClaw的TOOLS.md中添加：
```markdown
### 播客处理
- 处理播客: `cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 simple_podcast_processor.py`
```

## 📁 文件结构

```
系统方案/播客处理系统/
├── simple_podcast_processor.py  # 主处理脚本
├── install_deps.sh              # 依赖安装脚本
├── README.md                    # 说明文档
└── config.example.json          # 配置文件示例
```

输出文件保存在：
```
/Volumes/MxStore/Project/YearsAlso/Podcasts/
└── [播客名称]/
    └── YYYY-MM-DD_[播客名称]_[期数标题].md
```

## 🛠️ 功能特点

### ✅ 已实现
- [x] 音频转文字（Whisper）
- [x] 自动保存到Obsidian
- [x] 支持本地文件和在线URL
- [x] 简单的Markdown模板
- [x] 自动清理临时文件

### 🔄 待实现（可选）
- [ ] OpenAI AI总结（需要API key）
- [ ] 说话人分离
- [ ] RSS订阅自动抓取
- [ ] 图形界面
- [ ] 批量处理

## ⚙️ 配置说明

### 1. 基本配置
脚本使用默认配置，无需额外设置。

### 2. 高级配置（可选）
如需使用AI总结功能，需要：
1. 获取OpenAI API key
2. 在脚本中配置API key
3. 启用`summarize_with_gpt()`函数

## 🧪 测试

### 测试1：查看帮助
```bash
python3 simple_podcast_processor.py --help
```

### 测试2：处理示例音频
```bash
# 下载测试音频（可选）
curl -o test_audio.mp3 "https://example.com/test.mp3"

# 处理测试音频
python3 simple_podcast_processor.py \
  --file "test_audio.mp3" \
  --podcast "测试播客" \
  --episode "测试期数"
```

## 🔍 故障排除

### 常见问题

1. **Whisper模型下载失败**
   ```bash
   # 手动下载模型
   python3 -c "import whisper; whisper.load_model('base')"
   ```

2. **FFmpeg未安装**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt install ffmpeg
   ```

3. **权限问题**
   ```bash
   chmod +x *.py *.sh
   ```

### 日志查看
脚本会在控制台输出详细日志，包括：
- 下载进度
- 转录状态
- 文件保存位置

## 📈 性能说明

### 硬件要求
- **CPU**: 现代处理器即可
- **内存**: 至少2GB空闲内存
- **存储**: Whisper模型约100-300MB

### 处理时间
- 1分钟音频：约30-60秒
- 30分钟音频：约5-10分钟
- 1小时音频：约15-20分钟

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License