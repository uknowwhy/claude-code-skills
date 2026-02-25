import sys
import re
import json
from pathlib import Path
from collections import Counter

class TermExtractor:
    """术语提取器"""

    def __init__(self):
        # 常见的技术术语模式
        self.patterns = {
            # 英文产品名/工具名（首字母大写或全大写）
            'product': re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b|[A-Z]{2,4})\b'),

            # 英文单词组合（可能的专有名词）
            'english_phrase': re.compile(r'\b([A-Z][a-z]+(?:\s+[a-z]+){0,3})\b'),

            # 含数字的版本号或代号
            'version': re.compile(r'\b([A-Za-z]+\d+|[A-Za-z0-9]*|\d+[A-Za-z0-9]*)\b'),

            # AI/技术相关词汇
            'tech_terms': re.compile(r'\b(AI|ML|API|SDK|CLI|GUI|UI|UX|MCP|LLM|GPT)\b', re.IGNORECASE),

            # 互联网常见品牌/产品
            'brands': re.compile(r'\b(Claude|Anthropic|OpenAI|Google|Apple|Microsoft|GitHub|GitLab)\b', re.IGNORECASE),

            # 中文常见的缩写或品牌名（从测试文本中总结）
            'cn_brands': re.compile(r'\b(智谱|Claude|Claude Code|Claude Skills|Agent Skills|Anthropic|OpenAI|CodeX|OpenCode|Typeless|create skill|skill-creator)\b', re.IGNORECASE),
        }

        # 已知的常见术语（可扩展）
        self.known_terms = {
            'Claude Code', 'Claude Skills', 'Anthropic', 'OpenAI',
            'AI agent', 'MCP', 'LLM', 'API', 'SDK', 'CLI',
            'Google', 'Typeless', 'create skill', 'skill-creator'
        }

        # 排除的常见词
        self.exclude_words = {
            'The', 'This', 'That', 'These', 'Those', 'Here', 'There',
            'Now', 'Then', 'When', 'Where', 'What', 'Which', 'Who',
            'And', 'But', 'Or', 'Nor', 'For', 'Yet', 'So',
            'In', 'On', 'At', 'To', 'From', 'By', 'With', 'Of',
            'Is', 'Are', 'Was', 'Were', 'Be', 'Been', 'Being',
            'Have', 'Has', 'Had', 'Do', 'Does', 'Did', 'Will', 'Would',
            'Could', 'Should', 'May', 'Might', 'Must', 'Need', 'OK', 'Yes', 'No', 'Not'
        }

    def extract(self, text):
        """
        从文本中提取术语

        Args:
            text: 逐字稿文本

        Returns:
            dict: {term: {'count': int, 'contexts': [str]}}
        """
        terms = {}

        # 按行处理，保留上下文
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            # 提取各种模式的术语
            for pattern_name, pattern in self.patterns.items():
                matches = pattern.finditer(line)
                for match in matches:
                    term = match.group(1).strip()

                    # 标准化（首字母大写，其余小写，除非是缩写）
                    if len(term) > 1 and not term.isupper():
                        term = term.capitalize()

                    # 跳过排除词
                    if term in self.exclude_words:
                        continue

                    # 跳过单字母
                    if len(term) == 1:
                        continue

                    # 记录术语
                    if term not in terms:
                        terms[term] = {
                            'count': 0,
                            'contexts': [],
                            'first_line': line_num
                        }

                    terms[term]['count'] += 1

                    # 保存上下文（前后各50字符）
                    start = max(0, match.start() - 50)
                    end = min(len(line), match.end() + 50)
                    context = line[start:end].strip()
                    if context and context not in terms[term]['contexts']:
                        terms[term]['contexts'].append(context)

        # 按出现次数排序
        sorted_terms = dict(
            sorted(terms.items(), key=lambda x: x[1]['count'], reverse=True)
        )

        return sorted_terms

    def filter_by_frequency(self, terms, min_count=1):
        """过滤低频术语"""
        return {
            term: info for term, info in terms.items()
            if info['count'] >= min_count
        }

    def mark_known_terms(self, terms):
        """标记已知术语"""
        for term in terms:
            if term in self.known_terms:
                terms[term]['known'] = True
            else:
                terms[term]['known'] = False
        return terms


def main():
    """测试函数"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python term_extractor.py <transcript_file>")
        sys.exit(1)

    # 读取文件
    transcript_file = Path(sys.argv[1])
    if not transcript_file.exists():
        print(f"Error: File not found: {transcript_file}")
        sys.exit(1)

    text = transcript_file.read_text(encoding='utf-8')

    # 提取术语
    extractor = TermExtractor()
    terms = extractor.extract(text)
    terms = extractor.filter_by_frequency(terms, min_count=1)
    terms = extractor.mark_known_terms(terms)

    # 输出结果
    print(f"\n提取到 {len(terms)} 个术语：\n")
    print(f"{'术语':<30} {'次数':>6} {'状态':<10}")
    print("-" * 50)

    for term, info in terms.items():
        status = "✓ 已知" if info.get('known') else "? 待验证"
        print(f"{term:<30} {info['count']:>6} {status:<10}")
        if info['contexts']:
            print(f"  上下文: {info['contexts'][0][:80]}...")

    # 输出 JSON
    output_file = transcript_file.parent / f"{transcript_file.stem}_terms.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(terms, f, ensure_ascii=False, indent=2)

    print(f"\n术语已保存到: {output_file}")


if __name__ == '__main__':
    main()
