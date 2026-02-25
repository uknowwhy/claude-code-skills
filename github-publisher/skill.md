---
name: github-publisher
description: GitHub 项目发布助手 - 自动化项目初始化、代码提交、推送到 GitHub 的完整流程
---

# GitHub 项目发布助手

## 概述

自动化将本地项目发布到 GitHub 的完整流程，包括项目结构初始化、Git 仓库配置、代码提交、远程推送和后续优化。

**核心功能：**
- ✅ 项目结构初始化（.gitignore、LICENSE、README）
- ✅ Git 仓库配置和提交
- ✅ 推送到 GitHub
- ✅ 创建 Release
- ✅ 添加主题标签
- ✅ 项目优化建议

**使用场景：**
- 首次发布项目到 GitHub
- 快速搭建开源项目结构
- 规范化 Git 提交流程
- 自动化 GitHub 仓库创建

---

## 快速开始

### 前置要求

1. **GitHub 账号**
   - 访问 https://github.com 注册（免费）

2. **Personal Access Token**
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - Note: 填写用途（如 `github-publisher`）
   - Expiration: 选择过期时间
   - ☑️ 勾选 `repo` 权限
   - 点击 "Generate token"
   - ⚠️ **立即复制 Token**（只显示一次）

3. **本地项目**
   - 项目文件已准备好
   - 知道项目所在路径

---

## 使用方法

### 方式1：直接运行（推荐）

```
请帮我把当前项目发布到 GitHub
```

### 方式2：指定项目路径

```
帮我把 ~/my-project 发布到 GitHub
```

### 方式3：完整流程

```
我想发布一个 Python 项目，名称是 my-tool，描述是自动化工具，目标用户是开发者
```

---

## 执行流程

### 步骤1：收集信息

会询问以下信息（如有默认值可直接回车）：

| 信息 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| 项目路径 | 项目所在目录 | 当前目录 | 否 |
| GitHub 用户名 | 你的 GitHub 用户名 | - | 是 |
| 仓库名称 | 项目在 GitHub 上的名字 | 当前目录名 | 是 |
| 项目描述 | 简短介绍项目 | 未提供 | 否 |
| 许可证 | 开源协议类型 | MIT | 否 |
| 可见性 | Public 或 Private | Public | 否 |

### 步骤2：初始化项目结构

创建以下文件：
- `.gitignore` - Git 忽略规则
- `LICENSE` - 开源许可证
- `README.md` - 项目说明（基于信息生成）

### 步骤3：配置 Git 仓库

```bash
git init
git add .
git commit -m "Initial commit"
```

### 步骤4：推送到 GitHub

**方式A：自动创建（推荐）**

如果安装了 `gh` CLI：
```bash
gh repo create --public --source=. --remote=origin --push
```

**方式B：手动创建**

1. 打开 https://github.com/new
2. 填写仓库名称和描述
3. 不要勾选任何自动创建选项
4. 点击 "Create repository"
5. 运行推送命令（会自动生成）

### 步骤5：后续优化（可选）

- 创建 Release（版本发布）
- 添加主题标签（Topics）
- 完善 About 信息

---

## 输出成果

### 生成文件

```
your-project/
├── .git/                 # Git 仓库
├── .gitignore            # Git 忽略规则
├── LICENSE               # MIT 许可证
├── README.md             # 项目说明
└── (你的项目文件)
```

### GitHub 仓库

```
https://github.com/YOUR_USERNAME/REPO_NAME
```

---

## 常见问题

### Q: 需要 `gh` CLI 吗？

**A:** 不是必须，但推荐。
- 有 `gh`: 可以自动创建仓库
- 无 `gh`: 会提供手动创建的指引

### Q: Personal Access Token 安全吗？

**A:** 安全。Token 比账户密码更安全：
- 可以随时撤销
- 可以设置过期时间
- 可以限制权限范围
- 不会暴露账户密码

### Q: 可以修改已推送的代码吗？

**A:** 可以。发布后可以继续：
```bash
git add .
git commit -m "Update files"
git push origin main
```

### Q: 如何删除仓库？

**A:** 在 GitHub 网页操作：
1. 进入仓库 Settings
2. 滚动到最底部
3. 点击 "Delete this repository"

### Q: Public 和 Private 的区别？

**A:**
- **Public**: 所有人可见，可以获得 Stars、Forks
- **Private**: 只有你可见，适合个人项目

---

## 项目类型模板

Skill 支持智能识别项目类型并生成对应的 README：

### Python 项目
```python
# 自动识别 requirements.txt、setup.py 等
README 包含安装说明、使用示例
```

### Web 项目
```html
<!-- 自动识别 index.html、package.json 等 -->
README 包含部署说明、技术栈
```

### 文档项目
```markdown
<!-- 自动识别 .md 文件 -->
README 侧重于内容导航
```

### 通用项目
```bash
# 兜底模板，适用所有项目
```

---

## Git 提交规范

遵循以下提交信息规范：

```
feat: 新功能
fix: 修复问题
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

**示例：**
```bash
git commit -m "feat: add user authentication"
git commit -m "fix: resolve login bug"
git commit -m "docs: update README"
```

---

## 最佳实践

### 1. 分支管理

```bash
# 主分支
git checkout -b main

# 功能分支
git checkout -b feature/new-feature

# 完成后合并
git checkout main
git merge feature/new-feature
```

### 2. 提交频率

- ✅ 经常提交，小步快跑
- ✅ 每个提交做一件事
- ❌ 不要一次提交太多改动

### 3. 分支策略

- `main` - 稳定版本
- `develop` - 开发版本
- `feature/*` - 功能分支
- `hotfix/*` - 紧急修复

---

## 示例对话

### 示例1：快速发布

```
用户：帮我把这个项目发布到 GitHub

Assistant：好的，我来帮你发布。

[询问 GitHub 用户名、仓库名称等信息]

[自动初始化 Git、创建文件、提交代码]

[提供推送命令或自动推送]

✅ 完成！你的项目已发布：https://github.com/uknowwhy/my-project
```

### 示例2：完整流程

```
用户：我想发布一个 Python 自动化工具

Assistant：明白，我来帮你。

[收集信息]
- GitHub 用户名？
- 仓库名称？
- 项目描述？
- 目标用户？

[生成专业 README]
[初始化 Git]
[创建 LICENSE 和 .gitignore]
[提交代码]

[推送指引]

✅ 发布成功！
```

### 示例3：已有 Git 仓库

```
用户：这个项目已经有 Git 了，能直接推送吗？

Assistant：可以。我会跳过初始化步骤，直接推送到 GitHub。

[询问远程仓库信息]

[提供推送命令]

✅ 推送完成！
```

---

## 故障排除

### 问题1：Permission denied

**原因：** Token 错误或过期

**解决：**
1. 检查 Token 是否正确
2. 重新生成 Token
3. 确认勾选了 `repo` 权限

### 问题2：repository not found

**原因：** 仓库名称错误或未创建

**解决：**
1. 检查仓库名称拼写
2. 确认已在 GitHub 网页创建仓库
3. 检查用户名是否正确

### 问题3：nothing to commit

**原因：** 没有文件改动

**解决：**
1. 确认有文件需要提交
2. 检查 `git status` 查看状态

### 问题4：remote already exists

**原因：** 已配置远程仓库

**解决：**
```bash
git remote remove origin
git remote add origin <正确的URL>
```

---

## 进阶功能

### 创建 Release

```
请为我的项目创建 v1.0.0 Release
```

### 添加主题标签

```
帮我添加主题标签：python, automation, cli
```

### 设置仓库信息

```
把仓库描述更新为：自动化工具，提升工作效率
```

---

## 注意事项

1. **Token 安全**
   - ⚠️ 不要在公开场合暴露 Token
   - ⚠️ 定期更新 Token
   - ✅ 使用最小权限原则

2. **提交规范**
   - ✅ 提交信息清晰明确
   - ✅ 遵循约定式提交
   - ❌ 不要提交敏感信息

3. **公开项目**
   - ⚠️ 检查是否有敏感信息
   - ⚠️ 确认没有大文件
   - ✅ 添加适当的许可证

4. **首次发布**
   - ✅ 检查 README 是否完整
   - ✅ 确认 .gitignore 配置正确
   - ✅ 验证 LICENSE 文件存在

---

## 相关资源

- **GitHub 文档**: https://docs.github.com
- **Git 教程**: https://git-scm.com/docs
- **开源许可**: https://choosealicense.com/
- **gh CLI**: https://cli.github.com/

---

## 版本历史

- v1.0.0 - 初始版本
  - 项目结构初始化
  - Git 仓库配置
  - 推送到 GitHub
  - 创建 Release
  - 添加主题标签

---

**让项目发布变得简单高效！** 🚀
