#!/usr/bin/env python3
"""
飞书妙记视频剪辑标记工具
========================

自动为飞书妙记转录文稿添加删除标记（黄色背景 + 删除线），
让视频粗剪效率提升 10 倍！

用法:
    python mark_feishu.py <mark_plan.json> --doc <doc_id>

示例:
    python mark_feishu.py mark_plan.json --doc PVl5wGZf1i7w5kkHCvjcUgkfn0f
"""

import requests
import json
import sys
import time
import argparse
from pathlib import Path

# ============== 配置区域 ==============
# ⚠️ 重要：请从配置文件读取凭证，不要直接在这里填写！
# 复制 config.json.example 为 config.json 并填入你的飞书应用凭证
APP_ID = ""
APP_SECRET = ""
FEISHU_DOMAIN = "https://open.feishu.cn"

# 从配置文件读取（推荐方式）
CONFIG_FILE = Path(__file__).parent / "config.json"
if CONFIG_FILE.exists():
    with open(CONFIG_FILE) as f:
        config = json.load(f)
        APP_ID = config.get("app_id", APP_ID)
        APP_SECRET = config.get("app_secret", APP_SECRET)
        FEISHU_DOMAIN = config.get("domain", FEISHU_DOMAIN)

# 验证配置
if not APP_ID or not APP_SECRET:
    raise RuntimeError(
        "❌ 未配置飞书应用凭证！\n"
        "请复制 config.json.example 为 config.json，并填入你的 APP_ID 和 APP_SECRET\n"
        "获取方式：https://open.feishu.cn/ 创建企业自建应用"
    )


# ============== 核心功能 ==============

def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = f"{FEISHU_DOMAIN}/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    })
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"获取 token 失败：{data}")
    return data["tenant_access_token"]


def get_document_blocks(token, doc_id):
    """获取文档所有 blocks"""
    url = f"{FEISHU_DOMAIN}/open-apis/docx/v1/documents/{doc_id}/blocks"
    headers = {"Authorization": f"Bearer {token}"}
    
    all_blocks = []
    page_token = None
    while True:
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"获取 blocks 失败：{data}")
        items = data.get("data", {}).get("items", [])
        all_blocks.extend(items)
        if not data.get("data", {}).get("has_more"):
            break
        page_token = data["data"]["page_token"]
    return all_blocks


def update_block_text_elements(token, doc_id, block_id, new_elements, revision_id=-1):
    """
    更新 block 的 text elements（精确控制每个 text_run 的样式）
    使用 PATCH /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}
    """
    url = f"{FEISHU_DOMAIN}/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"document_revision_id": revision_id}
    
    body = {
        "update_text_elements": {
            "elements": new_elements
        }
    }
    
    resp = requests.patch(url, headers=headers, json=body, params=params)
    data = resp.json()
    if data.get("code") != 0:
        print(f"  ⚠️ 更新 block {block_id} 失败：{data}")
        return False, data.get("data", {}).get("document_revision_id", revision_id)
    return True, data.get("data", {}).get("document_revision_id", revision_id)


def mark_entire_block_content(original_elements):
    """
    将 block 中所有正文内容（非说话人/时间戳部分）标记为黄色背景 + 删除线
    """
    new_elements = []
    for elem in original_elements:
        text_run = elem.get("text_run")
        if not text_run:
            new_elements.append(elem)
            continue
        
        content = text_run["content"]
        style = dict(text_run.get("text_element_style", {}))
        
        # 如果已经标记过，跳过
        if style.get("background_color"):
            new_elements.append(elem)
            continue
        
        # 保留说话人和时间戳的样式不变（text_color: 7 是灰色）
        if style.get("text_color") == 7:
            new_elements.append(elem)
            continue
        
        # 换行符保持原样
        if content == "\n":
            new_elements.append(elem)
            continue
        
        # 其余正文内容标记
        style["background_color"] = 3  # 黄色
        style["strikethrough"] = True
        new_elements.append({
            "text_run": {
                "content": content,
                "text_element_style": style
            }
        })
    
    return new_elements


def mark_text_segments_in_block(original_elements, segments_to_mark):
    """
    在 block 的正文内容中，精确标记指定的文本片段（黄色背景 + 删除线）
    其余部分保持不变
    
    segments_to_mark: list of str
    """
    new_elements = []
    
    for elem in original_elements:
        text_run = elem.get("text_run")
        if not text_run:
            new_elements.append(elem)
            continue
        
        content = text_run["content"]
        style = text_run.get("text_element_style", {})
        
        # 已标记 / 说话人时间戳 / 换行符 → 跳过
        if style.get("background_color") or style.get("text_color") == 7 or content == "\n":
            new_elements.append(elem)
            continue
        
        # 在正文中查找并拆分
        remaining = content
        result_parts = []
        
        while remaining:
            # 找最早出现的片段
            earliest_idx = len(remaining)
            earliest_seg = None
            for seg in segments_to_mark:
                idx = remaining.find(seg)
                if idx != -1 and idx < earliest_idx:
                    earliest_idx = idx
                    earliest_seg = seg
            
            if earliest_seg is None:
                result_parts.append(("normal", remaining))
                break
            
            if earliest_idx > 0:
                result_parts.append(("normal", remaining[:earliest_idx]))
            result_parts.append(("marked", earliest_seg))
            remaining = remaining[earliest_idx + len(earliest_seg):]
        
        # 构建 elements
        for kind, text in result_parts:
            new_style = dict(style)
            if kind == "marked":
                new_style["background_color"] = 3
                new_style["strikethrough"] = True
            new_elements.append({
                "text_run": {
                    "content": text,
                    "text_element_style": new_style
                }
            })
    
    return new_elements


def apply_marks(doc_id, mark_plan, dry_run=False):
    """
    执行标记计划
    
    Args:
        doc_id: 飞书文档 ID
        mark_plan: list of dict, 每个 dict 包含:
            - block_id: str
            - mode: "full" | "segments"
            - segments: list of str (mode=segments 时需要)
            - reason: str (可选，标记原因)
        dry_run: 是否仅预览，不实际执行
    
    Returns:
        tuple: (success_count, fail_count)
    """
    print("🔑 获取 access token...")
    token = get_tenant_access_token()
    
    print(f"📄 读取文档 {doc_id} 的 blocks...")
    blocks = get_document_blocks(token, doc_id)
    block_map = {b["block_id"]: b for b in blocks}
    
    print(f"📝 共 {len(blocks)} 个 blocks，计划标记 {len(mark_plan)} 个")
    
    if dry_run:
        print("🔍 预览模式：不会实际修改文档\n")
        for item in mark_plan:
            block_id = item["block_id"]
            mode = item.get("mode", "full")
            reason = item.get("reason", "未说明原因")
            block = block_map.get(block_id)
            
            if not block:
                print(f"  ❌ block {block_id} 不存在")
                continue
            
            text_body = block.get("text")
            if not text_body:
                print(f"  ⏭️ block {block_id} 不是文本块")
                continue
            
            if mode == "full":
                print(f"  🟡 [整段标记] block {block_id[:15]}... - {reason}")
            else:
                segments = item.get("segments", [])
                print(f"  🟡 [片段标记] block {block_id[:15]}... - {len(segments)} 个片段 - {reason}")
                for seg in segments[:3]:  # 最多显示 3 个
                    print(f"      • \"{seg[:50]}{'...' if len(seg) > 50 else ''}\"")
                if len(segments) > 3:
                    print(f"      ... 还有 {len(segments) - 3} 个片段")
        return 0, 0
    
    print(f"🚀 开始执行标记...\n")
    
    success = 0
    fail = 0
    revision_id = -1
    
    for i, item in enumerate(mark_plan, 1):
        block_id = item["block_id"]
        mode = item.get("mode", "full")
        reason = item.get("reason", "")
        
        block = block_map.get(block_id)
        if not block:
            print(f"  ❌ [{i}/{len(mark_plan)}] block {block_id} 不存在")
            fail += 1
            continue
        
        text_body = block.get("text")
        if not text_body:
            print(f"  ⏭️ [{i}/{len(mark_plan)}] block {block_id} 不是文本块，跳过")
            continue
        
        original_elements = text_body.get("elements", [])
        
        if mode == "full":
            new_elements = mark_entire_block_content(original_elements)
            print(f"  ✏️ [{i}/{len(mark_plan)}] 整段标记 block {block_id[:15]}...")
        else:
            segments = item.get("segments", [])
            new_elements = mark_text_segments_in_block(original_elements, segments)
            print(f"  ✏️ [{i}/{len(mark_plan)}] 片段标记 block {block_id[:15]}... ({len(segments)} 个片段)")
        
        # 调用 API 更新
        ok, revision_id = update_block_text_elements(token, doc_id, block_id, new_elements, revision_id)
        if ok:
            success += 1
        else:
            fail += 1
        
        time.sleep(0.1)  # 避免限频
    
    print(f"\n{'='*50}")
    print(f"✅ 完成！成功 {success}，失败 {fail}")
    return success, fail


def create_config_template():
    """创建配置文件模板"""
    template = {
        "app_id": "你的 APP_ID",
        "app_secret": "你的 APP_SECRET",
        "domain": "https://open.feishu.cn"
    }
    config_path = Path(__file__).parent / "config.json.example"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    print(f"✅ 配置文件模板已创建：{config_path}")
    print("   请复制为 config.json 并填入你的飞书应用凭证")


# ============== 命令行入口 ==============

def main():
    parser = argparse.ArgumentParser(
        description="飞书妙记视频剪辑标记工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览模式（不实际修改）
  python mark_feishu.py mark_plan.json --doc PVl5wGZf1i7w5kkHCvjcUgkfn0f --dry-run
  
  # 执行标记
  python mark_feishu.py mark_plan.json --doc PVl5wGZf1i7w5kkHCvjcUgkfn0f
  
  # 创建配置文件模板
  python mark_feishu.py --init-config
        """
    )
    
    parser.add_argument("mark_plan", nargs="?", help="标记计划 JSON 文件路径")
    parser.add_argument("--doc", "-d", help="飞书文档 ID")
    parser.add_argument("--dry-run", "-n", action="store_true", help="预览模式，不实际修改文档")
    parser.add_argument("--init-config", action="store_true", help="创建配置文件模板")
    
    args = parser.parse_args()
    
    if args.init_config:
        create_config_template()
        return
    
    if not args.mark_plan or not args.doc:
        parser.print_help()
        print("\n❌ 错误：请提供标记计划文件和文档 ID")
        print("   使用 --help 查看用法")
        sys.exit(1)
    
    # 读取标记计划
    mark_plan_path = Path(args.mark_plan)
    if not mark_plan_path.exists():
        print(f"❌ 错误：文件不存在：{mark_plan_path}")
        sys.exit(1)
    
    with open(mark_plan_path, "r", encoding="utf-8") as f:
        mark_plan = json.load(f)
    
    # 执行标记
    apply_marks(args.doc, mark_plan, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
