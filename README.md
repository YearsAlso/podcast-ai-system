# 🎙️ Podcast AI Processing System

[![GitHub](https://img.shields.io/github/license/YearsAlso/podcast-ai-system)](https://github.com/YearsAlso/podcast-ai-system/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Integrated-green)](https://openclaw.ai/)
[![CI/CD](https://github.com/YearsAlso/podcast-ai-system/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/YearsAlso/podcast-ai-system/actions/workflows/ci-cd.yml)
[![Docker](https://img.shields.io/badge/docker-available-blue)](https://ghcr.io/YearsAlso/podcast-ai-system)
[![Release](https://img.shields.io/github/v/release/YearsAlso/podcast-ai-system)](https://github.com/YearsAlso/podcast-ai-system/releases)

自动爬取苹果播客 → 音频转文字 → AI智能总结 → 保存到Obsidian知识库

## ✨ 功能特性

### ✅ 已实现
- **系统框架** - 完整的命令行界面
- **数据库管理** - SQLite存储订阅和处理记录
- **Obsidian集成** - 自动生成Markdown笔记
- **订阅管理** - 添加、列出、管理播客订阅
- **配置系统** - 灵活的配置文件

### 🔄 待配置（需要额外设置）
- **音频转文字** - 使用OpenAI Whisper（需要安装）
- **AI智能总结** - 使用GPT模型（需要API key）
- **RSS解析** - 自动获取播客更新
- **音频下载** - 自动下载播客音频

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/YearsAlso/podcast-ai-system.git
cd podcast-ai-system
```

### 2. 安装依赖
```bash
# 运行安装脚本
chmod +x setup.sh
./setup.sh

# 或手动安装
pip install requests feedparser
```

### 3. 配置系统
编辑 `config.py` 设置你的Obsidian知识库路径：
```python
OBSIDIAN_VAULT = "/path/to/your/obsidian/vault"
```

### 4. 基本使用
```bash
# 查看帮助
python podcast_processor.py --help

# 添加播客订阅
python podcast_processor.py add --name "得到" --rss "https://example.com/rss"

# 测试处理（生成示例笔记）
python podcast_processor.py process --name "得到" --test

# 查看处理历史
python podcast_processor.py history
```

## 🎤 多种转录方案

系统支持多种音频转录方案，避免依赖复杂的Whisper安装：

### 方案1: OpenAI Whisper API（推荐）
```python
# 在 config.py 中配置
TRANSCRIPTION_MODE = "openai_api"
OPENAI_API_KEY = "你的API key"
```
**优点**: 无需本地安装，准确率高  
**安装**: `pip install openai`

### 方案2: faster-whisper（本地轻量版）
```python
TRANSCRIPTION_MODE = "faster_whisper"
```
**优点**: 本地运行，速度快，内存占用小  
**安装**: `pip install faster-whisper`

### 方案3: whisper.cpp（纯CPU）
```python
TRANSCRIPTION_MODE = "whisper_cpp"
```
**优点**: 纯CPU运行，无需GPU，跨平台  
**安装**: 需要编译，参考 https://github.com/ggerganov/whisper.cpp

### 方案4: 简化模式（默认）
```python
TRANSCRIPTION_MODE = "simplified"
```
**优点**: 无需任何依赖，快速验证系统  
**功能**: 仅下载和保存音频信息，不实际转录

## 📥 音频下载功能

系统现在支持真正的音频下载功能：

### 功能特性
- ✅ **真实下载**: 使用 requests 库下载音频文件
- ✅ **多格式支持**: MP3, M4A, WAV, OGG, FLAC, AAC 等
- ✅ **进度显示**: 下载时显示进度和速度
- ✅ **错误处理**: 完善的错误处理和重试机制
- ✅ **文件管理**: 自动清理旧文件

### 配置选项
```python
# 下载超时时间（秒）
DOWNLOAD_TIMEOUT = 30

# 最大重试次数
DOWNLOAD_MAX_RETRIES = 3

# 临时文件保留时间（小时）
TEMP_FILE_MAX_AGE_HOURS = 24
```

### 使用命令
```bash
# 清理临时文件
python podcast_processor.py cleanup --age 24

# 模拟清理（不实际删除）
python podcast_processor.py cleanup --dry-run
```

## 📁 项目结构

```
podcast-ai-system/
├── podcast_processor.py     # 主处理脚本
├── config.py                # 配置文件
├── transcription.py         # 多方案转录模块
├── audio_downloader.py      # 音频下载模块
├── setup.sh                 # 安装脚本
├── README.md                # 说明文档
├── NO_WHISPER_SOLUTIONS.md  # 非Whisper方案指南
├── .gitignore               # Git忽略文件
├── apple_podcast_auto.py    # 苹果播客专用处理
├── simple_podcast_processor.py  # 简单处理脚本
├── test_audio_download.py   # 音频下载测试
├── test_transcription.py    # 转录功能测试
├── version.py               # 版本管理
└── templates/               # Markdown模板
```

## ⚙️ 配置说明

### 核心配置（config.py）
```python
# Obsidian知识库路径
OBSIDIAN_VAULT = "/Volumes/MxStore/Project/YearsAlso"

# 播客笔记保存目录
PODCASTS_DIR = os.path.join(OBSIDIAN_VAULT, "Podcasts")

# 转录配置
WHISPER_MODEL_SIZE = "base"  # base, small, medium, large
TRANSCRIPT_LANGUAGE = "zh"   # 转录语言
```

### 启用完整功能

1. **安装Whisper（音频转文字）**
   ```bash
   pip install openai-whisper
   brew install ffmpeg  # macOS
   ```

2. **配置OpenAI API（AI总结）**
   ```python
   # 在config.py中设置
   AI_SUMMARY_ENABLED = True
   OPENAI_API_KEY = "your-api-key-here"
   ```

3. **实现RSS解析**
   - 安装feedparser库
   - 实现真正的RSS解析逻辑

## 🔌 OpenClaw集成

### 简单集成
```python
# 在OpenClaw中直接调用
exec("cd ~/Project/podcast-ai-system && python podcast_processor.py process --name '得到' --test")
```

### 创建OpenClaw Skill
在OpenClaw的TOOLS.md中添加：
```markdown
### 🎙️ 播客处理
- 处理播客: `cd ~/Project/podcast-ai-system && python podcast_processor.py process --name`
- 添加订阅: `cd ~/Project/podcast-ai-system && python podcast_processor.py add --name --rss`
- 查看历史: `cd ~/Project/podcast-ai-system && python podcast_processor.py history`
```

## 📊 使用示例

### 添加真实播客
```bash
# 添加得到播客
python podcast_processor.py add --name "得到" --rss "https://rss.example.com/dedao"

# 添加疯投圈
python podcast_processor.py add --name "疯投圈" --rss "https://rss.example.com/fengtouquan"

# 列出所有订阅
python podcast_processor.py list
```

### 处理播客
```bash
# 处理最新一期（测试模式）
python podcast_processor.py process --name "得到" --test

# 查看处理历史
python podcast_processor.py history --limit 10
```

### 查看配置
```bash
python podcast_processor.py config
```

## 🛠️ 开发指南

### 项目架构
- **podcast_processor.py** - 主入口，命令行界面
- **config.py** - 集中式配置管理
- **数据库** - SQLite存储订阅和处理记录
- **模板系统** - Markdown笔记模板

### 扩展功能
要添加新功能：
1. 在 `config.py` 中添加配置项
2. 在 `podcast_processor.py` 中添加处理逻辑
3. 创建新的模块文件

### 数据库模式
```sql
-- 已处理播客
CREATE TABLE processed_podcasts (
    id INTEGER PRIMARY KEY,
    podcast_name TEXT,
    episode_title TEXT,
    episode_url TEXT UNIQUE,
    output_path TEXT,
    status TEXT
);

-- 播客订阅
CREATE TABLE podcast_subscriptions (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    rss_url TEXT,
    enabled BOOLEAN
);
```

## 📈 路线图

### 阶段1：核心框架 ✅
- [x] 系统框架搭建
- [x] 数据库设计
- [x] Obsidian集成
- [x] 命令行界面

### 阶段2：完整功能 🔄
- [ ] 音频转文字集成（Whisper）
- [ ] AI智能总结（GPT）
- [ ] RSS自动解析
- [ ] 音频下载功能

### 阶段3：高级功能 📅
- [ ] Web管理界面
- [ ] 多用户支持
- [ ] 智能推荐系统
- [ ] 知识图谱集成

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🚀 CI/CD 自动化

### GitHub Actions 工作流

项目包含完整的CI/CD管道：

1. **CI/CD Pipeline** (`ci-cd.yml`)
   - 代码质量检查（black, flake8）
   - 自动化测试（pytest）
   - Docker镜像构建和推送
   - 自动创建GitHub Release

2. **每日构建** (`daily-build.yml`)
   - 每天自动运行测试
   - 构建Docker镜像
   - 失败时发送通知

3. **自动版本管理** (`auto-tag.yml`)
   - 检测重大代码变更
   - 自动创建版本标签
   - 根据变更类型更新版本号

### Docker 镜像

```bash
# 拉取最新镜像
docker pull ghcr.io/yearsalso/podcast-ai-system:latest

# 运行容器
docker run -it --rm \
  -v $(pwd)/config.py:/app/config.py \
  ghcr.io/yearsalso/podcast-ai-system:latest \
  python podcast_processor.py --help
```

### 版本管理

```bash
# 查看当前版本
python version.py show

# 更新版本号
python version.py bump patch  # 或 minor, major

# 创建Git标签
python version.py tag --push
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

遇到问题？
1. 查看 [Issues](https://github.com/YearsAlso/podcast-ai-system/issues)
2. 检查日志文件：`logs/podcast_processor.log`
3. 运行配置测试：`python config.py`

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 音频转文字
- [OpenClaw](https://openclaw.ai/) - AI助手平台
- [Obsidian](https://obsidian.md/) - 知识管理工具

---

**开始使用：**
```bash
git clone https://github.com/YearsAlso/podcast-ai-system.git
cd podcast-ai-system
./setup.sh
python podcast_processor.py --help
```

访问仓库：https://github.com/YearsAlso/podcast-ai-system