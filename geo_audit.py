#!/usr/bin/env python3
"""GEO / technical-SEO health dashboard for the junpingkoch-web portfolio.

Generates a self-contained static HTML report (geo_audit_dashboard.html) -
no local server, no backend, open it by double-clicking, same zero-build
convention as the rest of this portfolio. To re-check after a fix: rerun
this script and reload the file - there's no in-page "re-verify" button,
since that would need a live backend this portfolio deliberately doesn't
have anywhere else either.

Checks the LIVE domain (not local files) via curl-equivalent HTTP requests,
because that's what actually matters for AI crawlers/Googlebot - a fix only
counts once it's pushed and deployed. Reuses the same repo list as
generate_sitemap.py / check_dead_links.py (each script keeps its own copy
by this portfolio's existing convention, not a shared import).

Run:  python geo_audit.py   (no extra dependencies - stdlib only)
"""
import json
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://junpingkoch-web.github.io"
DESKTOP = Path(r"C:\Users\junpi\Desktop")
MY_PROJECT = Path(r"C:\Users\junpi\My Project")
ROOT_REPO = Path(__file__).resolve().parent

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; junpingkoch-web geo_audit.py)"}

# (slug or "" for homepage, local repo path or None if not applicable, is a
# "tool" page expected to carry FAQPage+WebApplication JSON-LD)
PAGES = [
    ("", ROOT_REPO, False),
    ("about.html", ROOT_REPO, False),
    ("tech-sales.html", ROOT_REPO, False),
    ("contact.html", ROOT_REPO, False),
    ("privacy.html", ROOT_REPO, False),
    ("terms.html", ROOT_REPO, False),
    ("impressum.html", ROOT_REPO, False),
    ("watch-guide-blog/", DESKTOP / "watch-guide-blog", False),
]

SIBLING_REPOS = [
    DESKTOP / "ai-resume-builder",
    DESKTOP / "alpine-route-planner",
    DESKTOP / "Europe-Travel-Watch-Duty-Free-Calculator",
    DESKTOP / "random-grouping-website",
    DESKTOP / "swiss-city-guide",
    DESKTOP / "timezone-planner",
    DESKTOP / "watch-price-tracker",
    DESKTOP / "watch-valuator",
    DESKTOP / "zodiac-stars",
    MY_PROJECT / "countdown-timer-app",
]

AI_CRAWLER_UAS = ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended"]

LEGAL_PAGES = ["privacy.html", "impressum.html", "contact.html", "terms.html"]


def git_slug(repo_path: Path):
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    url = result.stdout.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[: -len(".git")]
    return url.rsplit("/", 1)[-1]


def fetch(url, timeout=10):
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers=HEADERS, method="GET")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, str(e)


def cjk_width(s):
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)


def check_page(slug, expected_loc, is_tool, results):
    status, html = fetch(expected_loc)
    label = expected_loc

    if status != 200:
        results["critical"].append({
            "title": f"页面不可访问: {label}",
            "detail": f"HTTP {status}，无法继续检查这个页面的其他项目",
        })
        return

    # Attribute values are optionally quoted: Hugo's minifier strips quotes from
    # any attribute whose value has no spaces (name=description, href=<url-with-
    # no-spaces>), but keeps them when the value has spaces (content="a b c").
    # Matching only the quoted form produced false positives against the Hugo
    # blog earlier - both patterns below accept quoted or unquoted values.
    canon = re.search(r'rel=["\']?canonical["\']?\s+href=(?:"([^"]+)"|\'([^\']+)\'|([^\s>]+))', html, re.I)
    if not canon:
        results["high"].append({"title": f"缺少 canonical 标签: {label}", "detail": "页面 <head> 里没有找到 rel=\"canonical\""})
    else:
        canon_url = canon.group(1) or canon.group(2) or canon.group(3)
        if canon_url != expected_loc:
            results["high"].append({
                "title": f"canonical 不一致: {label}",
                "detail": f"页面自称 canonical 是 {canon_url}，跟它实际的访问地址不一致",
            })

    desc = re.search(r'name=["\']?description["\']?\s+content=(?:"([^"]*)"|\'([^\']*)\'|([^\s>]*))', html, re.I)
    if not desc:
        results["medium"].append({"title": f"缺少 meta description: {label}", "detail": ""})
    else:
        desc_content = desc.group(1) or desc.group(2) or desc.group(3) or ""
        w = cjk_width(desc_content)
        if w > 155:
            results["medium"].append({
                "title": f"meta description 过长: {label}",
                "detail": f"宽度计分 {w}（阈值 ~155），SERP 里大概率被截断",
            })

    if is_tool:
        if '"@type": "FAQPage"' not in html and '"@type":"FAQPage"' not in html:
            results["high"].append({"title": f"缺少 FAQPage 结构化数据: {label}", "detail": ""})
        if '"@type": "WebApplication"' not in html and '"@type":"WebApplication"' not in html:
            results["high"].append({"title": f"缺少 WebApplication 结构化数据: {label}", "detail": ""})


def main():
    results = {"critical": [], "high": [], "medium": [], "low": []}

    # --- robots.txt ---
    status, robots_txt = fetch(f"{BASE_URL}/robots.txt")
    if status != 200:
        results["critical"].append({"title": "robots.txt 不可访问", "detail": f"HTTP {status}"})
    else:
        if re.search(r"User-agent:\s*\*\s*\n\s*Disallow:\s*/\s*(\n|$)", robots_txt):
            results["critical"].append({"title": "robots.txt 屏蔽了全站", "detail": "User-agent: * 下有 Disallow: /，AI 爬虫和 Googlebot 都进不来"})
        for ua in AI_CRAWLER_UAS:
            block = re.search(rf"User-agent:\s*{ua}\b.*?(?=User-agent:|\Z)", robots_txt, re.S | re.I)
            if block and re.search(r"Disallow:\s*/\s*(\n|$)", block.group(0)):
                results["critical"].append({"title": f"robots.txt 单独屏蔽了 {ua}", "detail": "这个 AI 爬虫被明确 Disallow: / 了"})
        results["low"].append({"title": "robots.txt AI 爬虫放行检查", "detail": f"没有对 {', '.join(AI_CRAWLER_UAS)} 的显式屏蔽（隐式跟随 User-agent: * 的规则）", "pass": True})

    # --- sitemap.xml ---
    status, sitemap_xml = fetch(f"{BASE_URL}/sitemap.xml")
    if status != 200:
        results["critical"].append({"title": "sitemap.xml 不可访问", "detail": f"HTTP {status}"})
    else:
        import xml.dom.minidom as minidom
        try:
            minidom.parseString(sitemap_xml)
            results["low"].append({"title": "sitemap.xml 格式校验", "detail": "XML 合法", "pass": True})
        except Exception as e:
            results["critical"].append({"title": "sitemap.xml 格式错误", "detail": str(e)})

    # --- root pages + blog home ---
    for path, _, is_tool in PAGES:
        check_page(path, BASE_URL + "/" + path, is_tool, results)

    # --- sibling tool pages ---
    for repo_path in SIBLING_REPOS:
        if not repo_path.is_dir():
            results["medium"].append({"title": f"仓库不存在于本地: {repo_path}", "detail": "跳过"})
            continue
        slug = git_slug(repo_path)
        if not slug:
            results["medium"].append({"title": f"无法解析 git remote: {repo_path}", "detail": "跳过"})
            continue
        check_page(slug, f"{BASE_URL}/{slug}/", True, results)

    # --- legal pages reachable (already covered above for root, this is a summary check) ---
    all_ok = all(fetch(f"{BASE_URL}/{p}")[0] == 200 for p in LEGAL_PAGES)
    results["low"].append({"title": "法律合规页面（Privacy/Impressum/Contact/Terms）全部可访问", "detail": "", "pass": all_ok})
    if not all_ok:
        results["critical"].append({"title": "至少一个法律合规页面不可访问", "detail": "见上面各页面的检查结果"})

    return results


SEVERITY_META = {
    "critical": ("🚨 Critical", "#c0392b"),
    "high": ("⚠️ High", "#d68910"),
    "medium": ("🟡 Medium", "#b7950b"),
    "low": ("ℹ️ Low / Info", "#2874a6"),
}


def render_html(results, generated_at):
    total_issues = sum(len(v) for k, v in results.items() if k != "low") + \
        sum(1 for item in results["low"] if not item.get("pass"))
    sections = []
    for key in ["critical", "high", "medium", "low"]:
        label, color = SEVERITY_META[key]
        items = results[key]
        if not items:
            continue
        rows = []
        for item in items:
            passed = item.get("pass")
            icon = "✅" if passed else ("ℹ️" if key == "low" else "❌")
            detail = f"<div class='detail'>{item['detail']}</div>" if item.get("detail") else ""
            rows.append(f"<li>{icon} <strong>{item['title']}</strong>{detail}</li>")
        sections.append(f"""
        <section>
          <h2 style="color:{color}">{label} ({len(items)})</h2>
          <ul>{''.join(rows)}</ul>
        </section>""")

    return f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8">
<title>junpingkoch-web GEO 健康看板</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", "PingFang SC", sans-serif; max-width: 900px; margin: 0 auto; padding: 32px 20px; background:#f5f6f7; color:#1a1e24; }}
  h1 {{ font-size: 22px; }}
  .meta {{ color:#666; font-size:13px; margin-bottom:24px; }}
  section {{ background:#fff; border-radius:10px; padding:18px 22px; margin-bottom:18px; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
  h2 {{ font-size:16px; margin:0 0 10px; }}
  ul {{ margin:0; padding-left:22px; }}
  li {{ margin-bottom:10px; line-height:1.5; }}
  .detail {{ color:#666; font-size:13px; margin-top:2px; }}
  .summary {{ font-size:15px; margin-bottom:20px; padding:14px 18px; border-radius:8px; background:#fff; }}
</style></head>
<body>
<h1>junpingkoch-web 全站 GEO / 技术 SEO 健康看板</h1>
<div class="meta">生成时间: {generated_at}　|　检查范围: 域名 root + 10 个工具仓库 + watch-guide-blog 首页</div>
<div class="summary">{'🎉 没有发现需要处理的问题' if total_issues == 0 else f'⚠️ 共发现 {total_issues} 处需要处理的问题（不含下面标 ✅ 的通过项）'}</div>
{''.join(sections)}
<p style="color:#999; font-size:12px; margin-top:30px;">复查方式：改完问题后重新运行 <code>python geo_audit.py</code>，刷新这个文件即可看到最新结果——这是一个纯静态生成的报告，没有后台服务，不支持页面内一键重新检测。</p>
</body></html>"""


if __name__ == "__main__":
    generated_at = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    results = main()
    html = render_html(results, generated_at)
    out = ROOT_REPO / "geo_audit_dashboard.html"
    out.write_text(html, encoding="utf-8")
    total = sum(len(v) for k, v in results.items() if k != "low") + sum(1 for i in results["low"] if not i.get("pass"))
    print(f"Wrote {out} - {total} issues found (see file for detail; low-severity pass/info items not counted)")
