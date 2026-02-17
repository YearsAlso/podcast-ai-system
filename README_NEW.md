# 🎙️ 播客处理系统

自动爬取苹果播客 → 转文字 → AI总结 → 保存到Obsidian

## 📁 项目结构

```
~/Project/podcast-ai-system/      # 项目代码
├── podcast_processor.py          # 主处理脚本
├── config.py                     # 配置文件
├── setup.sh                      # 安装脚本
├── README_NEW.md                 # 说明文档
├── podcasts.db                   # 数据库
└── logs/                         # 日志目录

/Volumes/MxStore/Project/YearsAlso/  # Obsidian知识库
└── Podcasts/                        # 生成的播客笔记
    └── [播客名称]/
        └── YYYY-MM-DD_[播客名称]_[期数标题].md
```

## 🚀 快速开始

### 1. 安装
```bash
cd ~/Project/podcast-ai-system
chmod +x setup.sh
./setup.sh
```

### 2. 测试系统
```bash
# 查看帮助
python3 podcast_processor.py --help

# 添加测试订阅
python3 podcast_processor.py add --name "测试播客" --rss "https://example.com/rss"

# 测试处理（创建示例笔记）
python3 podcast_processor.py process --name "测试播客" --test

# 查看配置
python3 podcast_processor.py config

# 查看处理历史
python3 podcast_processor.py history
```

### 3. 查看结果
处理完成后，在Obsidian中打开：
```
/Volumes/MxStore/Project/YearsAlso/Podcasts/测试播客/
```

## 🔧 功能说明

### ✅ 已实现
- [x] 系统框架
- [x] 数据库记录
- [x] Obsidian集成
- [x] 命令行界面
- [x] 订阅管理

### 🔄 待实现（需要配置）
- [ ] 音频转文字（需要Whisper）
- [ ] AI总结（需要OpenAI API）
- [ ] RSS解析（需要实现解析逻辑）
- [ ] 音频下载（需要实现下载功能）

## ⚙️ 配置说明

### 主要配置（config.py）
```python
# Obsidian知识库路径
OBSIDIAN_VAULT = "/Volumes/MxStore/Project/YearsAlso"

# 播客笔记目录
PODCASTS_DIR = os.path.join(OBSIDIAN_VAULT, "Podcasts")

# 转录配置
WHISPER_MODEL_SIZE = "base"  # base, small, medium, large
TRANSCRIPT_LANGUAGE = "zh"   # 转录语言
```

### 启用完整功能需要：
1. **安装Whisper**（音频转文字）：
   ```bash
   pip install openai-whisper
   brew install ffmpeg  # macOS
   ```

2. **配置OpenAI API**（AI总结）：
   ```python
   # 在config.py中设置
   AI_SUMMARY_ENABLED = True
   OPENAI_API_KEY = "your-api-key"
   ```

3. **实现RSS解析**：
   - 安装feedparser库
   - 实现真正的RSS解析逻辑

## 📋 使用示例

### 添加真实播客订阅
```bash
# 添加得到播客（需要真实RSS地址）
python3 podcast_processor.py add --name "得到" --rss "https://rss.example.com/dedao"

# 添加疯投圈
python3 podcast_processor.py add --name "疯投圈" --rss "https://rss.example.com/fengtouquan"
```

### 处理播客
```bash
# 处理最新一期
python3 podcast_processor.py process --name "得到"

# 处理并保存到Obsidian
# （需要先配置完整功能）
```

### 管理订阅
```bash
# 列出所有订阅
python3 podcast_processor.py list

# 查看处理历史
python3 podcast_processor.py history --limit 20
```

## 🔌 OpenClaw集成

### 简单集成
```python
# 在OpenClaw中执行
exec("cd ~/Project/podcast-ai-system && python3 podcast_processor.py process --name '得到' --test")
```

### 创建OpenClaw快捷命令
在OpenClaw的TOOLS.md中添加：
```markdown
### 🎙️ 播客处理
- 处理播客: `cd ~/Project/podcast-ai-system && python3 podcast_processor.py process --name`
- 添加订阅: `cd ~/Project/podcast-ai-system && python3 podcast_processor.py add --name --rss`
- 查看历史: `cd ~/Project/podcast-ai-system && python3 podcast_processor.py history`
```

## 🛠️ 开发说明

### 项目结构
- `podcast_processor.py` - 主入口，命令行界面
- `config.py` - 配置文件
- `apple_podcast_auto.py` - 苹果播客专用处理（旧版本）
- `simple_podcast_processor.py` - 简单处理脚本（旧版本）

### 扩展功能
要添加新功能，可以修改：
1. `config.py` - 添加配置项
2. `podcast_processor.py` - 添加处理逻辑
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

## 🐛 故障排除

### 常见问题
1. **Obsidian目录不存在**
   ```
   修改config.py中的OBSIDIAN_VAULT路径
   ```

2. **Python依赖安装失败**
   ```
   使用虚拟环境：python3 -m venv venv && source venv/bin/activate
   ```

3. **权限问题**
   ```
   chmod +x ~/Project/podcast-ai-system/*.py
   ```

### 测试命令
```bash
# 测试Python环境
python3 -c "import sys; print(f'Python {sys.version}')"

# 测试配置
python3 config.py

# 测试主脚本
python3 podcast_processor.py --help
```

## 📈 路线图

### 阶段1：框架完成（当前）
- ✅ 系统框架
- ✅ 数据库设计
- ✅ Obsidian集成
- ✅ 命令行界面

### 阶段2：核心功能（下一步）
- [ ] 音频转文字集成
- [ ] AI总结功能
- [ ] RSS解析实现
- [ ] 音频下载功能

### 阶段3：高级功能（未来）
- [ ] Web管理界面
- [ ] 多用户支持
- [ ] 智能推荐
- [ ] 知识图谱

## 📞 支持

遇到问题？
1. 查看日志：`~/Project/podcast-ai-system/logs/`
2. 检查配置：`python3 config.py`
3. 运行测试：`python3 podcast_processor.py --help`

---

**开始使用：**
```bash
cd ~/Project/podcast-ai-system
./setup.sh
python3 podcast_processor.py --help
```