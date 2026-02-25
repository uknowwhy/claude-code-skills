#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能段落切分工具
基于语义、视觉呼吸、口语表达特点
"""

import re

class SemanticSplitter:
    def __init__(self, max_length=200, min_length=50):
        """
        max_length: 每段最大字数（建议150-200）
        min_length: 每段最小字数（避免过于破碎）
        """
        self.max_length = max_length
        self.min_length = min_length

        # 分段信号词
        self.split_signals = [
            # 强分段（必须分段）
            '还推荐一个',
            '更重要的是',
            '最后我想',
            '听完这节课',
            '好啦，',

            # 中等分段（优先考虑）
            '那首先',
            '那接下来',
            '接下来，',
            '然后，',
            '现在，',
            '这个时候，',
            '这个时候你',

            # 序列词
            '第一。',
            '第二',
            '第三',
            '第四',
            '第五',
            '最后',

            # 转折
            '但是，',
            '不过，',
            '然而，',
        ]

    def split(self, text: str) -> str:
        """智能分段"""
        # 先按现有段落分割
        original_paragraphs = text.split('\n\n')
        result_paragraphs = []

        for para in original_paragraphs:
            if not para.strip():
                continue

            # 如果段落太长，需要切分
            if len(para) > self.max_length:
                split_paras = self._split_long_paragraph(para)
                result_paragraphs.extend(split_paras)
            else:
                result_paragraphs.append(para.strip())

        return '\n\n'.join(result_paragraphs)

    def _split_long_paragraph(self, paragraph: str) -> list:
        """切分过长的段落"""
        sentences = self._split_sentences(paragraph)
        paragraphs = []
        current_para = []
        current_length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_length = len(sentence)

            # 检查是否是强分段信号
            is_strong_split = self._is_strong_split_signal(sentence)
            is_split_signal = self._is_split_signal(sentence)

            # 如果当前段落已满，且遇到分段信号，则分段
            if (current_length > self.min_length and
                (is_strong_split or (is_split_signal and current_length > self.min_length * 1.5))):

                paragraphs.append(''.join(current_para).strip())
                current_para = [sentence]
                current_length = sentence_length
            else:
                # 否则累加
                current_para.append(sentence)
                current_length += sentence_length

                # 如果超过最大长度，强制分段
                if current_length >= self.max_length:
                    # 尝试在句号处分段
                    if sentence.endswith('。'):
                        paragraphs.append(''.join(current_para).strip())
                        current_para = []
                        current_length = 0

        # 添加最后一段
        if current_para:
            paragraphs.append(''.join(current_para).strip())

        return paragraphs

    def _split_sentences(self, text: str) -> list:
        """按句号、问号、感叹号分割句子"""
        # 保护特殊标记
        text = text.replace('。', '。<SPLIT>')
        text = text.replace('？', '？<SPLIT>')
        text = text.replace('！', '！<SPLIT>')

        # 分割
        parts = text.split('<SPLIT>')

        # 去除空字符串
        sentences = [p.strip() for p in parts if p.strip()]

        return sentences

    def _is_strong_split_signal(self, sentence: str) -> bool:
        """检查是否是强分段信号"""
        strong_signals = [
            '还推荐一个',
            '更重要的是',
            '最后我想',
            '听完这节课',
            '好啦，',
        ]

        for signal in strong_signals:
            if sentence.startswith(signal):
                return True

        return False

    def _is_split_signal(self, sentence: str) -> bool:
        """检查是否是分段信号"""
        for signal in self.split_signals:
            if sentence.startswith(signal):
                return True

        return False


def main():
    import sys

    if len(sys.argv) < 3:
        print("用法: python3 semantic_splitter.py <输入文件> <输出文件> [最大字数]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    max_length = int(sys.argv[3]) if len(sys.argv) > 3 else 200

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # 执行分段
    splitter = SemanticSplitter(max_length=max_length)
    result = splitter.split(text)

    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)

    # 统计
    paragraphs = result.split('\n\n')
    avg_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0

    print(f"✅ 智能分段完成！")
    print(f"   输出: {output_file}")
    print(f"   总段数: {len(paragraphs)}")
    print(f"   平均段落长度: {avg_length:.0f} 字")
    print(f"   最大段落长度: {max((len(p) for p in paragraphs), default=0)} 字")


if __name__ == '__main__':
    main()
