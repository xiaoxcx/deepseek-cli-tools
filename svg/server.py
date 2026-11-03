#!/usr/bin/env python3
"""
svg-logo-generator - 本地 Web 服务：文本描述 -> SVG 图标

零依赖（仅 Python 标准库）。
运行:  python server.py
然后浏览器打开:  http://127.0.0.1:8000

图标风格参考阿里云图标库 / Iconfont 的扁平图标。
DeepSeek API Key 从环境变量 DEEPSEEK_API_KEY 读取。
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"
HERE = Path(__file__).resolve().parent


class DeepSeekClient:
    """与现有工具一致的带重试客户端（空响应/429/5xx 自动退避）"""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or self._load_api_key()
        self.model = model
        if not self.api_key:
            raise RuntimeError("未找到 DEEPSEEK_API_KEY（请设置环境变量或 ~/.dsh/.credentials.yaml）")

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

    def chat(self, system: str, user: str, max_tokens: int = 2000,
             temperature: float = 0.7, max_retries: int = 5) -> str:
        last_err: Exception | None = None
        for attempt in range(max_retries):
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
                content = data["choices"][0]["message"]["content"]
                if content and content.strip():
                    return content
                last_err = RuntimeError(f"API 返回空内容（第 {attempt + 1} 次尝试）")
                print(f"  ⚠️ 空内容，重试 ({attempt + 1}/{max_retries})...")
            except urllib.error.HTTPError as e:
                last_err = RuntimeError(f"API 错误 {e.code}: {e.read().decode('utf-8', 'replace')}")
                if e.code in (429, 500, 502, 503):
                    print(f"  ⚠️ API {e.code}，重试 ({attempt + 1}/{max_retries})...")
                else:
                    raise last_err
            except (json.JSONDecodeError, KeyError) as e:
                last_err = RuntimeError(f"响应解析失败: {e}")
                print(f"  ⚠️ 解析失败，重试 ({attempt + 1}/{max_retries})...")
            if attempt < max_retries - 1:
                import time
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"模型多次返回空响应: {last_err}")


def build_prompt(prompt: str, style: str, color: str) -> str:
    style_desc = {
        "line": "线性图标：仅描边，stroke-width 约 48，无填充，圆角拐点，简洁",
        "filled": "填充图标：仅纯色填充，无描边，块面简洁",
        "duotone": "双色图标：主色 + 浅色辅助，主形填充主色、细节用浅色，层次清晰",
    }.get(style, "线性图标：仅描边，无填充")
    return (
        "你是专业的图标设计师，风格参考阿里云图标库 / Iconfont 的扁平图标。\n"
        "根据描述生成一个简洁、可识别的 SVG 图标。硬性要求：\n"
        "1. 只输出纯 SVG 代码，不要 markdown 代码块、不要任何解释文字。\n"
        "2. 根节点必须是 <svg>，viewBox 固定为 '0 0 1024 1024'。\n"
        f"3. 风格：{style_desc}。\n"
        f"4. 颜色：主色使用 '{color}'（双色时辅助色用它的浅色调），不要使用其他随机色。\n"
        "5. 图形居中、留白合理、轮廓清晰，像一个能直接进图标库的成品。\n"
        "6. 除非描述明确要求，否则不要包含 <text> 文字。"
    )


def extract_svg(raw: str) -> str:
    # 1. 剥掉 markdown 代码围栏
    s = re.sub(r"^```(?:svg|xml)?\s*|\s*```$", "", raw.strip(), flags=re.S)
    # 2. 定位第一个 <svg 起点
    start = re.search(r"<svg[\s\S]*", s, re.I)
    if not start:
        raise RuntimeError("模型未返回有效 SVG")
    frag = s[start.start():]
    # 3. 截取第一个 <svg> 到闭合标签之间的内容
    close = re.search(r"</svg\s*>", frag, re.I)
    if close:
        frag = frag[:close.end()]
    else:
        # 模型偶尔漏写闭合标签，自动补全（应对截断/遗漏）
        frag = frag.rstrip() + "\n</svg>"
    return frag.strip()


def generate_icon(prompt: str, style: str, color: str) -> str:
    if not prompt.strip():
        raise RuntimeError("描述不能为空")
    client = DeepSeekClient()
    raw = client.chat(build_prompt(prompt, style, color), f"图标描述：{prompt}",
                      max_tokens=2000, temperature=0.7)
    return extract_svg(raw)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body, ctype: str = "application/json; charset=utf-8"):
        data = body if isinstance(body, (bytes, bytearray)) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (HERE / "index.html").read_text(encoding="utf-8"),
                       "text/html; charset=utf-8")
        else:
            self._send(404, json.dumps({"error": "not found"}, ensure_ascii=False))

    def do_POST(self):
        if self.path == "/api/generate":
            try:
                length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(length) or b"{}")
                svg = generate_icon(payload.get("prompt", ""),
                                    payload.get("style", "line"),
                                    payload.get("color", "#4A6CF7"))
                self._send(200, json.dumps({"svg": svg}, ensure_ascii=False))
            except Exception as e:  # noqa: BLE001
                self._send(500, json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            self._send(404, json.dumps({"error": "not found"}, ensure_ascii=False))

    def log_message(self, *args):  # 静默访问日志
        pass


def main() -> int:
    port = int(os.environ.get("PORT", "8000"))
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("=" * 56)
    print("  svg-logo-generator | 文本 -> SVG 图标生成器")
    print("=" * 56)
    print(f"\n  已启动:  http://127.0.0.1:{port}")
    print("  停止:    Ctrl+C\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
    return 0


if __name__ == "__main__":
    sys.exit(main())
