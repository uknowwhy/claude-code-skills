#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐字稿深度润色工具 V2
基于规则模板进行精确替换，保留自然口语感
"""

import re

class TranscriptRefiner:
    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self):
        """加载替换规则"""
        return {
            # 一、冗余套话类（精确替换）
            'redundant_phrases': [
                ('我们打一个比方', '打个比方'),
                ('你好比说', '比如'),
                ('好比说', '比如'),
                ('这一类', '这类'),
                ('这一系列', '一系列'),
                ('这样一个', '这个'),
                ('这样一种', '这种'),
            ],

            # 二、重复的"说"
            'redundant_say': [
                ('说这个', ''),
                ('说你', ''),
                ('说是一个', '是'),
                ('说是', '是'),
                ('说有一个', '有'),
            ],

            # 三、连续重复
            'duplicates': [
                (r'这{2,}', '这'),
                (r'那{2,}', '那'),
                (r'个{2,}', '个'),
                ('等等等等', '等等'),
            ],

            # 四、冗余代词和助词
            'redundant_pronouns': [
                ('给你', ''),  # 动词前
                ('给我', ''),  # 动词前
                ('一个劲的', ''),
                ('这样子', '这样'),
                ('这样的话', '这样'),
                ('什么的', ''),
            ],

            # 五、冗余动词
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

            # 六、特殊修正
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

            # 七、标点符号
            'punctuation': [
                ('。。', '。'),
                ('，，', '，'),
                ('.，', '。'),  # 中文内容用中文标点
                ('!,' , '！，'),
                ('?.', '？。'),
                (',，', '，'),
            ],

            # 八、专业术语格式
            'tech_terms': [
                ('USB c', 'USB-C'),
                ('Git Hub', 'GitHub'),
                ('git hub', 'GitHub'),
            ],

            # 九、语序调整 - 啰嗦语气
            'wordy_tone': [
                ('非常的清晰', '非常清晰'),
                ('非常的麻烦', '非常麻烦'),
                ('非常的满意', '非常满意'),
                ('非常的高兴', '非常高兴'),
                ('非常的重要', '非常重要'),
                ('非常的有意思', '非常有意思'),
            ],

            # 十、语序调整 - 冗余表达
            'wordy_expressions': [
                ('这个就是那个', '这就是'),
                ('就像你的那个', '就像'),
                ('这实际上是把', '这实际上是'),
                ('AI也是需要你给它这样的一些手把手的传授', 'AI也需要手把手的传授'),
            ],
        }

    def refine(self, text):
        """润色文本"""
        # 按规则顺序处理
        for category, rules in self.rules.items():
            if category == 'duplicates' or category == 'tech_terms':
                for pattern, replacement in rules:
                    text = re.sub(pattern, replacement, text)
            else:
                for pattern, replacement in rules:
                    text = text.replace(pattern, replacement)

        # 清理多余空格
        text = re.sub(r'  +', ' ', text)
        text = re.sub(r' \n', '\n', text)
        text = re.sub(r'\n +', '\n', text)

        return text

def main():
    # 读取文件
    input_file = '/Users/shier/transcript_20250202_final_v3.txt'
    output_file = '/Users/shier/transcript_20250202_refined_v2.txt'

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按段落分割处理
    paragraphs = content.split('\n\n')
    refiner = TranscriptRefiner()

    refined_paragraphs = []
    for i, para in enumerate(paragraphs, 1):
        if para.strip():
            refined_para = refiner.refine(para)
            refined_paragraphs.append(refined_para)
            print(f"处理段落 {i}/{len(paragraphs)}")

    # 写入文件
    output = '\n\n'.join(refined_paragraphs)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"\n处理完成！")
    print(f"共处理 {len(refined_paragraphs)} 个段落")
    print(f"输出文件: {output_file}")
    print(f"\n规则版本: V2（已补充标点、术语、语序规则）")

if __name__ == '__main__':
    main()
