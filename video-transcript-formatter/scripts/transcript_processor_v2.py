#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频逐字稿完整处理流程 V2
整合5步流程：基础清理→术语统一→段落分割→自动润色→人工精修指南
"""

import os
import sys
import json
import re
from pathlib import Path

class TranscriptProcessorV2:
    """逐字稿完整处理流程"""

    def __init__(self, input_file):
        self.input_file = Path(input_file)
        self.base_name = self.input_file.stem
        self.input_dir = self.input_file.parent

        # 加载规则
        self.refine_rules = self._load_refine_rules()

    def _load_refine_rules(self):
        """加载润色规则"""
        return {
            'redundant_phrases': [
                ('我们打一个比方', '打个比方'),
                ('你好比说', '比如'),
                ('好比说', '比如'),
                ('这一类', '这类'),
                ('这一系列', '一系列'),
                ('这样一个', '这个'),
                ('这样一种', '这种'),
            ],
            'redundant_say': [
                ('说这个', ''),
                ('说你', ''),
                ('说是一个', '是'),
                ('说是', '是'),
                ('说有一个', '有'),
            ],
            'duplicates': [
                (r'这{2,}', '这'),
                (r'那{2,}', '那'),
                (r'个{2,}', '个'),
                ('等等等等', '等等'),
            ],
            'redundant_pronouns': [
                ('给你', ''),
                ('给我', ''),
                ('一个劲的', ''),
                ('这样子', '这样'),
                ('这样的话', '这样'),
                ('什么的', ''),
            ],
            'redundant_verbs': [
                ('去执行', '执行'),
                ('去调用', '调用'),
                ('去做', '做'),
                ('来进行', '进行'),
                ('来调整', '调整'),
                ('来打开', '打开'),
                ('来安装', '安装'),
                ('来完成', '完成'),
                ('来使用', '使用'),
                ('来看', '看'),
                ('来讲', '讲'),
            ],
            'special_fixes': [
                ('那朋友', '朋友'),
                ('给他给看', '给他看'),
                ('这玩意', '这个'),
                ('那玩意', '那个'),
                ('我现在', '我'),
                ('这现在', '现在'),
                ('20242025', '2024、2025'),
                ('放在里', '放在里面'),
                ('这没有什么', '这没什么'),
                ('来打一个', '输入'),
                ('我把它利用', '我利用'),
            ],
            'punctuation': [
                ('。。', '。'),
                ('，，', '，'),
                ('.，', '。'),
                ('!,' , '！，'),
                ('?.', '？。'),
                (',，', '，'),
            ],
            'tech_terms': [
                ('USB c', 'USB-C'),
                ('Git Hub', 'GitHub'),
                ('git hub', 'GitHub'),
            ],
            'wordy_tone': [
                ('非常的清晰', '非常清晰'),
                ('非常的麻烦', '非常麻烦'),
                ('非常的满意', '非常满意'),
                ('非常的高兴', '非常高兴'),
                ('非常的重要', '非常重要'),
                ('非常的有意思', '非常有意思'),
            ],
            'wordy_expressions': [
                ('这个就是那个', '这就是'),
                ('就像你的那个', '就像'),
                ('这实际上是把', '这实际上是'),
                ('AI也是需要你给它这样的一些手把手的传授', 'AI也需要手把手的传授'),
            ],
        }

    def step1_clean_basic(self, text):
        """步骤1: 基础清理"""
        print("\n" + "="*60)
        print("步骤1: 基础清理")
        print("="*60)

        # 去除时间戳
        text = re.sub(r'\[\d{1,2}:\d{2}(:\d{2})?\]', '', text)
        text = re.sub(r'\d{1,2}:\d{2}(:\d{2})?', '', text)

        # 去除说话人标签
        text = re.sub(r'^[A-Za-z]+\s*\d*:\s*', '', text, flags=re.MULTILINE)

        # 去除双逗号
        text = text.replace('，，', '，')

        # 清理多余空行
        text = re.sub(r'\n\s*\n', '\n\n', text)

        output_file = self.input_dir / f"{self.base_name}_cleaned.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ 基础清理完成")
        print(f"   输出: {output_file}")
        return text

    def step2_unify_terms(self, text):
        """步骤2: 术语统一（简化版，使用内置规则）"""
        print("\n" + "="*60)
        print("步骤2: 术语统一")
        print("="*60)

        # 内置常见术语映射
        term_mappings = {
            'claude skill': 'Claude Skill',
            'claude code': 'Claude Code',
            'git hub': 'GitHub',
            'github': 'GitHub',
            'usb c': 'USB-C',
            'ai agent': 'AI Agent',
            'mcp': 'MCP',
        }

        count = 0
        for old, new in term_mappings.items():
            pattern = re.compile(r'\b' + re.escape(old) + r'\b', re.IGNORECASE)
            matches = pattern.findall(text)
            if matches:
                text = pattern.sub(new, text)
                count += len(matches)
                print(f"  ✓ {old:20} → {new:20} ({len(matches)} 处)")

        output_file = self.input_dir / f"{self.base_name}_normalized.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"\n✅ 术语统一完成")
        print(f"   共替换 {count} 处")
        print(f"   输出: {output_file}")
        return text

    def step3_split_paragraphs(self, text):
        """步骤3: 段落分割"""
        print("\n" + "="*60)
        print("步骤3: 段落分割")
        print("="*60)

        # 按句号、问号、感叹号分段
        sentences = re.split(r'([。！？])', text)

        # 重组句子（保留标点）
        rebuilt = []
        for i in range(0, len(sentences)-1, 2):
            if i+1 < len(sentences):
                sentence = sentences[i] + sentences[i+1]
                rebuilt.append(sentence.strip())

        # 按最多200字分段
        paragraphs = []
        current_para = ""
        current_length = 0

        for sentence in rebuilt:
            sentence_length = len(sentence)
            if current_length + sentence_length <= 200:
                current_para += sentence
                current_length += sentence_length
            else:
                if current_para:
                    paragraphs.append(current_para)
                current_para = sentence
                current_length = sentence_length

        if current_para:
            paragraphs.append(current_para)

        output_text = '\n\n'.join(paragraphs)

        output_file = self.input_dir / f"{self.base_name}_paragraphs.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)

        print(f"✅ 段落分割完成")
        print(f"   共分割为 {len(paragraphs)} 个段落")
        print(f"   输出: {output_file}")
        return output_text

    def step4_refine_auto(self, text):
        """步骤4: 自动润色"""
        print("\n" + "="*60)
        print("步骤4: 自动润色")
        print("="*60)

        # 应用所有规则
        for category, rules in self.refine_rules.items():
            if category in ['duplicates', 'tech_terms']:
                for pattern, replacement in rules:
                    text = re.sub(pattern, replacement, text)
            else:
                for pattern, replacement in rules:
                    text = text.replace(pattern, replacement)

        # 清理多余空格
        text = re.sub(r'  +', ' ', text)
        text = re.sub(r' \n', '\n', text)
        text = re.sub(r'\n +', '\n', text)

        output_file = self.input_dir / f"{self.base_name}_refined.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ 自动润色完成")
        print(f"   输出: {output_file} ⭐ 从这里开始人工精修")
        return text

    def step5_manual_guide(self):
        """步骤5: 人工精修指南"""
        print("\n" + "="*60)
        print("步骤5: 人工精修指南")
        print("="*60)

        guide = """
📋 人工精修指南

✅ 已完成的步骤:
   1. 基础清理 - 去除时间戳、元数据
   2. 术语统一 - 统一专业术语拼写
   3. 段落分割 - 建立合理段落结构
   4. 自动润色 - 删除冗余表达

🚧 现在需要人工处理:

高优先级（必须修正）:
   □ 断句错误 - 句子中间出现句号
   □ 漏词补全 - 缺少连接词
   □ 指代错误 - "它/他"混淆

中优先级（建议修正）:
   □ 语序调整 - 表达不自然
   □ 逻辑连接 - 添加连接词

📖 详细指南:
   请查看 MANUAL_FIXES_CHECKLIST.md

🎯 质量检查清单:
   □ 无明显断句错误
   □ 无"它/他"指代错误
   □ 行文流畅自然
   □ 保留讲师风格

📝 输出成品:
   人工精修后保存为: {name}_final.txt

💡 记住:
   - 不要追求100%自动化
   - 机器处理80%，人工处理20%
   - 每次都记录新问题
""".format(name=self.base_name)

        print(guide)

        # 保存指南到文件
        guide_file = self.input_dir / f"{self.base_name}_REFINEMENT_GUIDE.txt"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)

        print(f"\n💡 指南已保存到: {guide_file}")

    def process_full(self):
        """执行完整流程"""
        print("\n" + "="*60)
        print("视频逐字稿完整处理流程 V2.0")
        print("="*60)
        print(f"输入文件: {self.input_file}")
        print(f"文件大小: {self.input_file.stat().st_size / 1024:.1f} KB")

        # 读取原始文件
        with open(self.input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        print(f"\n📊 原始统计:")
        print(f"   字数: {len(text):,}")
        print(f"   行数: {text.count(chr(10)):,}")

        # 执行各步骤
        text = self.step1_clean_basic(text)
        text = self.step2_unify_terms(text)
        text = self.step3_split_paragraphs(text)
        text = self.step4_refine_auto(text)
        self.step5_manual_guide()

        # 最终总结
        print("\n" + "="*60)
        print("✅ 处理完成！")
        print("="*60)
        print(f"\n📁 生成的文件:")
        print(f"   1. {self.base_name}_cleaned.txt      - 基础清理版")
        print(f"   2. {self.base_name}_normalized.txt   - 术语统一版")
        print(f"   3. {self.base_name}_paragraphs.txt   - 段落分割版")
        print(f"   4. {self.base_name}_refined.txt      - 自动润色版 ⭐")
        print(f"   5. {self.base_name}_REFINEMENT_GUIDE.txt - 人工精修指南")

        print(f"\n🎯 下一步:")
        print(f"   打开 {self.base_name}_refined.txt")
        print(f"   参考 MANUAL_FIXES_CHECKLIST.md 进行人工精修")
        print(f"   保存最终成品为 {self.base_name}_final.txt")

        print(f"\n💡 需要帮助?")
        print(f"   查看 QUICK_REFERENCE.md - 快速参考")
        print(f"   查看 RULES_TEMPLATE.md   - 规则说明")
        print(f"   查看 MANUAL_FIXES_CHECKLIST.md - 问题分类")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 transcript_processor_v2.py <输入文件>")
        print("\n示例:")
        print("  python3 transcript_processor_v2.py my_transcript.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"❌ 错误: 文件不存在 - {input_file}")
        sys.exit(1)

    processor = TranscriptProcessorV2(input_file)
    processor.process_full()

if __name__ == '__main__':
    main()
