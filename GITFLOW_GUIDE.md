# 🌿 Git Flow 使用指南

## 快速开始

### 初始化 Git Flow
```bash
# 克隆仓库
git clone https://github.com/YearsAlso/podcast-ai-system.git
cd podcast-ai-system

# 查看分支
git branch -a

# 切换到开发分支
git checkout develop
git pull origin develop
```

### 安装 Git Flow 工具（可选）
```bash
# macOS
brew install git-flow

# Ubuntu/Debian
sudo apt-get install git-flow

# Windows (Git Bash)
# Git Flow 已包含在 Git for Windows 中
```

## 常用工作流

### 1. 开始新功能开发
```bash
# 从 develop 分支开始
git checkout develop
git pull origin develop

# 创建功能分支
git checkout -b feature/your-feature-name develop

# 或者使用 git-flow（如果已安装）
git flow feature start your-feature-name
```

### 2. 开发过程中
```bash
# 添加更改
git add .

# 提交更改（使用规范提交消息）
git commit -m "feat: 添加RSS解析功能"

# 推送到远程
git push origin feature/your-feature-name
```

### 3. 完成功能开发
```bash
# 确保代码是最新的
git checkout develop
git pull origin develop
git checkout feature/your-feature-name
git rebase develop

# 运行测试
python -m pytest

# 检查代码格式
black --check .

# 推送到远程
git push origin feature/your-feature-name

# 创建 Pull Request 到 develop 分支
# 访问: https://github.com/YearsAlso/podcast-ai-system/pulls
```

### 4. Bug修复
```bash
# 创建修复分支
git checkout -b bugfix/issue-description develop

# 修复问题
# ... 编写代码 ...

# 提交修复
git add .
git commit -m "fix: 修复音频下载超时问题"

# 推送到远程并创建PR
git push origin bugfix/issue-description
```

## 提交消息规范

### 格式
```
类型(范围): 描述

详细说明（可选）

关闭 #问题编号（可选）
```

### 类型
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具
- `perf`: 性能优化
- `ci`: CI配置

### 示例
```bash
# 新功能
git commit -m "feat(rss): 添加Apple播客RSS解析"

# Bug修复
git commit -m "fix(download): 修复大文件下载内存泄漏"

# 文档更新
git commit -m "docs: 更新安装指南"

# 重构
git commit -m "refactor(config): 重构配置加载逻辑"
```

## 分支命名规范

### 功能分支
```
feature/简短描述
feature/rss-parser
feature/ai-summary
```

### 修复分支
```
bugfix/问题描述
bugfix/audio-download-error
bugfix/memory-leak-fix
```

### 发布分支
```
release/v版本号
release/v1.2.0
release/v2.0.0
```

### 热修复分支（生产环境紧急修复）
```
hotfix/紧急问题
hotfix/critical-security-fix
```

## Pull Request 指南

### 创建PR的步骤
1. **确保代码质量**
   - 通过所有测试
   - 代码格式正确
   - 没有语法错误

2. **编写清晰的PR描述**
   ```markdown
   ## 变更内容
   - 添加了RSS解析功能
   - 支持Apple播客格式
   - 添加了错误处理
   
   ## 测试方法
   1. 运行 `python test_rss_parser.py`
   2. 测试URL: https://example.com/podcast.rss
   
   ## 相关Issue
   关闭 #123
   ```

3. **请求代码审查**
   - 至少需要1人批准
   - 选择适当的审查者
   - 及时回应审查意见

### PR审查清单
- [ ] 代码符合项目规范
- [ ] 有适当的测试覆盖
- [ ] 文档已更新
- [ ] 没有引入安全漏洞
- [ ] 性能影响可接受

## 发布流程

### 准备发布
```bash
# 从 develop 创建发布分支
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0 develop

# 更新版本号
python version.py --bump minor

# 更新CHANGELOG
# 编辑 CHANGELOG.md

# 提交版本更新
git add VERSION CHANGELOG.md
git commit -m "chore: 准备发布 v1.2.0"
```

### 测试发布分支
```bash
# 运行完整测试
python -m pytest

# 构建Docker镜像
docker build -t podcast-ai-system:v1.2.0 .

# 测试Docker镜像
docker run --rm podcast-ai-system:v1.2.0 python --version
```

### 完成发布
```bash
# 合并到 main
git checkout main
git merge --no-ff release/v1.2.0

# 打标签
git tag -a v1.2.0 -m "Release v1.2.0"

# 推送到远程
git push origin main
git push origin v1.2.0

# 合并到 develop
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop

# 删除发布分支
git branch -d release/v1.2.0
```

## 环境配置

### 开发环境
```bash
# 创建 .env 文件（从模板复制）
cp .env.example .env

# 编辑 .env 文件
# 填入你的API密钥和配置

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python podcast_processor.py config
```

### 生产环境
```bash
# 使用环境变量而不是文件
export OPENAI_API_KEY="your-api-key"
export DEVELOPMENT_MODE="False"

# 或使用Docker
docker run -e OPENAI_API_KEY="your-api-key" podcast-ai-system:latest
```

## 故障排除

### 常见问题

#### 1. 合并冲突
```bash
# 同步上游分支
git fetch origin
git rebase origin/develop

# 解决冲突后继续
git add .
git rebase --continue
```

#### 2. CI测试失败
```bash
# 在本地运行测试
python -m pytest

# 检查代码格式
black --check --diff .

# 运行代码检查
flake8 .
```

#### 3. 无法推送到受保护分支
- 确保你创建的是Pull Request而不是直接推送
- 检查你是否有所需权限
- 联系仓库管理员

#### 4. 环境变量不生效
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 重新加载 .env 文件
source .env

# 或在Python中检查
python -c "import os; print('API Key:', os.environ.get('OPENAI_API_KEY', 'Not set'))"
```

## 工具推荐

### Git客户端
- **命令行**: 原生Git
- **GUI**: GitHub Desktop, GitKraken, Sourcetree
- **IDE集成**: VS Code, PyCharm, IntelliJ IDEA

### 代码质量
- **格式化**: Black
- **检查**: flake8, pylint
- **测试**: pytest, coverage

### CI/CD
- **GitHub Actions**: 已配置
- **Docker**: 容器化部署
- **Codecov**: 测试覆盖率

## 学习资源

- [Git Flow官方文档](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions文档](https://docs.github.com/en/actions)