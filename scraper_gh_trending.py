#!/usr/bin/python3
"""
Q2: GitHub Trending Scraper
用 curl 抓取 github.com/trending HTML，解析真实 Trending 数据
"""

import json
import re
import subprocess
import sys


def fetch_trending_html() -> str:
    """用 curl 抓取 github.com/trending HTML"""
    cmd = [
        "curl", "-s", "-L",
        "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", "Accept: text/html",
        "-H", "Accept-Language: en-US,en;q=0.9",
        "--max-time", "15",
        "https://github.com/trending"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def parse_trending(html: str) -> list:
    """解析 GitHub Trending HTML"""
    results = []

    # 找到所有 article Box-row 块
    article_blocks = re.findall(r'<article class="Box-row">(.*?)</article>', html, re.DOTALL)
    print(f"  找到 {len(article_blocks)} 个 article", file=sys.stderr)

    for block in article_blocks:
        # 找真正的 repo 链接（排除 login redirect）
        # 格式: <a href="/owner/repo"> 其中 owner/repo 是真实的仓库名
        repo_match = re.search(r'<h2[^>]*>\s*<a[^>]+href="(/[^/]+/[^"]+)"[^>]*>\s*<svg[^>]*octicon-repo', block)
        if not repo_match:
            # 备选：直接找 /owner/repo 格式，排除 login?return
            repo_links = re.findall(r'href="(/[^/]+/[^"?]+)"', block)
            repo_name = None
            for link in repo_links:
                if "/login" in link or "return_to" in link:
                    continue
                if re.match(r'^/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.\-]+$', link):
                    repo_name = link.strip("/")
                    break
            if not repo_name:
                continue
        else:
            repo_name = repo_match.group(1).strip("/")

        # 描述：在 color-fg-muted 的 p 标签里
        desc_matches = re.findall(r'<p[^>]*class="[^"]*color-fg-muted[^"]*"[^>]*>(.*?)</p>', block, re.DOTALL)
        desc = ""
        for m in desc_matches:
            text = re.sub(r'<[^>]+>', '', m).strip()
            if text:
                desc = text
                break

        # 编程语言
        lang_match = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>([^<]+)<', block)
        language = lang_match.group(1).strip() if lang_match else ""

        # Star 总数：在 stargazers 链接里
        star_match = re.search(r'<a[^>]+href="/[^/]+/[^/]+/stargazers"[^>]*>.*?([\d,]+)</a>', block, re.DOTALL)
        stars_str = star_match.group(1) if star_match else ""

        # 今日新增 stars：plain text "X stars today"
        today_match = re.search(r'([\d,]+)\s+stars\s+today', block)
        today_stars = today_match.group(1) if today_match else ""

        results.append({
            "name": repo_name,
            "description": desc[:200],
            "language": language,
            "stars": stars_str,
            "today_stars": today_stars,
            "url": f"https://github.com/{repo_name}",
        })

    return results


def scrape() -> list:
    """主抓取流程"""
    print("  用 curl 抓取 GitHub Trending...", file=sys.stderr)
    try:
        html = fetch_trending_html()
        if not html or len(html) < 1000:
            print("  HTML 太短，可能抓取失败", file=sys.stderr)
            return []
        results = parse_trending(html)
        print(f"  解析到 {len(results)} 个仓库", file=sys.stderr)
        return results
    except Exception as e:
        print(f"  抓取失败: {e}", file=sys.stderr)
        return []


if __name__ == "__main__":
    results = scrape()
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
