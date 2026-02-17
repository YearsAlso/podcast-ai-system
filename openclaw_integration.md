# 🔌 OpenClaw 集成指南

如何将播客处理系统集成到OpenClaw中。

## 🎯 集成目标

让OpenClaw能够：
1. 通过简单命令处理播客
2. 自动保存到Obsidian知识库
3. 提供状态反馈
4. 支持批量处理

## 📋 集成方案

### 方案一：直接命令调用（最简单）

在OpenClaw中直接执行Python脚本：

```python
# 单个播客处理
exec("cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 simple_podcast_processor.py --file '/path/to/audio.mp3' --podcast '播客名' --episode '期数标题'")

# 或使用URL
exec("cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 simple_podcast_processor.py --url 'https://example.com/podcast.mp3' --podcast '播客名' --episode '期数标题'")
```

### 方案二：创建OpenClaw Skill

创建专门的Skill，提供更好的用户体验：

```markdown
# SKILL.md - 播客处理技能

## 功能
- 处理单个播客音频
- 批量处理多个音频
- 查看处理历史
- 配置参数

## 命令
- `/podcast process [url|file]` - 处理播客
- `/podcast list` - 列出已处理的播客
- `/podcast config` - 配置参数
```

### 方案三：Webhook集成（高级）

创建HTTP接口，OpenClaw通过webhook调用：

```python
# webhook_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process-podcast', methods=['POST'])
def process_podcast():
    data = request.json
    # 调用处理脚本
    # 返回处理结果
    return jsonify({"status": "success"})
```

## 🔧 实际集成步骤

### 步骤1：安装依赖
```bash
cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统
./install_deps.sh
```

### 步骤2：测试脚本
```bash
# 测试帮助
python3 simple_podcast_processor.py --help

# 测试处理（使用示例音频）
python3 simple_podcast_processor.py \
  --file "/tmp/test_audio.mp3" \
  --podcast "测试播客" \
  --episode "第1期：测试"
```

### 步骤3：创建OpenClaw快捷方式

在OpenClaw的TOOLS.md中添加：

```markdown
### 🎙️ 播客处理命令

#### 基本命令
```bash
# 处理本地文件
podcast_process_local() {
  cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统
  python3 simple_podcast_processor.py --file "$1" --podcast "$2" --episode "$3"
}

# 处理在线URL
podcast_process_url() {
  cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统
  python3 simple_podcast_processor.py --url "$1" --podcast "$2" --episode "$3"
}
```

#### 使用示例
```bash
# 处理本地文件
podcast_process_local "/Users/username/audio.mp3" "科技播客" "第42期：AI未来"

# 处理在线音频
podcast_process_url "https://example.com/podcast.mp3" "商业播客" "第10期：创业心得"
```

### 步骤4：创建OpenClaw对话命令

在OpenClaw中，你可以创建这样的对话流程：

```python
# 当用户说"处理播客"时
if "处理播客" in user_message:
    # 询问播客信息
    ask_for_podcast_info()
    
    # 获取音频文件/URL
    audio_source = get_audio_source()
    
    # 执行处理
    result = exec(f"cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统 && python3 simple_podcast_processor.py --url '{audio_source}' --podcast '{podcast_name}' --episode '{episode_title}'")
    
    # 返回结果
    send_message(f"✅ 播客处理完成！文件已保存到Obsidian。\n📁 路径: {result['output_path']}")
```

## 🎨 用户体验优化

### 1. 进度反馈
```python
def process_with_feedback(audio_url, podcast_name, episode_title):
    """带进度反馈的处理函数"""
    
    # 开始处理
    send_message("🔄 开始处理播客...")
    
    # 下载中
    send_message("📥 下载音频文件中...")
    
    # 转文字中
    send_message("🎤 音频转文字中...（这可能需要几分钟）")
    
    # 保存文件
    send_message("💾 保存到Obsidian...")
    
    # 完成
    send_message("✅ 处理完成！")
```

### 2. 错误处理
```python
try:
    result = process_podcast(audio_url, podcast_name, episode_title)
    send_message(f"✅ 成功处理！\n📝 文件: {result['file']}\n📊 长度: {result['length']}字符")
except Exception as e:
    send_message(f"❌ 处理失败: {str(e)}\n💡 建议: 请检查音频格式和网络连接")
```

### 3. 批量处理
```python
def batch_process(podcast_list):
    """批量处理多个播客"""
    
    send_message(f"🔄 开始批量处理 {len(podcast_list)} 个播客...")
    
    results = []
    for i, podcast in enumerate(podcast_list):
        send_message(f"📋 处理第 {i+1}/{len(podcast_list)} 个: {podcast['name']}")
        
        try:
            result = process_podcast(podcast['url'], podcast['name'], podcast['episode'])
            results.append({"status": "success", **result})
        except Exception as e:
            results.append({"status": "error", "error": str(e)})
    
    # 生成报告
    success_count = sum(1 for r in results if r['status'] == 'success')
    send_message(f"📊 批量处理完成！\n✅ 成功: {success_count}\n❌ 失败: {len(results)-success_count}")
```

## 📊 监控和日志

### 日志文件
脚本会自动生成日志：
```
/tmp/podcast_processor.log
```

### 在OpenClaw中查看日志
```python
# 查看最新日志
exec("tail -20 /tmp/podcast_processor.log")

# 查看错误日志
exec("grep -i error /tmp/podcast_processor.log | tail -10")
```

## 🔄 自动化工作流

### 每日自动处理
通过OpenClaw的cron功能：

```python
# 每天上午9点自动检查并处理新播客
cron.add({
    "name": "每日播客处理",
    "schedule": {"kind": "cron", "expr": "0 9 * * *"},
    "payload": {
        "kind": "agentTurn",
        "message": "检查并处理新的播客订阅"
    }
})
```

### RSS订阅自动抓取
```python
def check_rss_feeds():
    """检查RSS订阅是否有新播客"""
    
    feeds = [
        "https://example.com/podcast1/rss",
        "https://example.com/podcast2/rss"
    ]
    
    new_episodes = []
    for feed in feeds:
        # 解析RSS，获取新期数
        episodes = parse_rss(feed)
        new_episodes.extend(episodes)
    
    # 自动处理新播客
    for episode in new_episodes:
        process_podcast(episode['url'], episode['podcast'], episode['title'])
```

## 🚀 快速开始模板

### OpenClaw命令模板
```markdown
### 快速处理播客

1. **准备音频**：获取音频文件或URL
2. **执行命令**：
   ```bash
   cd /Volumes/MxStore/Project/YearsAlso/系统方案/播客处理系统
   python3 simple_podcast_processor.py --url "音频链接" --podcast "播客名称" --episode "期数标题"
   ```
3. **查看结果**：在Obsidian的Podcasts目录查看

### 常用命令
- `podcast help` - 查看帮助
- `podcast test` - 测试功能
- `podcast list` - 列出已处理的播客
```

## 📞 支持

遇到问题？
1. 查看日志：`/tmp/podcast_processor.log`
2. 检查依赖：`./install_deps.sh`
3. 提交Issue：在项目仓库中

---

**开始集成吧！** 从最简单的exec调用开始，逐步添加更多功能。