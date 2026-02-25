# Claude Code Skills Collection

私人Claude Code技能集合 - 提高日常工作效率的自定义skills

## 📦 包含的Skills

### 1. video-transcript-formatter V3
视频逐字稿智能整理工具 - 基于语义理解的智能分段与自动清理

**核心特性:**
- ✅ 智能语义分段 - 基于话题转换识别，每段80-100字
- ✅ 视觉呼吸原则 - 符合移动阅读习惯
- ✅ 口误智能识别 - 删除自我纠正、重复表达
- ✅ 语义完整性保护 - 不在句子中间切断

**适用场景:**
- 视频课程逐字稿整理
- 演讲/访谈/教学视频后期处理
- 播客/音频节目文字稿整理

**详细文档:** 见 `video-transcript-formatter/skill.md`

### 2. github-publisher
GitHub自动发布工具 - 一键初始化、提交、推送

**核心特性:**
- ✅ 自动初始化Git仓库
- ✅ 智能提交信息生成
- ✅ 一键推送到GitHub
- ✅ 仓库优化建议

**适用场景:**
- 快速发布项目到GitHub
- 批量管理多个仓库
- 自动化版本发布

## 🚀 快速开始

### 安装Skills

```bash
# 复制skill到你的Claude Code skills目录
cp -r video-transcript-formatter ~/.claude/skills/
cp -r github-publisher ~/.claude/skills/
```

### 使用video-transcript-formatter

```bash
# 处理逐字稿
cd ~/.claude/skills/video-transcript-formatter
python3 scripts/semantic_clean_v3.py input.txt cleaned.txt
python3 scripts/semantic_splitter.py cleaned.txt final.txt 80
```

### 使用github-publisher

在Claude Code中直接调用：
```
请帮我把这个项目发布到GitHub
```

## 📋 Skills列表

| Skill | 版本 | 最后更新 | 说明 |
|-------|------|----------|------|
| video-transcript-formatter | V3.0 | 2026-02-25 | 逐字稿智能分段+清理 |
| github-publisher | V1.0 | 2026-02-22 | GitHub自动发布 |

## 🛠️ 技术栈

- **Python 3.x** - 脚本语言
- **Regular Expressions** - 文本处理
- **Git** - 版本控制
- **GitHub API** - 仓库管理

## 📝 开发计划

- [ ] 添加更多实用skills
- [ ] 完善文档和示例
- [ ] 添加自动化测试
- [ ] 创建skill模板

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👤 作者

Created by Claude Code + 用户协作开发

---

**注意:** 这些skills是为私人使用场景设计的，可能需要根据你的具体需求进行调整。
