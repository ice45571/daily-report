#!/usr/bin/env python3
"""
Show HN Solo Founder Finder — 分析版
抓取 Show HN 首页 → 识别 solo founder → 分析机会点 → 输出带 Takeway 的报告
"""

import json
import re
import urllib.request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

HN_ALGOLIA = "https://hn.algolia.com/api/v1/search"
LIMIT = 30


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  fetch error: {e}", file=__import__('sys').stderr)
        return None


def get_show_hn_frontpage(limit=LIMIT):
    """通过 Algolia API 获取 Show HN Front Page（官方推荐方式）"""
    url = f"{HN_ALGOLIA}?tags=show_hn&hitsPerPage={limit}"
    data = fetch_json(url)
    if not data:
        return []
    return data.get("hits", [])


def is_solo_founder(item):
    """判断是否是 solo founder"""
    title = item.get("title", "").lower()
    author = item.get("author", "").lower()
    text = (item.get("text") or "").lower()
    combined = title + " " + text

    SOLO_INDICATORS = [
        r"\(sf\)", r"\[sf\]", r"sf:",
        r"\bsolo\b", r" solo founder",
        r"\bi built\b", r"\bi made\b", r"built solo", r"made solo",
        r"\(my own\b", r"\bby me\b",
        r"single founder", r"one-person",
    ]

    for indicator in SOLO_INDICATORS:
        if re.search(indicator, combined):
            return True
    return False


def extract_info(item):
    """提取产品关键信息"""
    title = item.get("title", "")
    url = item.get("url") or f"https://news.ycombinator.com/item?id={item.get('objectID')}"
    author = item.get("author", "")
    points = item.get("points", 0)
    comments = item.get("num_comments", 0)
    hn_link = f"https://news.ycombinator.com/item?id={item.get('objectID')}"
    object_id = item.get("objectID", "")
    text = item.get("text") or ""

    return {
        "title": title,
        "url": url,
        "author": author,
        "points": points,
        "comments": comments,
        "hn_link": hn_link,
        "object_id": object_id,
        "body": text,
    }


def analyze_product(item):
    """分析产品机会点"""
    title = item.get("title", "")
    url = item.get("url", "")
    body = item.get("body", "") or ""
    points = item.get("points", 0)
    comments = item.get("num_comments", 0)

    insights = []

    # 从标题和内容提取关键词
    title_lower = title.lower()

    # 模式识别
    if any(kw in title_lower for kw in ["open?", "is ", "does ", "can ", "will "]):
        insights.append("「Yes/No 问题页」模式——简单直接的问答式页面，传播性极强")

    if any(kw in title_lower for kw in ["实时", "live", "real-time", "track", "monitor", "status"]):
        insights.append("「实时状态监控」——抓住时效性信息需求")

    if any(kw in title_lower for kw in ["tool", "cli", "api", "lib", "library", "sdk"]):
        insights.append("「开发者工具」——B端/开发者受众，付费意愿强，容易口碑传播")

    if any(kw in title_lower for kw in ["game", "play", "browser", "pixel"]):
        insights.append("「浏览器轻游戏」——蹭热点 + 病毒传播，蹭到就是大流量")

    if "ai" in title_lower or "gpt" in title_lower or "claude" in title_lower:
        insights.append("「AI 赋能」——蹭 AI 热点，但同质化严重，差异化是关键")

    if points > 200:
        insights.append(f"🔥 高分爆款（{points}分）——值得深度研究")

    if comments > 100:
        insights.append(f"💬 讨论火热（{comments}条评论）——说明击中了某个集体共鸣点")

    return insights


def generate_takeway(products):
    """生成总结"""
    if not products:
        return "今日首页无明显 solo founder 特征产品。"

    takeaways = []

    # 分析高分产品
    high_score = [p for p in products if p["points"] > 100]
    if high_score:
        top = max(high_score, key=lambda x: x["points"])
        takeaways.append(
            f"今日首页最高分：**{top['title']}**（{top['points']}分）"
        )

    # 分析讨论热度
    high_comments = [p for p in products if p["comments"] > 50]
    if high_comments:
        takeaways.append(
            f"讨论最热烈：**{max(high_comments, key=lambda x: x['comments'])['title']}**（{max(high_comments, key=lambda x: x['comments'])['comments']}条评论）"
        )

    # 共性模式
    titles_concat = " ".join([p["title"].lower() for p in products])

    patterns = []
    if any(k in titles_concat for k in ["open", "?", "is ", "does ", "status"]):
        patterns.append("「Yes/No 状态页」")
    if "api" in titles_concat or "tool" in titles_concat:
        patterns.append("「开发者工具」")
    if "ai" in titles_concat or "gpt" in titles_concat:
        patterns.append("「AI 应用」")
    if "game" in titles_concat or "play" in titles_concat:
        patterns.append("「轻游戏」")

    if patterns:
        takeaways.append(f"今日模式共性：**{' / '.join(set(patterns))}**")

    # 机会洞察
    takeaways.append(
        "\n💡 **机会捕捉**\n"
        "1. 实时热点 + 极简状态页 = 低成本高传播（参考 Is Hormuz open yet?）\n"
        "2. 开发者痛点工具化——解决自己每天遇到的小麻烦，就是一个好产品起点\n"
        "3. 地缘政治/新闻热点 + 数据可视化 = 天然的病毒传播土壤\n"
        "4. Solo founder 优势：速度 + 专注，单点突破比功能堆砌更重要"
    )

    return "\n".join(takeaways)


def generate_markdown(products, run_date):
    md = f"# 🔍 Show HN Solo Founder Report\n\n"
    md += f"**日期**: {run_date}\n"
    md += f"**首页 Solo Founder 产品数**: {len(products)}\n\n"
    md += "---\n\n"

    if not products:
        md += "今日首页暂无明确标记为 solo founder 的产品。\n"
        md += "\n## 📊 Takeway\n\n"
        md += generate_takeway(products)
        return md

    for i, p in enumerate(products, 1):
        md += f"## {i}. {p['title']}\n\n"
        md += f"👤 **作者**: @{p['author']} | "
        md += f"⭐ **{p['points']}** 分 | "
        md += f"💬 **{p['comments']}** 评论\n\n"
        md += f"🔗 **产品**: [{p['url']}]({p['url']})\n"
        md += f"💬 **HN**: [讨论]({p['hn_link']})\n\n"

        insights = analyze_product(p)
        if insights:
            md += "**📊 机会分析:**\n"
            for insight in insights:
                md += f"- {insight}\n"
            md += "\n"

        if p["body"]:
            body_preview = p["body"][:400].replace("<p>", "").replace("</p>", "\n")
            md += f"> {body_preview[:300]}{'...' if len(p['body']) > 300 else ''}\n\n"

        md += "---\n\n"

    # Takeway
    md += "## 📊 Takeway\n\n"
    md += generate_takeway(products)
    md += "\n"

    return md


def main():
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{run_date}] 开始抓取 Show HN Front Page...", flush=True)

    items = get_show_hn_frontpage()
    if not items:
        print("获取失败")
        return
    print(f"获取到 {len(items)} 条 Front Page 帖子", flush=True)

    solo_items = [item for item in items if is_solo_founder(item)]
    print(f"识别出 {len(solo_items)} 个 solo founder 产品", flush=True)

    products = [extract_info(item) for item in solo_items]
    md_content = generate_markdown(products, run_date)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"showhn-solo-{date_str}.md"
    output_path = f"/tmp/daily-report/{filename}"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n输出: {output_path}")
    print(md_content)

    return output_path


if __name__ == "__main__":
    main()
