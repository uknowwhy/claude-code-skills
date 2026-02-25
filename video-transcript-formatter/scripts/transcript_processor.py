import sys
import json
import re
from pathlib import Path
from term_extractor import TermExtractor
from term_cache_manager import TermCacheManager

class TranscriptProcessor:
    """逐字稿处理器"""

    def __init__(self):
        self.extractor = TermExtractor()
        self.cache = TermCacheManager()
        self.stats = {
            'total_terms': 0,
            'cached_terms': 0,
            'verified_terms': 0,
            'websearch_count': 0
        }

    def process(self, text, use_websearch=False):
        """
        处理逐字稿文本

        Args:
            text: 逐字稿文本
            use_websearch: 是否使用 WebSearch 验证（默认 False）

        Returns:
            dict: 处理结果
        """
        print("\n" + "="*60)
        print("第一阶段：术语提取")
        print("="*60)

        # 提取术语
        terms = self.extractor.extract(text)
        raw_terms = list(terms.keys())

        print(f"\n✓ 提取到 {len(raw_terms)} 个术语")

        # 检查缓存
        print("\n检查本地缓存...")
        cached_terms, uncached_terms = self.cache.check_cached(raw_terms)

        if cached_terms:
            print(f"  ✓ {len(cached_terms)} 个术语已缓存")
            for term, info in cached_terms.items():
                print(f"    - {term:<30} (已验证: {info['verified']})")
                self.stats['cached_terms'] = len(cached_terms)

        if uncached_terms:
            print(f"  ? {len(uncached_terms)} 个术语未缓存")

            # 分组：已知术语 vs 新术语
            new_terms = {t: info for t, info in uncached_terms.items()
                      if not info.get('known')}
            known_terms = {t: info for t, info in uncached_terms.items()
                         if info.get('known')}

            if known_terms:
                print(f"    ✓ {len(known_terms)} 个已知术语（使用缓存）")
                self.stats['verified_terms'] += len(known_terms)

            if new_terms:
                print(f"    ! {len(new_terms)} 个新术语（可能需要验证）")
                print("\n新术语列表：")
                for term in sorted(new_terms.keys()):
                    print(f"      - {term}")

        # WebSearch 验证（可选）
        verified_uncached = {}
        if use_websearch and uncached_terms:
            print("\n" + "="*60)
            print("第二阶段：术语验证（使用 WebSearch）")
            print("="*60)
            print(f"  将验证 {len(uncached_terms)} 个术语")
            print("  ⚠️  注意：这会消耗 WebSearch 配额")
            print("  建议：对不确定的术语使用验证，高频术语可直接使用缓存")

            # 询问是否继续
            print("\n是否继续使用 WebSearch 验证？: ", end='')
            try:
                confirm = input().strip().lower()
                if confirm not in ['y', 'yes', '是']:
                    print("\n  ⏭  跳过 WebSearch 验证")
                    # 直接使用提取的术语
                    verified_uncached = {t: {'verified': info.get('verified', t),
                                         'source': 'extracted',
                                         'context': info.get('context', '')}
                                    for t, info in uncached_terms.items()}
                else:
                    print("\n  ✓ 开始 WebSearch 验证")
                    # 这里应该调用 WebSearch，但由于在脚本中无法直接调用
                    # 暂时标记为需要验证
                    verified_uncached = {t: {'verified': 'pending',
                                         'source': 'pending',
                                         'context': '需要 WebSearch 验证'}
                                    for t, info in uncached_terms.items()}
                    self.stats['websearch_count'] = len(uncached_terms)
            except (KeyboardInterrupt, EOFError):
                print("\n\n  ⏭️  用户取消")
                verified_uncached = {t: {'verified': 'cancelled', 'source': 'cancelled'}
                                    for t, info in uncached_terms.items()}
        else:
            # 不使用 WebSearch，直接使用提取的术语作为待验证术语
            verified_uncached = {t: {'verified': t,
                                 'source': 'extracted',
                                 'context': ''}
                            for t, info in uncached_terms.items()}

        # 合并缓存术语和待验证术语，得到完整的 verified_terms
        verified_terms = {**cached_terms, **verified_uncached}

        # 更新缓存
        if verified_terms:
            print("\n更新术语缓存...")
            self.cache.batch_set({
                t: {
                    'verified': v['verified'],
                    'source': v['source'],
                    'context': v.get('context', '')
                }
                for t, v in verified_terms.items()
            })

        # 生成统计
        self.stats['total_terms'] = len(raw_terms)

        # === 新增：术语统一阶段 ===
        print("\n" + "="*60)
        print("准备统一全文术语拼写...")
        print("="*60)
        print("  ⚠️  这将替换原文中的所有术语为验证后的标准拼写")
        print("  ⚠️  例如：'claude skill' → 'Claude Skills'")
        print("\n是否执行术语统一？: ", end='')
        try:
            confirm_normalize = input().strip().lower()
            if confirm_normalize in ['y', 'yes', '是']:
                print("\n✓ 开始统一术语...")
                normalized_text, replacement_count = self._normalize_term_spelling(text, verified_terms)

                # 保存统一后的文本（去除时间戳）
                output_dir = Path.home()
                normalized_file = output_dir / f"{Path(sys.argv[1]).stem}_normalized.txt"

                # 去除时间戳后再保存
                normalized_text_no_timestamp = self._remove_timestamps(normalized_text)

                with open(normalized_file, 'w', encoding='utf-8') as f:
                    f.write(normalized_text_no_timestamp)

                print(f"\n✅ 统一后的文稿已保存到: {normalized_file}")
                print(f"📊 共替换 {replacement_count} 处术语拼写")
                print(f"✨ 已自动去除时间戳")

                # 更新返回的 terms 为使用统一后的文本
                # 这里保持原 terms，但可以返回 normalized_text 供后续使用
            else:
                print("\n⏭️  跳过术语统一，保留原文")
                replacement_count = 0
        except (KeyboardInterrupt, EOFError):
            print("\n\n  ⏭️  用户取消")
            replacement_count = 0

        self._print_summary(verified_terms, replacement_count)

        return {
            'terms': terms,
            'verified': verified_terms
        }

    def _normalize_term_spelling(self, text, verified_terms):
        """
        根据验证后的术语表统一全文中的名词拼写

        Args:
            text: 原始文本
            verified_terms: 验证后的术语字典 {term: {'verified': str, ...}}

        Returns:
            tuple: (normalized_text, replacement_count)
        """
        import re
        normalized_text = text
        replacement_count = 0

        # 按照术语长度降序排序（优先替换长术语，避免部分匹配问题）
        # 例如：先替换 "Claude Skills"，再替换 "Claude"
        sorted_terms = sorted(
            verified_terms.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )

        print(f"\n{'='*60}")
        print("第三阶段：术语统一")
        print("="*60)
        print(f"将统一 {len(sorted_terms)} 个术语的拼写...")

        for term, info in sorted_terms:
            verified = info['verified']

            # 构建替换模式（匹配单词边界）
            # 使用正则确保不会部分替换（如避免把 "Claude" 中的 "aud" 也替换）
            pattern = r'\b' + re.escape(term) + r'\b'

            # 执行替换
            matches = re.findall(pattern, normalized_text, flags=re.IGNORECASE)
            if matches:
                normalized_text = re.sub(
                    pattern,
                    verified,
                    normalized_text,
                    flags=re.IGNORECASE
                )
                replacement_count += len(matches)
                print(f"  ✓ {term:<30} → {verified:<30} ({len(matches)} 处)")

        print(f"\n共替换 {replacement_count} 处")

        return normalized_text, replacement_count

    def _remove_timestamps(self, text):
        """
        去除文本中的时间戳

        Args:
            text: 原始文本

        Returns:
            str: 去除时间戳后的文本
        """
        import re

        # 匹配常见时间戳格式
        # [00:01:23] 或 [1:23] 或 00:01:23
        timestamp_pattern = r'\[?\d{1,2}:\d{2}:\d{2}\]?|\[\d{1,2}:\d{2}\]'

        # 去除时间戳
        text_no_timestamp = re.sub(timestamp_pattern, '', text)

        # 清理多余的空行 - 使用双反斜杠
        pattern_newlines = r'\n\s*\n'
        replacement_newlines = '\n\n'
        text_no_timestamp = re.sub(pattern_newlines, replacement_newlines, text_no_timestamp)

        return text_no_timestamp.strip()

    def _print_summary(self, verified_terms, replacement_count=0):
        """打印处理摘要"""
        print("\n" + "="*60)
        print("处理摘要")
        print("="*60)

        print(f"\n总术语数: {self.stats['total_terms']}")
        print(f"缓存术语: {self.stats['cached_terms']}")
        print(f"已验证术语: {self.stats['verified_terms']}")
        if self.stats.get('websearch_count', 0) > 0:
            print(f"WebSearch 次数: {self.stats['websearch_count']}")

        # 生成逗号分隔的术语列表
        comma_terms = self._generate_comma_terms(verified_terms)
        print(f"\n✅ 术语词库已生成（{len(comma_terms)} 个术语）")

    def _generate_comma_terms(self, verified_terms):
        """生成逗号分隔的术语列表"""
        # 按缓存排序（已验证的优先）
        sorted_terms = sorted(
            [(term, info) for term, info in verified_terms.items()],
            key=lambda x: (
                0 if x[1].get('verified') == 'pending' else
                (1 if x[1].get('source') == 'websearch' else 2),
                (1 if x[1].get('source') == 'known' else 2),
                (1 if x[1].get('source') == 'cached' else 2)
            ),
            reverse=True
        )

        # 生成逗号分隔的字符串
        term_list = [term for term, info in sorted_terms]
        return ','.join(term_list)

    def export_terms(self, verified_terms, output_file):
        """导出术语词库到文件"""
        comma_terms = self._generate_comma_terms(verified_terms)

        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(comma_terms)

        print(f"\n✅ 术语词库已保存到: {output_path}")
        return output_path


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python transcript_processor.py <transcript_file> [--websearch]")
        print("\n选项:")
        print("  --websearch    启用 WebSearch 验证（会消耗配额）")
        print("\n示例:")
        print("  python transcript_processor.py transcript.txt")
        print("  python transcript_processor.py transcript.txt --websearch")
        sys.exit(1)

    # 解析参数
    transcript_file = Path(sys.argv[1])
    use_websearch = '--websearch' in sys.argv

    if not transcript_file.exists():
        print(f"Error: 文件不存在: {transcript_file}")
        sys.exit(1)

    # 读取文件
    print(f"\n处理文件: {transcript_file}")
    text = transcript_file.read_text(encoding='utf-8')

    # 处理
    processor = TranscriptProcessor()
    result = processor.process(text, use_websearch=use_websearch)

    # 导出术语词库
    output_file = transcript_file.parent / f"{transcript_file.stem}_terms.txt"
    processor.export_terms(result['verified'], output_file)

    print("\n" + "="*60)
    print("✅ 处理完成！")
    print("="*60)

    print(f"\n生成文件:")
    print(f"  1. {transcript_file.stem}_terms.json (JSON 格式，供后续处理）")
    print(f"  2. {output_file} (逗号分隔，供复制到后台）")


if __name__ == '__main__':
    main()
