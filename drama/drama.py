#!/usr/bin/env python3
"""
ai-drama-script - AI 短剧脚本生成器

输入一个故事梗概/主题，自动生成完整短剧脚本：
分集大纲 → 单集脚本（场景/对白/动作/情绪）→ 爆点设计

纯标准库，零依赖，DeepSeek 驱动。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-v4-flash"


class DeepSeekClient:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or self._load_api_key()
        self.model = model
        if not self.api_key:
            raise RuntimeError("未找到 DEEPSEEK_API_KEY（环境变量或 ~/.dsh/.credentials.yaml）")

    @staticmethod
    def _load_api_key() -> str | None:
        env_key = os.environ.get("DEEPSEEK_API_KEY")
        if env_key:
            return env_key.strip()
        cred = Path.home() / ".dsh" / ".credentials.yaml"
        if cred.exists():
            for line in cred.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY:"):
                    return line.split(":", 1)[1].strip()
        return None

    def chat(self, system: str, user: str, max_tokens: int = 4000, temperature: float = 0.9) -> str:
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode("utf-8")
        req = urllib.request.Request(API_URL, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        })
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"API 错误 {e.code}: {e.read().decode('utf-8', 'replace')}") from e
        return data["choices"][0]["message"]["content"]


def generate_outline(client: DeepSeekClient, concept: str, episodes: int) -> str:
    sys_prompt = (
        "你是爆款竖屏短剧编剧。根据概念设计分集大纲。要求：\n"
        f"1. 共 {episodes} 集，每集2-3分钟体量\n"
        "2. 每集结尾必须有钩子（悬念/反转/冲突升级）\n"
        "3. 符合竖屏短剧节奏：开头3秒抓人，每30秒一个小高潮\n"
        "4. 输出格式：每集一行【第X集】标题：内容概要（含结尾钩子）"
    )
    return client.chat(sys_prompt, f"故事概念：{concept}", max_tokens=2500)


def generate_episode(client: DeepSeekClient, concept: str, outline: str, episode_no: int) -> str:
    sys_prompt = (
        "你是爆款竖屏短剧编剧。根据分集大纲，扩写单集完整脚本。要求：\n"
        "1. 场景+对白+动作+情绪标注的完整脚本格式\n"
        "2. 对白口语化、有冲突、信息量密度高\n"
        "3. 结尾带钩子\n"
        "4. 输出：场景标题、角色动作、对白（角色名：台词）\n"
        "5. 全文字数800-1200字"
    )
    return client.chat(sys_prompt, f"故事概念：{concept}\n\n分集大纲：\n{outline}\n\n请扩写第 {episode_no} 集：", max_tokens=3500)


def main() -> int:
    parser = argparse.ArgumentParser(description="AI 短剧脚本生成器")
    parser.add_argument("concept", help="故事概念/梗概（一句话或一段话）")
    parser.add_argument("--episodes", type=int, default=6, help="分集数（默认6）")
    parser.add_argument("--episode", type=int, default=0, help="只生成指定集（0=全部）")
    parser.add_argument("--out", default=None, help="输出目录（默认当前目录）")
    args = parser.parse_args()

    try:
        print("=" * 56)
        print("  ai-drama-script | AI 短剧脚本生成器")
        print("=" * 56)
        client = DeepSeekClient()

        print(f"\n[1/2] 生成 {args.episodes} 集分集大纲...")
        outline = generate_outline(client, args.concept, args.episodes)
        print(outline)

        out_dir = Path(args.out) if args.out else Path(".")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "outline.md").write_text(f"# 分集大纲\n\n{outline}\n", encoding="utf-8")
        print(f"\n[大纲已保存] {out_dir / 'outline.md'}")

        if args.episode > 0:
            print(f"\n[2/2] 扩写第 {args.episode} 集...")
            script = generate_episode(client, args.concept, outline, args.episode)
            path = out_dir / f"episode-{args.episode:02d}.md"
            path.write_text(f"# 第{args.episode}集\n\n{script}\n", encoding="utf-8")
            print(f"\n[脚本已保存] {path}")
            print("\n" + script[:2000])
        else:
            print(f"\n[2/2] 扩写全部 {args.episodes} 集...")
            for i in range(1, args.episodes + 1):
                print(f"  第 {i}/{args.episodes} 集...")
                script = generate_episode(client, args.concept, outline, i)
                path = out_dir / f"episode-{i:02d}.md"
                path.write_text(f"# 第{i}集\n\n{script}\n", encoding="utf-8")
            print(f"\n✅ 全部完成，输出目录：{out_dir.resolve()}")
        return 0
    except RuntimeError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\n已取消", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
