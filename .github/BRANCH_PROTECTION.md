# 🌳 Git Flow 分支保护规则

## 分支结构

```
main (生产分支)
  ↑
develop (开发分支)
  ↑
feature/* (功能分支)
  ↑
bugfix/* (修复分支)
  ↑
release/* (发布分支)
```

## 分支保护规则

### 1. main 分支（生产分支）
- **保护级别**: 最高
- **推送权限**: 仅限仓库管理员
- **合并要求**:
  - 必须通过所有CI测试
  - 必须有代码审查（至少1人批准）
  - 必须从 `develop` 或 `release/*` 分支合并
  - 必须解决所有对话
- **状态检查要求**:
  - `test-production` 必须通过
  - `build-and-push` 必须通过
  - `security-scan` 必须通过
- **其他保护**:
  - 禁止强制推送
  - 禁止删除分支
  - 需要线性提交历史

### 2. develop 分支（开发分支）
- **保护级别**: 高
- **推送权限**: 核心贡献者
- **合并要求**:
  - 必须通过所有CI测试
  - 建议代码审查
  - 必须从 `feature/*` 或 `bugfix/*` 分支合并
- **状态检查要求**:
  - `test` 必须通过
  - `docker-build` 必须通过
  - `security-scan` 必须通过
- **其他保护**:
  - 禁止强制推送
  - 禁止删除分支

### 3. 功能分支（feature/*）
- **保护级别**: 中等
- **命名规范**: `feature/简短描述`（如 `feature/rss-parser`）
- **生命周期**:
  - 从 `develop` 分支创建
  - 开发完成后合并回 `develop`
  - 删除分支
- **要求**:
  - 必须通过基础CI测试
  - 建议添加单元测试

### 4. 修复分支（bugfix/*）
- **保护级别**: 中等
- **命名规范**: `bugfix/问题描述`（如 `bugfix/audio-download-error`）
- **生命周期**:
  - 从 `develop` 分支创建（针对开发问题）
  - 从 `main` 分支创建（针对生产问题）
  - 修复完成后合并回对应分支
  - 删除分支

### 5. 发布分支（release/*）
- **保护级别**: 高
- **命名规范**: `release/v版本号`（如 `release/v1.2.0`）
- **生命周期**:
  - 从 `develop` 分支创建
  - 仅进行bug修复和文档更新
  - 测试完成后合并到 `main` 和 `develop`
  - 删除分支

## 工作流程

### 新功能开发
1. 从 `develop` 创建功能分支：`git checkout -b feature/新功能 develop`
2. 在功能分支上开发
3. 提交更改：`git commit -m "feat: 添加新功能"`
4. 推送到远程：`git push origin feature/新功能`
5. 创建Pull Request到 `develop` 分支
6. 通过代码审查后合并
7. 删除功能分支

### Bug修复
1. 从 `develop` 创建修复分支：`git checkout -b bugfix/问题描述 develop`
2. 修复问题
3. 提交更改：`git commit -m "fix: 修复问题描述"`
4. 推送到远程：`git push origin bugfix/问题描述`
5. 创建Pull Request到 `develop` 分支
6. 通过代码审查后合并
7. 删除修复分支

### 发布流程
1. 从 `develop` 创建发布分支：`git checkout -b release/v1.2.0 develop`
2. 更新版本号：`python version.py --bump minor`
3. 更新CHANGELOG.md
4. 进行最终测试
5. 合并到 `main`：`git checkout main && git merge --no-ff release/v1.2.0`
6. 打标签：`git tag -a v1.2.0 -m "Release v1.2.0"`
7. 合并到 `develop`：`git checkout develop && git merge --no-ff release/v1.2.0`
8. 删除发布分支：`git branch -d release/v1.2.0`

## GitHub Actions 工作流

### 1. CI - Develop Branch
- **触发**: `develop` 分支的push和pull request
- **任务**:
  - 多版本Python测试（3.9-3.12）
  - 代码格式检查（Black）
  - 代码质量检查（flake8）
  - 测试覆盖率
  - Docker镜像构建
  - 安全扫描（Trivy）

### 2. CD - Main Branch
- **触发**: `main` 分支的push
- **任务**:
  - 生产环境测试（Python 3.12）
  - Docker镜像构建和推送
  - 创建GitHub Release

### 3. Daily Build
- **触发**: 每天UTC 00:00
- **任务**:
  - 在 `develop` 分支上运行完整测试
  - 确保日常构建稳定

### 4. Auto Tag
- **触发**: `main` 分支的关键文件更改
- **任务**:
  - 自动更新版本号
  - 创建Git标签

## 配置分支保护

### 在GitHub上配置：
1. 进入仓库 Settings → Branches
2. 点击 "Add branch protection rule"
3. 配置规则：
   - Branch name pattern: `main`
   - Require a pull request before merging: ✓
   - Require approvals: 1
   - Require status checks to pass: ✓
   - Require branches to be up to date before merging: ✓
   - Include administrators: ✓
   - Restrict who can push to matching branches: ✓

4. 重复步骤为 `develop` 分支配置（可适当放宽要求）

## 最佳实践

### 提交消息规范
- `feat:` 新功能
- `fix:` Bug修复
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具

### 分支管理
- 保持分支小而专注
- 及时删除已合并的分支
- 定期同步 `develop` 分支
- 使用rebase而不是merge保持整洁历史

### 代码审查
- 至少需要1人批准
- 关注代码质量和安全性
- 确保测试覆盖
- 检查API密钥等敏感信息

## 故障排除

### 问题：无法推送到受保护分支
**解决方案**:
1. 确保你有推送权限
2. 创建Pull Request而不是直接推送
3. 联系仓库管理员

### 问题：CI检查失败
**解决方案**:
1. 查看CI日志了解失败原因
2. 在本地运行测试：`python -m pytest`
3. 修复问题后重新推送

### 问题：合并冲突
**解决方案**:
1. 同步上游分支：`git pull origin develop`
2. 解决冲突
3. 重新提交：`git commit -m "解决合并冲突"`
4. 推送更新