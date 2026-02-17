# 🔒 安全配置设置指南

## 概述

为了保护你的API密钥安全，系统提供了多种安全配置方式。请选择其中一种方式配置你的API密钥。

## 方案一：使用安全配置文件（推荐）

### 步骤
1. 复制配置模板：
   ```bash
   cp config_secrets_template.py config_secrets.py
   ```

2. 编辑配置文件：
   ```bash
   # 使用文本编辑器打开
   nano config_secrets.py
   # 或
   vim config_secrets.py
   # 或使用任何你喜欢的编辑器
   ```

3. 填入你的API密钥：
   ```python
   OPENAI_API_KEY = "sk-你的真实OpenAI API密钥"
   
   # 可选：添加测试播客
   TEST_PODCASTS = [
       {
           "name": "得到",
           "rss": "https://example.com/dedao.rss",
           "enabled": True
       }
   ]
   ```

### 安全性
- `config_secrets.py` 已添加到 `.gitignore`，不会上传到GitHub
- 文件只存储在本地
- 建议定期轮换API密钥

## 方案二：使用环境变量

### macOS/Linux
```bash
# 临时设置（当前终端会话）
export OPENAI_API_KEY="sk-你的真实OpenAI API密钥"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export OPENAI_API_KEY="sk-你的真实OpenAI API密钥"' >> ~/.zshrc
source ~/.zshrc
```

### Windows
```cmd
# 临时设置（当前命令行）
set OPENAI_API_KEY=sk-你的真实OpenAI API密钥

# 永久设置（系统环境变量）
# 1. 右键点击"此电脑" → "属性"
# 2. 点击"高级系统设置"
# 3. 点击"环境变量"
# 4. 在"用户变量"或"系统变量"中新建
```

## 方案三：使用 .env 文件（高级）

1. 创建 `.env` 文件：
   ```bash
   echo 'OPENAI_API_KEY="sk-你的真实OpenAI API密钥"' > .env
   ```

2. 系统会自动加载（需要python-dotenv库）：
   ```bash
   pip install python-dotenv
   ```

## 🔐 安全最佳实践

### 1. 密钥管理
- **不要**将API密钥硬编码在代码中
- **不要**将包含密钥的文件上传到GitHub
- **定期轮换**API密钥（每3-6个月）
- **使用不同密钥**用于不同环境（开发/测试/生产）

### 2. 权限控制
- 为API密钥设置使用限额
- 限制密钥的权限范围
- 监控API使用情况

### 3. 本地安全
- 确保配置文件权限为600：
  ```bash
  chmod 600 config_secrets.py
  ```
- 定期清理临时文件
- 使用全盘加密

## 🚨 如果密钥泄露怎么办

1. **立即撤销**泄露的密钥
2. **生成新密钥**替换旧密钥
3. **检查日志**查看是否有异常使用
4. **更新所有地方**使用新密钥

## 📋 配置验证

运行以下命令验证配置是否正确：

```bash
# 检查配置状态
python config.py

# 测试API密钥（如果已配置）
python -c "
import openai
openai.api_key = '你的密钥'
try:
    models = openai.Model.list()
    print('✅ OpenAI API 连接成功')
except Exception as e:
    print(f'❌ OpenAI API 连接失败: {e}')
"
```

## 🤝 开发协作建议

### 团队开发
1. 创建 `config_secrets.example.py` 作为模板
2. 每个开发者创建自己的 `config_secrets.py`
3. 在README中说明配置步骤

### CI/CD管道
1. 在CI系统中使用环境变量
2. 不要将真实密钥存储在代码仓库中
3. 使用密钥管理服务（如AWS Secrets Manager）

## 🆘 故障排除

### 问题：API密钥无效
- 检查密钥是否正确复制（注意前后空格）
- 确认账户是否有足够余额
- 检查密钥是否已启用

### 问题：配置文件未加载
- 确认文件名为 `config_secrets.py`（不是 `.py.txt`）
- 检查文件是否在项目根目录
- 确认Python有读取权限

### 问题：环境变量未生效
- 重启终端或IDE
- 检查变量名是否正确（大小写敏感）
- 确认在正确的终端会话中设置

---

**记住：安全第一！** 保护好你的API密钥就是保护你的账户和资金安全。