# 🧰 DeepSeek CLI Tools — 4 Zero-Dependency Money-Making Tools

> **Give DeepSeek a prompt, get a poster, a drama script, a book monetization plan, or a full content pipeline — all from your terminal. No pip install, no API framework, pure Python stdlib.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Deps](https://img.shields.io/badge/dependencies-ZERO-green.svg)](#)
[![DeepSeek](https://img.shields.io/badge/powered_by-DeepSeek-4A6CF7.svg)](https://deepseek.com)

4 standalone CLI tools, each one file, each one solving a real "make money with AI" job:

| Tool | What it does | Output |
|------|-------------|--------|
| 🖼️ **`poster.py`** | Generate marketing posters | Copy + SVG poster (1080×1440, 6 layouts) |
| 🎬 **`drama.py`** | Generate short-drama scripts | Episode outline → full script with beats |
| 📚 **`monetize.py`** | Book → monetization plan | Assets, channels, pricing, compliance, exec plan |
| 🏭 **`content-studio.py`** | Automated content pipeline | Topic → article (batch, rewrite, niche) |

All four are **pure Python standard library — zero pip dependencies**. One shared config: your `DEEPSEEK_API_KEY`.

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. clone (or download the one file you need)
git clone https://github.com/chaoyibot/deepseek-cli-tools.git
cd deepseek-cli-tools

# 2. set your key (or add to ~/.dsh/.credentials.yaml)
export DEEPSEEK_API_KEY=sk-xxxx

# 3. run anything — try all 4 in one minute:
python poster/poster.py "AI coding course" --layout portrait
python drama/drama.py "a broke student finds a magic notebook"
python book-monetize/monetize.py book.txt --no-copy
python content-studio/studio.py "why AI agents matter" --count 3
```

**Windows one-liner** (PowerShell):
```powershell
.\install.ps1
```

**Linux/macOS one-liner**:
```bash
curl -fsSL https://raw.githubusercontent.com/chaoyibot/deepseek-cli-tools/main/install.sh | bash
```

The installers add `dsh-poster`, `dsh-drama`, `dsh-monetize`, `dsh-studio` commands to your PATH.

---

## 🖼️ Tool 1: Poster Generator (`poster.py`)

Input one topic → get marketing copy + a ready-to-use SVG poster.

```bash
python poster/poster.py "AI short-drama course" --layout portrait --out poster.svg
```

- 6 layouts: `portrait` (3:4, Xiaohongshu/Douyin), `landscape`, `minimal`, `bold`, `quote`, `event`
- Generates: title / subtitle / 3 selling points / CTA
- Pure SVG output — editable in any editor, scales losslessly

**Use case**: posters for your courses, books, products, WeChat moments, Xiaohongshu — in 30 seconds instead of hiring a designer.

---

## 🎬 Tool 2: Short-Drama Script Generator (`drama.py`)

Input a logline → get a production-ready vertical short-drama script (the fastest-growing content format in 2026).

```bash
python drama/drama.py "a broke student finds a magic notebook" --episodes 12
```

- Episode-by-episode outline → full script: scene / dialogue / action / emotion
- Hook design at every episode cliffhanger
- Outputs: overview + per-episode scripts + suspense map

**Use case**: short-drama creators, MCNs, or sell scripts as a service.

---

## 📚 Tool 3: Book Monetization Planner (`monetize.py`)

Input a manuscript → get a complete multi-channel monetization plan.

```bash
python book-monetize/monetize.py book.txt --out plan.md
```

Pipeline: manuscript analysis → asset extraction → monetization matrix (paid columns, courses, communities, licensing) → compliance check → pricing → execution plan → marketing copy.

**Use case**: self-published authors, course creators, anyone with content assets.

---

## 🏭 Tool 4: Content Pipeline (`content-studio.py`)

Automated content factory: auto topic → article, in batches, with rewrite mode.

```bash
python content-studio/studio.py                        # auto topic, 1 article
python content-studio/studio.py "AI agents" --count 5  # batch 5 articles
python content-studio/studio.py --rewrite draft.md     # de-duplicate rewrite
```

**Use case**: WeChat Official Account, Xiaohongshu, SEO blogs — daily output without writing.

---

## 🔑 Configuration

All tools read `DEEPSEEK_API_KEY` env var, or `~/.dsh/.credentials.yaml`:

```yaml
deepseek:
  api_key: sk-xxxx
  model: deepseek-v4-flash
```

Each tool accepts `--model` to override (e.g. `deepseek-chat`, `deepseek-reasoner`).

---

## 🧩 Project Layout

```
deepseek-cli-tools/
├── poster/          poster.py          — AI poster generator
├── drama/           drama.py           — short-drama script generator
├── book-monetize/   monetize.py + engine.py
├── content-studio/  studio.py + pipeline.py
├── install.sh       Linux/macOS installer (adds dsh-* commands)
├── install.ps1      Windows installer
└── README.md
```

Each tool is fully self-contained — **copy the one file you need** into any project, it just works.

---

## 💰 Support

If these tools save you time or make you money:

- ☕ **Buy me a coffee**: https://afdian.com/a/dg1688
- ⭐ **Star this repo** — it helps a solo developer keep shipping
- 🐛 Found a bug / want a feature? Open an issue or PR

---

## 📦 More from the same author

- [deepseek-prompts-cn](https://github.com/chaoyibot/deepseek-prompts-cn) — 300+ curated Chinese DeepSeek prompts (CLI searchable)
- [ai-drama-script](https://github.com/chaoyibot/ai-drama-script) — the drama tool, standalone
- [ai-poster-generator](https://github.com/chaoyibot/ai-poster-generator) — the poster tool, standalone
- [chaolingo](https://github.com/chaoyibot/chaolingo) — AI language learning app

## 📄 License

MIT — do whatever you want, just keep the license header.

---

## 💖 Support

If these tools help you, please:

- ⭐ Star the repo so more people can find it
- ☕ [Buy me a coffee](https://afdian.com/a/dg1688) — support the ongoing AI automation series (Afdian)
- 🤖 Follow the AI automation journey (content matrix / agents / monetization) via [ClawChat](https://clawling.com/u/usr_01KXT5GF70ESESJQZNB06AJQ9B)

More tools coming. Every star and coffee keeps this project alive 🚀
