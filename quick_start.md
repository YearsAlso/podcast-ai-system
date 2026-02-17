# 🚀 苹果播客自动处理系统 - 快速开始

## 目标
自动爬取苹果播客 → 下载音频 → 转文字 → AI总结 → 保存到Obsidian

## 第一步：解决依赖问题

由于Whisper安装有编译问题，我们先用简化版本：

```bash
# 1. 安装基础依赖
cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统

# 2. 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# 3. 安装轻量依赖
pip install requests feedparser

# 4. 尝试安装Whisper（如果失败，用简化版）
pip install openai-whisper || echo "Whisper安装失败，使用简化版"
```

## 第二步：测试简化版系统

```bash
# 测试苹果播客处理（模拟模式）
python3 apple_podcast_auto.py \
  --rss "https://podcasts.apple.com/cn/podcast/example/id123456789" \
  --name "测试播客" \
  --limit 2 \
  --test
```

## 第三步：实际处理一个播客

### 方法A：使用现有RSS地址
```bash
# 找一个你喜欢的苹果播客，复制RSS地址
# 例如：得到喜马拉雅
python3 apple_podcast_auto.py \
  --rss "https://rss.example.com/your-podcast.rss" \
  --name "得到" \
  --limit 1
```

### 方法B：手动提供音频URL
```bash
# 如果找不到RSS，直接处理单个音频
python3 simple_podcast_processor.py \
  --url "https://example.com/podcast-episode.mp3" \
  --podcast "播客名称" \
  --episode "期数标题"
```

## 第四步：OpenClaw集成

### 最简单集成：exec命令
```python
# 在OpenClaw中执行
exec("cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 apple_podcast_auto.py --rss '播客RSS地址' --name '播客名' --limit 1")
```

### 创建OpenClaw快捷命令
在OpenClaw的TOOLS.md中添加：
```markdown
### 🍎 苹果播客处理
- 处理最新一期: `process_apple_podcast RSS地址 "播客名"`
- 查看帮助: `podcast_help`
```

## 第五步：查看结果

处理完成后，在Obsidian中查看：
```
/Volumes/MxStore/Project/YearsAlso/Podcasts/
└── [播客名称]/
    └── YYYY-MM-DD_[播客名称]_[期数标题].md
```

## 当前状态说明

### ✅ 已完成
- [x] 系统框架搭建
- [x] 数据库记录
- [x] Obsidian集成
- [x] 模拟数据处理

### 🔄 待配置
- [ ] Whisper转文字（依赖问题）
- [ ] 实际音频下载
- [ ] AI总结（需要OpenAI API）
- [ ] 真正的RSS解析

### 🛠️ 临时解决方案

如果Whisper安装失败，可以：

1. **使用在线服务**：
   ```python
   # 使用OpenAI的Whisper API
   import openai
   audio_file = open("audio.mp3", "rb")
   transcript = openai.Audio.transcribe("whisper-1", audio_file)
   ```

2. **使用其他转文字服务**：
   - 阿里云语音识别
   - 腾讯云语音识别
   - Google Speech-to-Text

3. **手动转录**：
   - 先下载音频
   - 用其他工具转文字
   - 手动粘贴到系统中

## 下一步建议

### 短期（今天）
1. 测试简化版系统是否能运行
2. 处理一个测试播客
3. 在Obsidian中验证结果

### 中期（本周）
1. 解决Whisper依赖问题
2. 添加真正的音频下载
3. 配置AI总结功能

### 长期（本月）
1. 添加Web界面
2. 支持多个播客订阅
3. 定时自动处理

## 故障排除

### 常见问题

1. **Whisper安装失败**
   ```
   解决方案：使用Docker或在线API
   ```

2. **RSS地址找不到**
   ```
   解决方案：手动查找播客RSS，或使用播客平台API
   ```

3. **权限问题**
   ```
   解决方案：chmod +x *.py
   ```

### 测试命令
```bash
# 测试环境
python3 -c "import sys; print(f'Python: {sys.version}')"

# 测试脚本
python3 apple_podcast_auto.py --help

# 测试Obsidian目录
ls -la /Volumes/MxStore/Project/YearsAlso/Podcasts/
```

## 开始吧！

从最简单的测试开始：
```bash
cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统
python3 apple_podcast_auto.py --test --name "测试" --rss "test.rss"
```

如果测试成功，再尝试处理真实的播客。