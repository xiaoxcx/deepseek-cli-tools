"""
dsh-content-studio - DeepSeek 中文自媒体内容自动化生产流水线

核心库：选题 / 写作 / 原创化改写 / 批量导出
纯标准库实现，零第三方依赖。
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-v4-flash"


class DeepSeekClient:
    """DeepSeek API 客户端（OpenAI 兼容接口，纯标准库实现）"""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or self._load_api_key()
        self.model = model
        if not self.api_key:
            raise RuntimeError(
                "未找到 DEEPSEEK_API_KEY。请设置环境变量，或写入 ~/.dsh/.credentials.yaml"
            )

    @staticmethod
    def _load_api_key() -> str | None:
        """从环境变量或 dsh 凭据文件读取 API Key"""
        env_key = os.environ.get("DEEPSEEK_API_KEY")
        if env_key:
            return env_key.strip()
        cred_file = Path.home() / ".dsh" / ".credentials.yaml"
        if cred_file.exists():
            for line in cred_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY:"):
                    return line.split(":", 1)[1].strip()
        return None

    def chat(self, system: str, user: str, max_tokens: int = 4000,
             temperature: float = 0.85) -> str:
        """调用 DeepSeek chat completions"""
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
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
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek API 错误 {e.code}: {detail}") from e
        return data["choices"][0]["message"]["content"]


class ContentPipeline:
    """内容生产流水线：选题 -> 写作 -> 原创化 -> 导出"""

    def __init__(self, client: DeepSeekClient | None = None):
        self.client = client or DeepSeekClient()

    # ---------- 选题引擎 ----------
    def generate_topics(self, niche: str = "职场效率/AI工具/生活技巧",
                        count: int = 5) -> list[str]:
        sys_prompt = (
            f"你是资深新媒体主编。请围绕领域「{niche}」生成 {count} 个"
            "适合普通读者、有传播力的干货选题。要求：\n"
            "1. 每个选题带具体痛点或数字，不要空泛\n"
            "2. 适合头条号/公众号传播\n"
            "3. 只输出编号列表（1. xxx），不要其他内容"
        )
        out = self.client.chat(sys_prompt, f"请生成 {count} 个选题", max_tokens=1000)
        topics = []
        for ln in out.splitlines():
            ln = ln.strip()
            m = re.match(r"^\d+[.、]\s*(.+)$", ln)
            if m:
                topics.append(m.group(1).strip())
        # 兜底：无编号则全部按行收
        if not topics:
            topics = [ln.strip() for ln in out.splitlines() if ln.strip()]
        return topics[:count]

    # ---------- 写作 ----------
    def write_article(self, topic: str) -> dict:
        sys_prompt = (
            "你是今日头条签约作者，擅长写高完读率的中文干货文章。要求：\n"
            "1. 标题不超过30字，带数字或痛点，吸引点击但不过度标题党\n"
            "2. 正文1000-1500字，开头50字内抓住读者\n"
            "3. 分3-5个小标题，段落短（每段不超过4行），多用口语化表达\n"
            "4. 内容必须具体可操作，有真实细节，禁止空话套话\n"
            "5. 结尾留互动问题引导评论\n"
            "6. 输出格式：第一行【标题】xxx，第二行【正文】然后接全文"
        )
        out = self.client.chat(sys_prompt, f"选题：{topic}", max_tokens=3500)
        title = ""
        body = out
        if "【标题】" in out:
            title = out.split("【标题】", 1)[-1].splitlines()[0].strip()
            if "【正文】" in out:
                body = out.split("【正文】", 1)[-1].strip()
        if not title:
            title = topic[:30]
        return {"topic": topic, "title": title, "body": body}

    # ---------- 原创化改写 ----------
    def rewrite_article(self, source_text: str) -> dict:
        sys_prompt = (
            "你是资深内容编辑，负责对文章进行原创化深度改写。要求：\n"
            "1. 保留核心观点和信息，但重组结构、换用不同表达\n"
            "2. 调整段落顺序、改写开头结尾、替换同义表达\n"
            "3. 增加个人化语气和细节，使其通过原创检测\n"
            "4. 篇幅与原文章相当\n"
            "5. 输出格式：第一行【标题】xxx，第二行【正文】然后接全文"
        )
        out = self.client.chat(sys_prompt, f"原文如下：\n{source_text}", max_tokens=3500)
        title = ""
        body = out
        if "【标题】" in out:
            title = out.split("【标题】", 1)[-1].splitlines()[0].strip()
            if "【正文】" in out:
                body = out.split("【正文】", 1)[-1].strip()
        return {"title": title, "body": body}

    # ---------- 导出 ----------
    @staticmethod
    def to_markdown(title: str, body: str) -> str:
        return f"标题：{title}\n\n{body}"

    def save(self, article: dict, out_dir: Path, index: int) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r'[\\/:*?"<>|]', "_", article.get("title", f"article-{index}"))[:40]
        path = out_dir / f"{index:03d}-{safe}.md"
        path.write_text(self.to_markdown(article.get("title", ""), article.get("body", "")),
                        encoding="utf-8")
        return path
