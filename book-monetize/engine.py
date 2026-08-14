"""
ai-book-monetization - AI 拆书全域变现方案生成器

核心库：书稿定性分类 → 资产提取 → 变现路径匹配 → 合规检查 → 方案输出
将资深内容商业化操盘方法论固化为可执行代码。
纯标准库实现，零第三方依赖。
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-v4-flash"

# ============================================================
# 1. 书稿类型定义与自检清单（方法论固化）
# ============================================================

BOOK_TYPES = {
    "tool": {
        "name": "工具书",
        "desc": "教程、行业手册、实操指南、技术文稿",
        "readers_want": "学会技能、流程、实操方法",
        "carrier": "步骤、清单、SOP、案例、模板、工作流",
        "action": "看完立刻落地执行做事",
    },
    "mind": {
        "name": "思想认知类",
        "desc": "商业理论、心理学、底层逻辑、人性、哲学、认知成长",
        "readers_want": "重塑认知、掌握思维框架、看懂事物规律",
        "carrier": "观点、模型、理论、金句、思辨框架",
        "action": "看完改变看待事物的思路",
    },
    "story": {
        "name": "娱乐叙事类",
        "desc": "小说、故事、传记、纪实、散文",
        "readers_want": "获得情绪体验、消遣、沉浸式感受故事",
        "carrier": "人物、剧情、冲突、对白、反转情节",
        "action": "打发时间、感受故事情绪",
    },
}

# 三道自检题（30秒判定清单）
SELF_CHECK_QUESTIONS = [
    "问题1：读者看完最想获得什么？（学会技能/重塑认知/情绪体验）",
    "问题2：内容核心载体是什么？（步骤模板/观点模型/人物剧情）",
    "问题3：读者行动预期？（立刻执行/改变思路/消遣情绪）",
]

# 混合型书稿主次原则
MIXED_RULE = "混合型书稿遵循主次原则：标注主类别、次要类别，变现方案优先按主类设计。"

# ============================================================
# 2. 分类型专属变现路径矩阵（收益优先级从高到低）
# ============================================================

MONETIZATION_MATRIX = {
    "tool": {
        "专属变现手段": [
            "将书中完整流程拆解，封装成 AI Skill、标准化提示词、自动化工作流，作为付费会员核心权益",
            "依托书中方法论，对外承接商业项目、落地服务，把理论转化为接单产品",
            "拆分独立模块，制作模块化小课、单项工具包",
            "提取清单/表格/模板/脚本，打造引流款低价工具包（只释放片段，不放出完整文稿）",
            "开设实操训练营，以本书体系作为训练大纲，陪伴式动手落地",
        ],
        "衍生内容形式": "实操短视频、案例复盘播客、图文步骤拆解",
    },
    "mind": {
        "专属变现手段": [
            "萃取金句、思维模型、核心论点，制作图文海报、思辨口播短视频",
            "整合零散观点，重构系统化线上思维课程",
            "结合社会热点，用书中框架解读时事，打造深度内容",
            "举办读书会、线上话题辩论直播、深度共读栏目",
        ],
        "衍生内容形式": "深度长文专栏、长篇解读播客、观点讨论直播",
    },
    "story": {
        "专属变现手段": [
            "摘取冲突桥段、人物对白，改编短视频剧本、短剧脚本",
            "提炼名场面、故事段子，制作剧情短视频、有声播客",
            "开发剧情解读系列栏目，发起角色、剧情话题讨论",
            "二次创作同人图文、故事衍生内容",
        ],
        "衍生内容形式": "剧情解说短视频、睡前故事音频、剧情解析图文",
    },
}

# 三类通用保底变现方式（全部适用，必配置）
GENERIC_MONETIZATION = [
    "搭建主题体系化书单合集，公域引流，引导私域转化付费产品",
    "永久会员社群：完整素材包 + 持续更新衍生内容 + 社群答疑交流",
    "版权授权业务：节选内容转载授权、有声改编授权、企业素材年费授权",
    "公域内容策略：只对外发布章节节选，完整内容仅向付费用户开放",
    "周期性线上直播，系统性拆解全书内容",
    "知识博主跨界合作、流量互换、联合打包推广",
]

# ============================================================
# 3. 合规双场景规则
# ============================================================

COMPLIANCE = {
    "no_isbn": {
        "label": "🔵 场景A｜无书号原创电子文稿",
        "rules": [
            "所有文件、音频、视频素材禁止单独标价售卖，必须绑定服务作为配套福利",
            "交易标的统一为：知识社群、咨询服务、训练营、实战指导",
            "文档/音频/视频仅作为服务配套附属学习素材，禁止单独标价售卖",
        ],
        "red_lines": [
            "❌ 禁止直接售卖 PDF、电子书、打印册子、文稿文件",
            "❌ 禁止印刷无书号出版物",
            "❌ 禁止网盘单独兜售文稿",
        ],
    },
    "has_isbn": {
        "label": "🟢 场景B｜正规出版带ISBN图书",
        "rules": [
            "无售卖纸质书禁令，可叠加图书零售 + 衍生服务双路线",
            "电商、短视频橱窗销售纸质正版图书、官方电子书",
            "实体书店铺货、图书馆馆配、政企单位批量采购",
            "线下作者签售会",
            "IP 持续衍生：系列丛书、实体周边、品牌商业合作",
        ],
        "red_lines": [],
    },
}

# 风险分级
RISK_LEVELS = {
    "极低风险": ["会员社群", "咨询陪跑", "训练营", "版权授权", "公域节选内容引流"],
    "中等风险": ["线下小规模沙龙", "博主联名合作", "技能商业接单"],
    "高危禁止": ["公开售卖PDF", "印刷无书号出版物", "网盘单独兜售文稿"],
}

# 敏感词过滤（宣传物料自动过滤）
SENSITIVE_WORDS = ["卖书", "电子书", "PDF购买", "书稿售卖", "购买PDF", "售卖文稿", "卖电子版"]

# 产品阶梯定价框架
PRICING_LADDER = [
    ("低价引流工具包", "9.9~49元", "片段素材/模板/清单，引流获客"),
    ("主力永久会员", "99~299元", "完整素材包 + 持续衍生内容 + 社群答疑"),
    ("主题训练营", "499~1999元", "陪伴式实操落地，按主题开班"),
    ("一对一高阶咨询", "1999~9999元", "深度定制服务，按次或按周期"),
]

# 强制交付顺序
DELIVERY_ORDER = ["付款", "开通社群服务权限", "发放配套素材"]
DELIVERY_RULE = "强制交付顺序：付款 → 开通社群服务权限 → 发放配套素材，禁止裸交付、先发资料后拉群"

# 分阶段执行路线
EXECUTION_PHASES = [
    ("短期 0~30天", "内容搭建 + 引流启动"),
    ("中期 1~6个月", "产品转化 + 社群运营"),
    ("长期 6个月以上", "版权资产复用 + IP 放大"),
]

# 万能9步框架
NINE_STEP_FRAMEWORK = [
    "使用自检清单完成书稿定性分类",
    "提取内容核心可复用资产",
    "将全文模块化拆分为多个素材单元",
    "匹配对应书籍类型专属变现方案",
    "叠加全品类通用保底变现方式",
    "多媒介内容衍生：图文/短视频/播客/直播",
    "搭建分层付费产品矩阵",
    "搭建公域引流 + 私域转化完整闭环",
    "长期运营，持续复用版权资产",
]


# ============================================================
# 4. DeepSeek 客户端
# ============================================================

class DeepSeekClient:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or self._load_api_key()
        self.model = model
        if not self.api_key:
            raise RuntimeError(
                "未找到 DEEPSEEK_API_KEY。请设置环境变量，或写入 ~/.dsh/.credentials.yaml"
            )

    @staticmethod
    def _load_api_key() -> str | None:
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
             temperature: float = 0.8) -> str:
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


# ============================================================
# 5. 核心引擎
# ============================================================

@dataclass
class BookReport:
    book_type: str = ""
    type_name: str = ""
    secondary_type: str = ""
    assets: list[str] = field(default_factory=list)
    confidence: str = ""


class BookAnalyzer:
    """书稿定性分类引擎（内置30秒自检清单，AI辅助判定）"""

    def __init__(self, client: DeepSeekClient | None = None):
        self.client = client or DeepSeekClient()

    def classify(self, text: str) -> BookReport:
        excerpt = text[:6000]
        sys_prompt = (
            "你是资深内容商业化操盘专家。执行三道自检题判定书稿类型：\n"
            f"{chr(10).join(SELF_CHECK_QUESTIONS)}\n\n"
            f"{MIXED_RULE}\n\n"
            "书稿类型定义：\n"
            + "\n".join(f"- {v['name']}: {v['desc']}" for v in BOOK_TYPES.values()) +
            "\n\n只输出 JSON（不要 markdown 代码块），格式：\n"
            '{"type": "tool|mind|story", "type_name": "工具书/思想认知类/娱乐叙事类", '
            '"secondary_type": "次要类别名或空字符串", "confidence": "高/中/低", '
            '"assets": ["核心可复用资产1", "资产2", ...]}'
        )
        out = self.client.chat(sys_prompt, f"书稿内容（节选）：\n{excerpt}", max_tokens=1500)
        m = re.search(r"\{.*\}", out, re.S)
        if not m:
            raise RuntimeError(f"AI 返回无法解析: {out[:200]}")
        data = json.loads(m.group(0))
        btype = data.get("type", "tool")
        if btype not in BOOK_TYPES:
            btype = "tool"
        return BookReport(
            book_type=btype,
            type_name=data.get("type_name") or BOOK_TYPES[btype]["name"],
            secondary_type=data.get("secondary_type", ""),
            assets=data.get("assets", []),
            confidence=data.get("confidence", "中"),
        )


class MonetizationPlanner:
    """变现方案生成器：专属矩阵 + 通用保底 + 合规 + 定价 + 执行计划"""

    def __init__(self, client: DeepSeekClient | None = None):
        self.client = client or DeepSeekClient()

    def build_plan(self, report: BookReport, has_isbn: bool) -> dict:
        matrix = MONETIZATION_MATRIX.get(report.book_type, MONETIZATION_MATRIX["tool"])
        compliance = COMPLIANCE["has_isbn"] if has_isbn else COMPLIANCE["no_isbn"]
        return {
            "report": report,
            "has_isbn": has_isbn,
            "matrix": matrix,
            "generic": GENERIC_MONETIZATION,
            "compliance": compliance,
            "risk": RISK_LEVELS,
            "pricing": PRICING_LADDER,
            "delivery": {"order": DELIVERY_ORDER, "rule": DELIVERY_RULE},
            "phases": EXECUTION_PHASES,
            "framework": NINE_STEP_FRAMEWORK,
        }

    def render_markdown(self, plan: dict) -> str:
        r = plan["report"]
        lines = [
            "# 📚 书稿全域多元变现方案",
            "",
            f"> 生成时间：由 AI 拆书变现引擎自动输出",
            "",
            "---",
            "",
            "## ① 书稿定性判定结果",
            "",
            f"- **最终归类**：{r.type_name}（置信度：{r.confidence}）",
            f"- **次要属性**：{r.secondary_type or '无'}",
            f"- **核心内容资产**：",
        ]
        for a in r.assets:
            lines.append(f"  - {a}")
        if not r.assets:
            lines.append("  - （AI 未能提取，请人工补充）")

        lines += ["", "---", "", "## ② 专属变现路径矩阵（收益优先级从高到低）", ""]
        for i, m in enumerate(plan["matrix"]["专属变现手段"], 1):
            lines.append(f"{i}. {m}")
        lines += ["", f"**衍生内容形式**：{plan['matrix']['衍生内容形式']}", ""]

        lines += ["---", "", "## ③ 通用保底变现方式（必配置）", ""]
        for i, g in enumerate(plan["generic"], 1):
            lines.append(f"{i}. {g}")

        lines += ["", "---", "", f"## ④ {plan['compliance']['label']}", ""]
        for rule in plan["compliance"]["rules"]:
            lines.append(f"- {rule}")
        if plan["compliance"]["red_lines"]:
            lines += ["", "**🚨 红线（强制遵守）**："]
            for rl in plan["compliance"]["red_lines"]:
                lines.append(f"- {rl}")

        lines += ["", "---", "", "## ⑤ 风险分级标注", ""]
        for level, items in plan["risk"].items():
            lines.append(f"- **{level}**：{'、'.join(items)}")

        lines += ["", "---", "", "## ⑥ 产品阶梯定价框架", ""]
        lines.append("| 层级 | 定价 | 内容 |")
        lines.append("|------|------|------|")
        for tier, price, desc in plan["pricing"]:
            lines.append(f"| {tier} | {price} | {desc} |")

        lines += ["", "---", "", "## ⑦ 标准交付 SOP", ""]
        lines.append(f"**{plan['delivery']['rule']}**")
        lines += ["", "交付顺序："]
        for i, step in enumerate(plan["delivery"]["order"], 1):
            lines.append(f"{i}. {step}")

        lines += ["", "---", "", "## ⑧ 落地执行路线", ""]
        for phase, desc in plan["phases"]:
            lines.append(f"- **{phase}**：{desc}")

        lines += ["", "---", "", "## ⑨ 万能9步复用模型", ""]
        for i, step in enumerate(plan["framework"], 1):
            lines.append(f"{i}. {step}")

        lines += ["", "---", "", "> ⚠️ 本方案由 AI 生成，仅供商业化思路参考。无书号文稿请严格遵守红线条款，杜绝违规售卖。", ""]
        return "\n".join(lines)


class MarketingCopyGenerator:
    """宣传物料生成器：短视频脚本/播客文案/主页简介/私信话术/朋友圈文案，自动过滤敏感词"""

    SENSITIVE = SENSITIVE_WORDS

    def __init__(self, client: DeepSeekClient | None = None):
        self.client = client or DeepSeekClient()

    @staticmethod
    def filter_sensitive(text: str) -> str:
        for w in MarketingCopyGenerator.SENSITIVE:
            text = re.sub(re.escape(w), "[已过滤]", text)
        return text

    def generate(self, report: BookReport) -> dict:
        type_cn = report.type_name
        assets = "、".join(report.assets[:5]) if report.assets else "核心内容"
        sys_prompt = (
            f"你是资深新媒体文案。为一部{type_cn}书稿生成全套宣传物料。\n"
            f"该书稿核心资产：{assets}\n\n"
            "输出5部分，每部分用【】标题分隔：\n"
            "【短视频脚本】30秒口播脚本，钩子开头+3个要点+行动号召\n"
            "【账号主页简介】120字内个人简介，突出价值\n"
            "【私信承接话术】3条，用于用户咨询时的回复\n"
            "【朋友圈文案】3条，分别用于：发布预告/成果展示/互动提问\n"
            "【直播预告文案】1条，200字内\n\n"
            "要求：突出知识服务价值，不出现售卖文件、PDF、电子书等字眼；"
            "用口语化、有温度的表达。"
        )
        out = self.client.chat(sys_prompt, "请生成全套宣传物料", max_tokens=2500)
        out = self.filter_sensitive(out)
        return {"raw": out}

    def render_markdown(self, materials: dict) -> str:
        return f"## 📣 宣传物料（已自动过滤敏感词）\n\n{materials['raw']}\n"
