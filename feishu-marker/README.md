# 飞书妙记视频剪辑标记工具

🎬 **自动为飞书妙记转录文稿添加删除标记，让视频粗剪效率提升 10 倍！**

## ✨ 功能特点

- 🟡 **黄色背景 + 删除线标记**：直观显示需要删除的口误、重复、口癖
- 📝 **灵活标记模式**：支持整段标记和精确片段标记
- 🤖 **AI 辅助规则**：基于专业校对经验总结的标记规则
- ⚡ **批量处理**：一次执行完成所有标记
- 🔒 **隐私友好**：基于飞书开放 API，无需第三方服务

## 🎯 适用场景

- 视频课程粗剪（删除口误、重复、口癖）
- 播客/访谈文稿整理
- 会议记录精简
- 任何需要基于飞书妙记进行文字编辑的场景

## 📦 安装

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/feishu-marker.git
cd feishu-marker

# 2. 安装依赖
pip install -r requirements.txt
```

## ⚙️ 配置

### 第一步：获取飞书应用凭证

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 为应用添加 **飞书文档** 权限（读取和编辑文档）

### 第二步：创建配置文件

复制示例配置文件：

```bash
cp config.json.example config.json
```

编辑 `config.json`，填入你的凭证：

```json
{
  "app_id": "cli_xxxxxxxxxxxxxxxx",
  "app_secret": "YOUR_APP_SECRET_HERE",
  "domain": "https://open.feishu.cn"
}
```

⚠️ **安全提示**：`config.json` 已在 `.gitignore` 中，不会被提交到 Git

## 🚀 使用

### 基本用法

```bash
python mark_feishu.py mark_plan.json
```

### 标记计划文件格式

`mark_plan.json` 示例：

```json
[
  {
    "block_id": "doxcnxxx",
    "mode": "full",
    "reason": "整段都是口误，需要删除"
  },
  {
    "block_id": "doxcnyyy",
    "mode": "segments",
    "segments": ["口误内容", "重复的片段"],
    "reason": "这些片段需要删除"
  }
]
```

### 如何获取 Block ID

1. 打开飞书妙记文档
2. 在浏览器中按 F12 打开开发者工具
3. 选中要标记的段落，查看元素属性中的 `data-block-id`
4. 或使用飞书 API 的 `GET /open-apis/docx/v1/documents/{doc_id}/blocks` 接口

## 📖 标记规则

详细规则请参考 [MARKING_RULES.md](MARKING_RULES.md)

### 核心规则

| 类型 | 规则 | 示例 |
|------|------|------|
| 口误修正 | 删第一遍，保留第二遍完整版 | "我们要一起用，我们要一起用好豆包" → 删第一遍 |
| 跨段落重复 | 检查段落首尾与相邻段落的重复 | 段尾"你会发现。" + 段首"来，让我们看一下...你发现" |
| 口癖删除 | 诶/哎/好/看/哇等非关键位置一律删 | "诶，好，" "哎，对了，" |
| 断句残片 | 句子说了一半就断的，整个删 | "那这个时候你其实就可以。" |

## 📁 项目结构

```
feishu-marker/
├── README.md              # 项目说明
├── mark_feishu.py         # 核心标记脚本
├── mark_plan.json         # 标记计划（示例）
├── MARKING_RULES.md       # 详细标记规则
├── requirements.txt       # Python 依赖
└── .gitignore            # Git 忽略文件
```

## 🔧 进阶用法

### 自动生成标记计划（TODO）

未来版本将支持：
- AI 自动分析口误和重复
- 基于规则的自动检测
- 交互式标记界面

### 自定义标记样式

修改 `mark_feishu.py` 中的样式配置：

```python
style["background_color"] = 3  # 3=黄色，其他颜色参考飞书 API 文档
style["strikethrough"] = True
```

## ⚠️ 注意事项

1. **API 限流**：飞书 API 有调用频率限制，脚本已内置延时
2. **文档权限**：确保应用有目标文档的编辑权限
3. **备份文档**：建议先复制文档再执行标记
4. **Token 过期**：飞书应用 token 会定期过期，需重新授权

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👤 作者

由 AI 课程主编开发，用于视频课程高效粗剪

---

**让视频剪辑像编辑文字一样简单！** ✂️
