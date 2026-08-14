#!/usr/bin/env python3
"""
dsh-content-studio 主程序（命令行入口）

用法示例：
  python studio.py                       # 自动选题 + 写 1 篇
  python studio.py "指定选题"             # 指定选题写 1 篇
  python studio.py --count 5 --out ./articles   # 批量生产 5 篇
  python studio.py --rewrite ./draft.md --out ./rewritten.md   # 原创化改写
  python studio.py --niche "数码/科技"    # 指定选题领域
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pipeline import ContentPipeline, DeepSeekClient


def banner():
    print("=" * 56)
    print("  dsh-content-studio | DeepSeek 内容自动化流水线")
    print("=" * 56)


def cmd_generate(args) -> int:
    pipe = ContentPipeline()
    topics = [args.topic] if args.topic else pipe.generate_topics(args.niche, args.count)

    if not args.topic:
        print(f"\n[选题] 生成 {len(topics)} 个候选：")
        for i, t in enumerate(topics, 1):
            print(f"  {i}. {t}")

    if args.count and not args.topic:
        # 批量模式：每个候选写一篇
        selected = topics
    else:
        selected = [topics[0]]

    out_dir = Path(args.out) if args.out else Path(".")
    for idx, topic in enumerate(selected, 1):
        print(f"\n[写作 {idx}/{len(selected)}] {topic}")
        article = pipe.write_article(topic)
        path = pipe.save(article, out_dir, idx)
        print(f"  完成：{article['title']}")
        print(f"  已保存：{path}")
        if not args.quiet:
            print("-" * 56)
            print(pipe.to_markdown(article["title"], article["body"]))
            print("-" * 56)
    print(f"\n✅ 共生成 {len(selected)} 篇，输出目录：{out_dir.resolve()}")
    return 0


def cmd_rewrite(args) -> int:
    pipe = ContentPipeline()
    src = Path(args.rewrite)
    if not src.exists():
        print(f"错误：文件不存在 {src}", file=sys.stderr)
        return 1
    text = src.read_text(encoding="utf-8")
    print(f"[改写] {src.name} ({len(text)} 字符)...")
    result = pipe.rewrite_article(text)
    out_dir = Path(args.out) if args.out else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{src.stem}-rewritten.md"
    out_path.write_text(pipe.to_markdown(result["title"], result["body"]), encoding="utf-8")
    print(f"✅ 改写完成：{out_path.resolve()}")
    if not args.quiet:
        print("-" * 56)
        print(pipe.to_markdown(result["title"], result["body"]))
        print("-" * 56)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="studio.py",
        description="DeepSeek 中文自媒体内容自动化生产工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("topic", nargs="?", default=None, help="指定选题（缺省则自动选题）")
    parser.add_argument("--count", type=int, default=1, help="批量生成篇数（默认 1）")
    parser.add_argument("--niche", default="职场效率/AI工具/生活技巧", help="选题领域")
    parser.add_argument("--out", default=None, help="输出目录（默认当前目录）")
    parser.add_argument("--rewrite", default=None, help="对指定 Markdown 文件做原创化改写")
    parser.add_argument("--quiet", action="store_true", help="不打印全文，只输出保存路径")
    args = parser.parse_args()

    try:
        banner()
        if args.rewrite:
            return cmd_rewrite(args)
        return cmd_generate(args)
    except RuntimeError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\n已取消", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
