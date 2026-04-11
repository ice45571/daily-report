#!/usr/bin/python3
"""
Q2: GitHub Trending Scraper
从 github.com/trending 抓取真实 Trending 数据（HTML解析）
fallback: GitHub Search API
"""

import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime


def parse_trending_html(html: bytes) -> list:
    """解析 GitHub Trending HTML（lxml）"""
    try:
        from lxml import html as lh
    except ImportError:
        print("lxml not available, using regex fallback", file=sys.stderr)
        return parse_trending_regex(html)

    tree = lh.fromstring(html)
    articles = tree.xpath('//article')
    results = []

    for art in articles:
        # repo 链接
        all_hrefs = art.xpath('.//@href')
        repo_name = None
        for href in all_hrefs:
            if not href:
                continue
            skip = ['login', 'stargazers', 'forks', 'issues', 'pulse',
                    'actions', 'settings', 'wiki', '/search', '/notifications']
            if any(s in href for s in skip):
                continue
            parts = href.strip('/').split('/')
            if len(parts) == 2 and parts[0] and parts[1]:
                repo_name = href.strip('/')
                break

        if not repo_name:
            continue

        # 描述
        desc_nodes = art.xpath('.//p[contains(@class, "color-fg-muted")]')
        desc = ""
        for node in desc_nodes:
            text = "".join(node.xpath(".//text()")).strip()
            if text:
                desc = text
                break

        # 语言
        lang_nodes = art.xpath('.//span[@itemprop="programmingLanguage"]')
        language = ""
        if lang_nodes:
            language = "".join(lang_nodes[0].xpath(".//text()")).strip()

        # Star 数
        star_nodes = art.xpath('.//a[contains(@href, "/stargazers")]')
        stars_str = ""
        for node in star_nodes:
            text = "".join(node.xpath(".//text()")).strip()
            if text and text not in ("Stars", "Star"):
                stars_str = text
                break

        # 今日新增 stars（在 SVG 旁边的 text 里）
        today_stars = ""
        # 找包含数字的 span
        span_texts = art.xpath('.//span[@class="d-inline-flex"]//text()')
        for t in span_texts:
            t = t.strip()
            if re.match(r'^[\d,]+$', t):
                today_stars = t
                break

        results.append({
            "name": repo_name,
            "description": desc,
            "language": language,
            "stars": stars_str,
            "today_stars": today_stars,
            "url": f"https://github.com/{repo_name}",
        })

    return results


def parse_trending_regex(html: bytes) -> list:
    """正则 fallback（当 lxml 不可用时）"""
    text = html.decode("utf-8", errors="ignore")
    results = []

    # 找所有 article 块
    article_blocks = re.findall(r'<article[^>]*>(.*?)</article>', text, re.DOTALL)
    for block in article_blocks:
        # repo 名
        repo_match = re.search(r'<a[^>]+href="/([^/]+/[^"]+)"[^>]*>\s*<svg[^>]*octicon-star', block)
        if not repo_match:
            continue
        repo_name = repo_match.group(1)

        # 描述
        desc_match = re.search(r'<p[^>]*class="[^"]*color-fg-muted[^"]*"[^>]*>(.*?)</p>', block, re.DOTALL)
        desc = re.sub(r'<[^>]+>', '', desc_match.group(1) if desc_match else '').strip()[:200]

        # 语言
        lang_match = re.search(r'programmingLanguage[^>]*>([^<]+)<', block)
        language = lang_match.group(1).strip() if lang_match else ''

        # stars
        star_match = re.search(r'aria-label="([\d,]+) star', block)
        stars_str = star_match.group(1) if star_match else ""

        results.append({
            "name": repo_name,
            "description": desc,
            "language": language,
            "stars": stars_str,
            "today_stars": "",
            "url": f"https://github.com/{repo_name}",
        })

    return results


def fetch_trending_html() -> bytes:
    """抓取 github.com/trending HTML"""
    req = urllib.request.Request(
        "https://github.com/trending",
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "text/html",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()


def fetch_via_github_api() -> list:
    """
    通过 GitHub Search API 获取 trending 新项目（1000-30000 stars）
    策略：创建时间较新（2024年后）+ 最近push + 排除巨型知名项目
    """
    import os
    token = os.environ.get("GH_TOKEN", "")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"token {token}" if token else "",
        "Accept": "application/vnd.github.v3+json"
    }

    # 找新兴项目：1000-30000 stars，创建于2024年后
    queries = [
        # 新兴高星（排除 freeCodeCamp/Linux/React 这类老牌巨型项目）
        "stars:1000..25000 created:>2024-01-01 pushed:>2026-03-01 fork:false -freeCodeCamp",
        # 中等星近期活跃（2025年后创建的）
        "stars:500..8000 created:>2025-01-01 pushed:>2026-04-01 fork:false",
    ]

    all_repos = []
    seen = set()

    for q in queries:
        encoded_q = urllib.parse.quote(q)
        url = f"https://api.github.com/search/repositories?q={encoded_q}&sort=stars&per_page=25"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                for item in data.get("items", []):
                    name = item["full_name"]
                    if name in seen:
                        continue
                    # 排除已知巨型项目
                    big_repos = ["freeCodeCamp", "EbookFoundation", "open-sauced", "sindresorhus",
                                 "facebook/react", "tensorflow/tensorflow", "torvalds/linux",
                                 "microsoft/vscode", "twbs/bootstrap", "TheAlgorithms",
                                 "avelino/awesome-go", "vinta/awesome-python"]
                    if any(b in name for b in big_repos):
                        continue
                    seen.add(name)
                    all_repos.append({
                        "name": name,
                        "description": item.get("description") or "",
                        "language": item.get("language") or "",
                        "stars": str(item.get("stargazers_count", 0)),
                        "today_stars": "",
                        "url": item.get("html_url", ""),
                    })
        except Exception as e:
            print(f"    API error: {e}", file=sys.stderr)

    all_repos.sort(key=lambda x: int(x.get("stars", "0").replace(",", "")), reverse=True)
    return all_repos


def scrape() -> list:
    """
    主抓取：
    1. 先抓 github.com/trending HTML 并解析
    2. 如果解析结果为空或<5条，用 API 备用
    """
    print("  抓取 GitHub Trending HTML...", file=sys.stderr)
    try:
        html = fetch_trending_html()
        results = parse_trending_html(html)
        if len(results) >= 5:
            print(f"  HTML 解析到 {len(results)} 个仓库", file=sys.stderr)
            return results
        else:
            print(f"  HTML 只解析到 {len(results)} 个（可能JS渲染），使用 API", file=sys.stderr)
    except Exception as e:
        print(f"  HTML 抓取失败: {e}，使用 API", file=sys.stderr)

    return fetch_via_github_api()


if __name__ == "__main__":
    results = scrape()
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
