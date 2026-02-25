#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐字稿清理工具 V3
保持段落结构，只修复明确的问题
"""

import re

class SemanticCleanerV3:
    def __init__(self):
        self.stats = {
            'fixed_issues': 0
        }

    def clean(self, text: str) -> str:
        """主清理流程"""
        print("🔄 开始 V3 清理...")

        # 按顺序处理，每一步都保持段落结构
        text = self._remove_speaker_labels(text)
        text = self._fix_specific_issues(text)
        text = self._unify_terms(text)
        text = self._fix_pronouns(text)
        text = self._clean_punctuation(text)
        text = self._optimize_format(text)

        return text

    def _remove_speaker_labels(self, text: str) -> str:
        """删除说话人标签，保持段落结构"""
        # 删除所有"说话人 X"
        text = re.sub(r'说话人\s+\d+\s*', '', text)
        # 删除说话人标签后的多余空格和空行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text

    def _fix_specific_issues(self, text: str) -> str:
        """修复具体问题"""
        fixes = [
            # 删除口误
            ('手里的半，手里的', '手里的'),
            ('首先我们打开豆包，首先我们打开豆包', '首先我们打开豆包'),
            ('单次简单操作。单次。单次操作简单', '单次操作简单'),
            ('如何用一个指令让 AI 帮你快速生成数编程系。如何用一个指令让 AI 快速帮你生成数据小游戏',
             '如何用一个指令让 AI 快速帮你生成数学小游戏'),

            # 修复被错误切断的句子
            ('点击预览之后你就会。\n\n发现，它这里出现了，', '点击预览之后你就会发现，它这里出现了，'),

            # 修复不完整的句子
            ('要有清晰的目标，达成规则一定要。', '要有清晰的目标和达成规则。'),
            ('接下来。就直接', '接下来直接'),
            ('首先。我们打开豆包', '首先我们打开豆包'),
            ('第一。是可视化元素', '第一，是可视化元素'),

            # 修复英文单词
            ('Dee p Seek', 'DeepSeek'),
            ('Dee pSee k', 'DeepSeek'),

            # 删除重复的"发现"开头
            ('发现，孩子看你的眼神变了', '孩子看你的眼神变了'),
        ]

        for old, new in fixes:
            if old in text:
                text = text.replace(old, new)
                self.stats['fixed_issues'] += 1

        return text

    def _unify_terms(self, text: str) -> str:
        """统一术语"""
        # 保留"及时反馈"还是"即时反馈"？根据上下文，教学中通常用"即时"
        # 但先不改，等用户确认

        # 统一代词（AI工具用"它"）
        return text

    def _fix_pronouns(self, text: str) -> str:
        """修复代词 - 指代工具/物品用'它'"""
        # 检查上下文，如果是指代AI/工具，用"它"
        pronoun_fixes = [
            ('他告诉我说', '它告诉我'),
            ('跟他说', '跟它说'),
            ('让他', '让它'),
            ('看他现在', '看它现在'),
            ('他已经生成完了', '它已经生成完了'),
            ('他已经生成完毕', '它已经生成完毕'),
        ]

        for old, new in pronoun_fixes:
            text = text.replace(old, new)

        return text

    def _clean_punctuation(self, text: str) -> str:
        """清理标点符号"""
        # 删除重复标点
        text = re.sub(r'。。', '。', text)
        text = re.sub(r'，，', '，', text)

        # 删除段落开头的空格
        paragraphs = text.split('\n\n')
        cleaned_paras = []

        for para in paragraphs:
            if para.strip():
                # 删除段落开头的空格
                lines = para.split('\n')
                lines = [line.lstrip() for line in lines if line.strip()]
                cleaned_paras.append('\n'.join(lines))

        return '\n\n'.join(cleaned_paras)

    def _optimize_format(self, text: str) -> str:
        """优化格式"""
        # 删除多余空行（保留段落间的单个空行）
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 删除首尾空行
        text = text.strip()

        return text


def main():
    import sys

    if len(sys.argv) < 3:
        print("用法: python3 semantic_clean_v3.py <输入文件> <输出文件>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    original_length = len(text)

    cleaner = SemanticCleanerV3()
    cleaned = cleaner.clean(text)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    print(f"\n✅ V3 清理完成！")
    print(f"   输出: {output_file}")
    print(f"   原文: {original_length} 字")
    print(f"   清理后: {len(cleaned)} 字")
    print(f"   修复: {cleaner.stats['fixed_issues']} 处")


if __name__ == '__main__':
    main()
