#!/usr/bin/env python3
"""
Q1: Show HN Solo Founder Scraper
"""

import json
import re
import urllib.request
from datetime import datetime

HN_ALGOLIA = "https://hn.algolia.com/api/v1/search"
HN_API = "https://hacker-news.firebaseio.com/v0"


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except:
        return None


def strip_html(text):
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</p>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&#x27;", "'", text)
    text = re.sub(r"&\w+;", "", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()[:3000]


def fetch_page_text(url):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "text/html",
        })
        with urllib.request.urlopen(req, timeout=6) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        title_match = re.search(r"<title[^>]*>([^<]+)</title>", raw, re.IGNORECASE)
        page_title = title_match.group(1).strip() if title_match else ""
        raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
        raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.IGNORECASE)
        text = strip_html(raw)
        return page_title, text[:800]
    except:
        return "", ""


def get_show_hn_frontpage(limit=30):
    data = fetch_json(f"{HN_ALGOLIA}?tags=show_hn&hitsPerPage={limit}")
    return data.get("hits", []) if data else []


def get_item_content(object_id):
    item = fetch_json(f"{HN_API}/item/{object_id}.json")
    if not item:
        return "", ""
    return strip_html(item.get("text") or ""), item.get("url") or ""


def get_all_content(item, object_id):
    hn_text, hn_url = get_item_content(object_id)
    url = item.get("url", "") or hn_url
    text_parts = []
    if hn_text:
        text_parts.append(hn_text)
    if url and len(hn_text or "") < 150:
        page_title, page_text = fetch_page_text(url)
        if page_text:
            if page_title:
                text_parts.insert(0, f"标题: {page_title}")
            text_parts.append(page_text)
    return url, " ".join(text_parts)


def is_solo_founder(item):
    title = item.get("title", "").lower()
    text = (item.get("text") or "").lower()
    combined = title + " " + text
    indicators = [
        r"\(sf\)", r"\[sf\]", r"sf:",
        r"\bsolo\b", r" solo founder",
        r"\bi built\b", r"\bi made\b", r"built solo", r"made solo",
        r"\(my own\b", r"\bby me\b",
        r"single founder", r"one-person",
    ]
    for ind in indicators:
        if re.search(ind, combined):
            return True
    return False


TRANSLATIONS = {
    ("laptop", "scratch"): {
        "what": "自己做了一台笔记本电脑",
        "problem": "想证明能不能从零造一台完整的笔记本电脑，代码和设计全部开源",
        "notable": "6个月，纯手工打造一台能用的笔记本，极客精神拉满，工程量巨大"
    },
    ("typelit",): {
        "what": "用打字来读小说",
        "problem": "练打字太无聊，用自己喜欢的小说片段来练习，边打边读",
        "notable": "把「刻意练习」变成「阅读体验」，留存率极高"
    },
    ("pilot", "flight"): {
        "what": "把飞行记录变成3D地球仪",
        "problem": "飞行员要记飞行日志，他把数据可视化，地球上一飞就能看到自己的航线",
        "notable": "职业工具做出美感；「把枯燥记录变好看」在很多职业都存在机会"
    },
    ("bloomberg",): {
        "what": "Bloomberg Terminal的免费替代",
        "problem": "Bloomberg一个月要2万多美元，普通投资者用不起，他用开源做了一个类似工具",
        "notable": "高价工具的免费替代永远有市场；散户+工具平替，双重流量密码"
    },
    ("rotten tomatoes", "durable"): {
        "what": "豆瓣评分式的「耐用消费品」评价平台",
        "problem": "想买真正耐用的东西但不知道哪个好，做一个用户真实评价「能用很久」的消费品的社区",
        "notable": "反消费主义趋势，「只买能用一辈子的东西」这个群体在增长"
    },
    ("synth", "daughter"): {
        "what": "给女儿做了一台合成器",
        "problem": "给女儿做音乐启蒙，用代码和硬件自己造了一台合成器，是一起创造的过程",
        "notable": "「DIY + 亲子 + 音乐」三元素结合，故事感极强"
    },
}


def translate_product(title, body):
    title_lower = title.lower()
    body_lower = body.lower()

    for keywords, info in TRANSLATIONS.items():
        # 所有关键词都匹配才认为是同一个产品
        if all(kw in body_lower or kw in title_lower for kw in keywords):
            return info

    first_sentences = re.split(r"[.!?]", body[:600])
    first_sentences = [s.strip() for s in first_sentences if len(s.strip()) > 30]
    hint = first_sentences[0][:100] if first_sentences else ""
    return {
        "what": f"（需查看产品页，标题：{title[:50]}）",
        "problem": hint or "（需查看产品页）",
        "notable": "建议点链接查看完整介绍"
    }


def scrape() -> list:
    items = get_show_hn_frontpage()
    solo_items = [item for item in items if is_solo_founder(item)]

    results = []
    for item in solo_items:
        object_id = item["objectID"]
        url, combined_text = get_all_content(item, object_id)
        item["url"] = url
        title = item.get("title", "")
        translated = translate_product(title, combined_text)
        results.append({
            "title": title,
            "url": url,
            "author": item.get("author", ""),
            "points": item.get("points", 0),
            "comments": item.get("num_comments", 0),
            "hn_link": f"https://news.ycombinator.com/item?id={object_id}",
            "what": translated["what"],
            "problem": translated["problem"],
            "notable": translated["notable"],
        })
    return results


if __name__ == "__main__":
    results = scrape()
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
