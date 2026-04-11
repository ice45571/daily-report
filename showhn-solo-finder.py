#!/usr/bin/env python3
"""
Show HN Solo Founder Finder
每天定时抓取 Show HN 首页，识别 solo founder 产品，生成 Markdown 报告
"""

import json
import re
import urllib.request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

HN_API = "https://hacker-news.firebaseio.com/v0"
LIMIT = 30  # 每次抓前30条


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  fetch error: {e}", file=__import__('sys').stderr)
        return None


def get_show_hn_stories(limit=LIMIT):
    """获取 Show HN stories"""
    story_ids = fetch_json(f"{HN_API}/showstories.json")
    if not story_ids:
        return []
    return story_ids[:limit]


def fetch_story(story_id):
    item = fetch_json(f"{HN_API}/item/{story_id}.json")
    if item and item.get("type") == "story":
        return item
    return None


def get_stories_parallel(story_ids):
    """并发抓取 story 详情"""
    stories = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_story, sid): sid for sid in story_ids}
        for future in as_completed(futures):
            result = future.result()
            if result:
                stories.append(result)
    return stories


SOLO_INDICATORS = [
    r"\(sf\)", r"\[sf\]", r"sf:",
    r"\bsolo\b", r" solo founder",
    r"\bi built\b", r"\bi made\b", r"built solo", r"made solo",
    r"\(my own",
    r"single founder", r"one-person",
]


def is_solo_founder(story):
    title = story.get("title", "").lower()
    text = (story.get("text") or "").lower()
    combined = title + " " + text
    for indicator in SOLO_INDICATORS:
        if re.search(indicator, combined):
            return True
    return False


def extract_info(story):
    title = story.get("title", "")
    url = story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}"
    score = story.get("score", 0)
    comments = story.get("descendants", 0)
    hn_link = f"https://news.ycombinator.com/item?id={story['id']}"
    text = story.get("text") or ""
    return {
        "title": title,
        "url": url,
        "score": score,
        "comments": comments,
        "hn_link": hn_link,
        "body": text[:500] if text else "",
    }


def generate_markdown(products, run_date):
    md = f"# Show HN Solo Founder Report\n\n**日期**: {run_date}\n**总数**: {len(products)} 个 solo founder 产品上了 Show HN 首页\n\n---\n\n"
    if not products:
        md += "今日首页暂无明确标记为 solo founder 的产品。\n"
        return md
    for i, p in enumerate(products, 1):
        md += f"## {i}. {p['title']}\n\n"
        md += f"- **产品链接**: {p['url']}\n"
        md += f"- **HN 讨论**: {p['hn_link']}\n"
        md += f"- **Score**: {p['score']} | **Comments**: {p['comments']}\n\n"
        if p["body"]:
            preview = p["body"][:300]
            md += f"> {preview}{'...' if len(p['body']) > 300 else ''}\n\n"
        md += "---\n\n"
    return md


def main():
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{run_date}] 开始抓取 Show HN...", flush=True)

    story_ids = get_show_hn_stories()
    if not story_ids:
        print("无法获取 story IDs")
        return
    print(f"获取到 {len(story_ids)} 条 story IDs", flush=True)

    stories = get_stories_parallel(story_ids)
    print(f"抓回 {len(stories)} 条 stories", flush=True)

    solo_stories = [s for s in stories if is_solo_founder(s)]
    print(f"识别出 {len(solo_stories)} 个 solo founder 产品", flush=True)

    products = [extract_info(s) for s in solo_stories]

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
