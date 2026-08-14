#!/usr/bin/env python3
"""
ai-book-monetization - AI 拆书全域变现方案生成器（命令行入口）

用法示例：
  python monetize.py 书稿.txt                      # 分析书稿并输出完整变现方案
  python monetize.py 书稿.txt --isbn              # 标记为正规出版（带ISBN）
  python monetize.py 书稿.txt --no-copy           # 跳过宣传物料生成（省token）
  python monetize.py 书稿.txt --out 方案.md       # 输出到指定文件

流程：书稿定性 → 资产提取 → 变现矩阵 → 合规检查 → 定价交付 → 执行计划 → 宣传物料
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from engine import (
    BookAnalyzer,
    MarketingCopyGenerator,
    MonetizationPlanner,
)


def banner():
    print("=" * 60)
    print("  ai-book-monetization | AI 拆书全域变现方案生成器")
    print("  输入书稿 → 自动分类 → 变现矩阵 → 合规方案 → 宣传物料")
    print("=" * 60)


def load_book(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"错误：文件不存在 {path}")
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="gbk", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="monetize.py",
        description="AI 拆书全域变现方案生成器：输入书稿，输出整套分层落地方案",
        epilog="示例: python monetize.py 我的书稿.txt --isbn --out 方案.md",
    )
    parser.add_argument("book", help="书稿文件路径（.txt/.md 等文本格式）")
    parser.add_argument("--isbn", action="store_true",
                        help="标记为正规出版（带ISBN），启用图书零售双路线")
    parser.add_argument("--no-copy", action="store_true",
                        help="跳过宣传物料生成（节省API调用）")
    parser.add_argument("--out", default=None, help="输出方案到指定文件（默认打印到屏幕）")
    args = parser.parse_args()

    try:
        banner()
        text = load_book(args.book)
        print(f"\n[1/6] 读取书稿：{args.book}（{len(text)} 字符）")

        # 阶段1：书稿定性判定
        print("[2/6] 执行30秒自检清单，AI 判定书稿类型...")
        analyzer = BookAnalyzer()
        report = analyzer.classify(text)
        print(f"      → 判定结果：{report.type_name}"
              f"{'（次要：' + report.secondary_type + '）' if report.secondary_type else ''}"
              f" | 置信度：{report.confidence}")
        print(f"      核心资产：{len(report.assets)} 项")

        # 阶段2-4：变现方案 + 合规 + 风险
        print("[3/6] 匹配变现路径 + 合规边界检查...")
        planner = MonetizationPlanner()
        plan = planner.build_plan(report, has_isbn=args.isbn)
        compliance = plan["compliance"]
        print(f"      合规场景：{compliance['label']}")
        if compliance["red_lines"]:
            print("      🚨 红线条款已生成（无书号文稿禁止售卖PDF）")

        # 阶段5-6：定价 + 交付 + 执行
        print("[4/6] 生成定价阶梯 + 交付SOP + 执行计划...")
        body = planner.render_markdown(plan)

        # 阶段7：宣传物料
        if args.no_copy:
            print("[5/6] 跳过宣传物料生成（--no-copy）")
            full = body
        else:
            print("[5/6] 生成全套宣传物料（短视频脚本/话术/朋友圈文案）...")
            copy_gen = MarketingCopyGenerator()
            materials = copy_gen.generate(report)
            full = body + "\n" + materials["raw"] + "\n"

        print("[6/6] 方案生成完毕")

        if args.out:
            out_path = Path(args.out)
            out_path.write_text(full, encoding="utf-8")
            print(f"\n✅ 方案已保存：{out_path.resolve()}")
        else:
            print("\n" + "=" * 60)
            print(full)

        print("\n✅ 全部完成")
        return 0
    except RuntimeError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\n已取消", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
