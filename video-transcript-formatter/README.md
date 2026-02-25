# 视频逐字稿格式化工具 - 快速开始

## 一句话介绍

将带时间戳的视频逐字稿自动转换为格式规范、术语统一、可读性强的最终文稿。

## 适用场景

✅ 视频课程逐字稿整理
✅ 技术演讲/访谈记录
✅ 教学视频后期处理
✅ 需要生成术语词库的内容

## 快速使用 (3 步)

### 1. 准备逐字稿文件

将视频逐字稿保存为 `.txt` 文件，例如 `my_course_transcript.txt`

**支持的时间戳格式:**
```
[00:00:00] 大家好，我是...
[00:01:23] 今天我们要讲...
[02:15] 或者是这样的格式...
```

### 2. 运行处理器

```bash
python3 ~/.claude/skills/video-transcript-formatter/scripts/transcript_processor.py my_course_transcript.txt
```

### 3. 查看生成文件

处理完成后会生成 3 个文件:

1. **`my_course_transcript_normalized.txt`** - 最终文稿
   - ✅ 无时间戳
   - ✅ 术语拼写统一
   - ✅ 可直接使用

2. **`my_course_transcript_terms.txt`** - 术语词库
   - 逗号分隔: `Claude,Skill,Anthropic,AI...`
   - 可复制到后台系统

3. **`my_course_transcript_terms.json`** - JSON 数据
   - 包含术语频率、上下文等信息
   - 用于数据分析

## 实际效果

### 输入 (带时间戳)
```
[00:00:00] 大家好，我是王树义，今天咱们要来介绍如何制作文献综述 Claude Skill...
[00:00:30] 那么我们先来强调一下 Claude Skill 的实质...
```

### 输出 (最终文稿)
```
大家好，我是王树义，今天咱们要来介绍如何制作文献综述 Claude Skill...

那么我们先来强调一下 Claude Skill 的实质。它实际上是可以把你的经验反向灌输给 AI Agent...
```

### 术语词库
```
Claude,Skill,Anthropic,AI,Agent,Claude Code,Typeless
```

## 核心优势

✅ **0% WebSearch 消耗** - 首次验证后缓存，后续处理零成本
✅ **智能术语提取** - 自动识别专业术语（产品名、技术术语）
✅ **术语拼写统一** - 自动统一全文术语拼写
✅ **时间戳自动去除** - 清除所有时间戳格式
✅ **多格式输出** - JSON + 逗号分隔 + 最终文稿

## 测试案例

完整测试案例和详细文档请查看 [SKILL.md](./SKILL.md)

**测试结果:**
- 文本长度: 600 字
- 术语数量: 20 个
- 替换次数: 266 处
- 处理时间: <1 秒 (缓存命中后)
- WebSearch 消耗: 0% (使用缓存后)

## 常见问题

**Q: 如何清空缓存重新开始?**
```bash
rm ~/.claude/skills/video-transcript-formatter/term_cache.json
```

**Q: 如何添加自定义术语?**
编辑 `scripts/term_extractor.py` 中的 `known_terms` 集合

**Q: WebSearch 什么时候使用?**
仅在首次处理新领域术语时使用，后续直接用缓存，无需重复消耗配额

## 技术支持

- 详细文档: [SKILL.md](./SKILL.md)
- 脚本位置: `~/.claude/skills/video-transcript-formatter/scripts/`
- 缓存位置: `~/.claude/skills/video-transcript-formatter/term_cache.json`

---

**版本:** 1.0.0
**最后更新:** 2026-02-14
