#!/usr/bin/env python3
"""
术语缓存管理器 - 管理术语验证结果的缓存
"""

import json
from pathlib import Path
from datetime import datetime

class TermCacheManager:
    """术语缓存管理器"""

    def __init__(self, cache_file=None):
        if cache_file is None:
            # 默认缓存位置
            cache_dir = Path.home() / '.claude' / 'skills' / 'video-transcript-formatter'
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / 'term_cache.json'

        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()

    def _load_cache(self):
        """加载缓存文件"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """保存缓存文件"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def get(self, term):
        """
        获取缓存的术语验证结果

        Returns:
            dict or None: {'verified': str, 'source': str, 'last_verified': str}
        """
        return self.cache.get(term)

    def set(self, term, verified, source='websearch', context=''):
        """
        添加或更新术语缓存

        Args:
            term: 原始术语
            verified: 验证后的正确拼写
            source: 验证来源（websearch/manual/known）
            context: 上下文说明
        """
        self.cache[term] = {
            'verified': verified,
            'source': source,
            'last_verified': datetime.now().strftime('%Y-%m-%d'),
            'context': context
        }
        self._save_cache()

    def batch_set(self, terms_dict):
        """
        批量添加术语

        Args:
            terms_dict: {term: {'verified': str, 'source': str, 'context': str}}
        """
        for term, info in terms_dict.items():
            self.cache[term] = {
                'verified': info.get('verified', term),
                'source': info.get('source', 'unknown'),
                'last_verified': datetime.now().strftime('%Y-%m-%d'),
                'context': info.get('context', '')
            }
        self._save_cache()

    def check_cached(self, terms):
        """
        检查哪些术语已缓存，哪些需要验证

        Args:
            terms: 术语列表

        Returns:
            tuple: (cached_terms, uncached_terms)
        """
        cached = {}
        uncached = {}

        for term in terms:
            if term in self.cache:
                cached[term] = self.cache[term]
            else:
                uncached[term] = {}

        return cached, uncached

    def get_stats(self):
        """获取缓存统计信息"""
        return {
            'total_terms': len(self.cache),
            'by_source': {
                source: sum(1 for t in self.cache.values() if t['source'] == source)
                for source in ['websearch', 'manual', 'known', 'unknown']
            }
        }

    def clear_old(self, days=30):
        """清除过期的缓存（可选）"""
        # 暂不实现，保留所有缓存
        pass


def main():
    """测试函数"""
    manager = TermCacheManager()

    # 添加一些测试术语
    test_terms = {
        'Claude Code': {
            'verified': 'Claude Code',
            'source': 'websearch',
            'context': "Anthropic's CLI tool"
        },
        'OpenCode': {
            'verified': 'OpenCode',
            'source': 'websearch',
            'context': 'Open source AI coding agent'
        }
    }

    manager.batch_set(test_terms)

    # 查看统计
    stats = manager.get_stats()
    print(f"缓存统计: {stats}")

    # 测试查询
    result = manager.get('Claude Code')
    print(f"\n查询 'Claude Code': {result}")


if __name__ == '__main__':
    main()
