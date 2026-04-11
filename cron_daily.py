#!/usr/bin/env python3
"""
Daily Report Orchestrator
运行 Q1 (HN) + Q2 (GitHub Trending) scrapers，生成报告，推送 GitHub
定时任务入口
"""

import base64
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = "ice45571/daily-report"
TOKEN = os.environ.get("GH_TOKEN", "")
WORKSPACE = "/Users/ice/.openclaw/workspace-xiaotantan"
MENTIONS_FILE = f"{WORKSPACE}/mentions/github-projects.json"
SHOWHN_MENTION_FILE = f"{WORKSPACE}/mentions/showhn-projects.json"


def load_mentions(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_mentions(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


PY39 = "/usr/bin/python3"


def run_scraper(path) -> list:
    """跑 scraper，GH scraper 用 Python 3.9（lxml）"""
    # GH scraper 需要 Python 3.9（有 lxml）
    python = PY39 if "gh_trending" in path else sys.executable
    result = subprocess.run(
        [python, path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=WORKSPACE
    )
    if result.returncode != 0:
        print(f"  scraper error: {result.stderr[:200]}", file=sys.stderr)
        return []
    try:
        data = json.loads(result.stdout)
        return data.get("results", [])
    except:
        print(f"  JSON parse error: {result.stdout[:200]}", file=sys.stderr)
        return []


def is_commercial_repo(repo_name) -> bool:
    """检查仓库是否商业化"""
    try:
        req = urllib.request.Request(
            f"https://github.com/{repo_name}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        commercial = ["this software is proprietary",
                     "commercial license required",
                     "not open source"]
        return any(p in html.lower() for p in commercial)
    except:
        return False


def analyze_github_project(repo):
    name = repo.get("name", "")
    desc = repo.get("description", "")
    language = repo.get("language", "")
    stars_str = repo.get("stars", "0")
    all_text = f"{desc} {name}".lower()

    # 产品类型
    if any(k in all_text for k in ["cli", "command", "terminal"]):
        ptype = "命令行工具"
    elif any(k in all_text for k in ["api", "sdk", "wrapper"]):
        ptype = "SDK / API 封装"
    elif any(k in all_text for k in ["web", "framework", "frontend", "dashboard"]):
        ptype = "Web 框架 / 前端"
    elif any(k in all_text for k in ["ai", "gpt", "llm", "claude", "openai", "agent"]):
        ptype = "AI 相关"
    elif any(k in all_text for k in ["database", "db", "sql", "storage"]):
        ptype = "数据库 / 存储"
    elif any(k in all_text for k in ["image", "video", "audio", "media"]):
        ptype = "多媒体处理"
    elif any(k in all_text for k in ["security", "auth", "crypto"]):
        ptype = "安全工具"
    elif any(k in all_text for k in ["devops", "docker", "kubernetes"]):
        ptype = "DevOps / 部署"
    elif language:
        ptype = f"{language} 项目"
    else:
        ptype = "工具 / 项目"

    # 为什么火
    try:
        stars = int(stars_str.replace(",", ""))
    except:
        stars = 0

    reasons = []
    if stars > 20000:
        reasons.append(f"极火（{stars_str} stars）")
    elif stars > 5000:
        reasons.append(f"较火（{stars_str} stars）")
    else:
        reasons.append(f"{stars_str} stars")

    if repo.get("today_stars"):
        reasons.append(f"今日 +{repo['today_stars']} stars")

    if any(k in all_text for k in ["simple", "easy", "lightweight", "minimal"]):
        reasons.append("强调简单轻量")
    if any(k in all_text for k in ["fast", "quick", "performance"]):
        reasons.append("强调性能")
    if any(k in all_text for k in ["open source", "free", "mit", "apache"]):
        reasons.append("宽松开源许可证")
    if any(k in all_text for k in ["beautiful", "design", "dark mode"]):
        reasons.append("颜值高")

    why_good = "；".join(reasons) if reasons else "建议直接看 README"

    # 启发
    insights = []
    if "ai" in ptype.lower():
        insights.append("AI 赛道热，但同质化严重，差异化要靠垂直场景")
    if "cli" in ptype.lower():
        insights.append("CLI 工具容易口碑传播，从自己痛点出发")
    if stars > 20000:
        insights.append("高分项目说明市场验证充分，但竞争可能已很激烈")

    opportunity = "；".join(insights) if insights else "暂无特定启发，建议直接使用感受"

    return {
        "type": ptype,
        "what": (desc or f"一个 {ptype}")[:100],
        "why_good": why_good,
        "opportunity": opportunity,
    }


def generate_markdown(hn_products, gh_projects, run_date):
    md = f"# 🔍 独立开发者情报日报\n\n"
    md += f"**日期**: {run_date}\n\n"

    # Q1
    md += "---\n\n## Q1: Show HN 首页 Solo Founder 产品\n\n"
    if not hn_products:
        md += "今日首页暂无 solo founder 产品。\n\n"
    else:
        for i, p in enumerate(sorted(hn_products, key=lambda x: x["points"], reverse=True), 1):
            md += f"### {i}. {p['title']}\n\n"
            md += f"⭐ **{p['points']}** 分 | 💬 {p['comments']} 条讨论 | @{p['author']}\n\n"
            md += f"🔗 [产品]({p['url']}) | [HN讨论]({p['hn_link']})\n\n"
            md += f"**这个产品是啥**：{p['what']}\n\n"
            md += f"**解决什么问题**：{p['problem']}\n\n"
            md += f"**为什么值得看**：{p['notable']}\n\n---\n\n"

    # Q2
    md += "\n## Q2: GitHub Trending 热门开源新项目\n\n"
    md += "_已去重：之前提过的项目今天不再出现_\n\n"
    if not gh_projects:
        md += "今日无新的未商业化开源项目。\n\n"
    else:
        for i, p in enumerate(sorted(gh_projects,
                                      key=lambda x: int(x.get("stars", "0").replace(",", "")),
                                      reverse=True), 1):
            a = p["analysis"]
            md += f"### {i}. [{p['name']}](https://github.com/{p['name']})\n\n"
            stars = p.get("stars", "?")
            today = f" | 今日 +{p['today_stars']} stars" if p.get("today_stars") else ""
            md += f"⭐ **{stars}** stars{today} | 语言: {p.get('language', '未识别')}\n\n"
            md += f"**这是啥**：{a['what']}\n\n"
            md += f"**类型**：{a['type']}\n\n"
            md += f"**为什么火**：{a['why_good']}\n\n"
            md += f"**对开发者的启发**：{a['opportunity']}\n\n"
            if p.get("description"):
                md += f"> {p['description'][:150]}\n\n"
            md += "---\n\n"

    # 综合洞察
    md += "## 📊 今日综合洞察\n\n"
    if hn_products:
        top = max(hn_products, key=lambda x: x["points"])
        md += f"**Show HN 今日最爆**：[{top['title']}]({top['url']}) — {top['points']}分\n"
        md += f"- {top['what']}\n"
        md += f"- {top['notable']}\n\n"
    if gh_projects:
        top_gh = gh_projects[0]
        md += f"**GitHub 今日最热**：[{top_gh['name']}]"
        md += f"(https://github.com/{top_gh['name']}) — {top_gh.get('stars','?')}stars\n"
        md += f"- {top_gh['analysis']['what']}\n"
        md += f"- {top_gh['analysis']['why_good']}\n\n"
    if hn_products or gh_projects:
        md += "**💡 值得关注的共同点**\n"
        md += "1. 解决真实痛点的产品分数最高——概念类产品很难爆\n"
        md += "2. 「从零造」+ 「自己做」的故事天然带传播力\n"
        md += "3. 开源工具 + 清晰 README = 最低成本的传播组合\n"
        md += "4. GitHub Trending 代表当前技术圈的关注方向\n\n"

    return md


def github_api_put(path, content, sha=None):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    data = {
        "message": f"Daily Report - {datetime.now().strftime('%Y-%m-%d')}",
        "content": base64.b64encode(content.encode()).decode(),
    }
    if sha:
        data["sha"] = sha
    body = json.dumps(data).encode()
    headers = {"Authorization": f"Bearer {TOKEN}",
               "Content-Type": "application/json",
               "User-Agent": "daily-report-cron"}
    req = urllib.request.Request(url, data=body, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except Exception as e:
        print(f"  push error: {e}", file=sys.stderr)
        return None


def get_file_sha(path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    headers = {"User-Agent": "daily-report-cron"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read()).get("sha")
    except:
        return None


def main():
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"[{run_date}] 开始抓取...", flush=True, file=sys.stderr)

    # Q1
    print("Q1: Show HN...", flush=True, file=sys.stderr)
    hn_products = run_scraper(f"{WORKSPACE}/scraper_hn.py")
    print(f"  获取 {len(hn_products)} 个 solo founder 产品", flush=True, file=sys.stderr)

    # 记录 HN mentions
    showhn_mentions = load_mentions(SHOWHN_MENTION_FILE)
    for p in hn_products:
        showhn_mentions[p["title"]] = {
            "first_mentioned": today_str,
            "points": p["points"],
        }
    save_mentions(SHOWHN_MENTION_FILE, showhn_mentions)

    # Q2
    print("Q2: GitHub Trending...", flush=True, file=sys.stderr)
    mentions = load_mentions(MENTIONS_FILE)
    raw_repos = run_scraper(f"{WORKSPACE}/scraper_gh_trending.py")
    print(f"  获取 {len(raw_repos)} 个候选仓库", flush=True, file=sys.stderr)

    # 去重
    new_repos = [r for r in raw_repos if r["name"] not in mentions]
    print(f"  去重后 {len(new_repos)} 个新项目", flush=True, file=sys.stderr)

    # 过滤商业化（串行检查，慢一点但稳定）
    filtered = []
    for r in new_repos:
        if is_commercial_repo(r["name"]):
            continue
        filtered.append(r)
    print(f"  过滤商业化后剩余 {len(filtered)} 个", flush=True, file=sys.stderr)

    # 分析
    gh_projects = []
    for repo in filtered:
        repo["analysis"] = analyze_github_project(repo)
        gh_projects.append(repo)
        mentions[repo["name"]] = {
            "first_mentioned": today_str,
            "stars": repo.get("stars", ""),
            "type": repo["analysis"]["type"],
        }
    save_mentions(MENTIONS_FILE, mentions)

    # 报告
    md = generate_markdown(hn_products, gh_projects, run_date)
    date_str = today_str
    filename = f"showhn-solo-{date_str}.md"

    sha = get_file_sha(filename)
    status = github_api_put(filename, md, sha)
    print(f"{'✅' if status in (200, 201) else '❌'} 推送: {filename}", file=sys.stderr)

    readme = f"# 独立开发者情报日报\n\n每日自动更新\n\n[查看今日报告](showhn-solo-{date_str}.md)\n"
    github_api_put("README.md", readme, get_file_sha("README.md"))

    print(md)


if __name__ == "__main__":
    main()
