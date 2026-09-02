#!/usr/bin/env python3
"""Dead-link / missing-image check across the whole junpingkoch-web portfolio.

Requires beautifulsoup4 (`pip install beautifulsoup4`). Run from anywhere - paths
below are absolute, this doesn't need to run from inside this repo:
    python check_dead_links.py
On Windows, run with PYTHONUTF8=1 if the console errors on the Chinese output
(cp1252 can't encode it): `PYTHONUTF8=1 python check_dead_links.py`. Writes
dead_links_report.md next to this script.

Adapted from a pasted check_dead_links.py / -v2.py: those assume a single-repo
os.walk(".") - correct for the AdSense/Screaming Frog style "point at one domain"
check, but wrong for local scanning here, since the portfolio is ~11 separate git
repos in separate folders, not subdirectories of one site. This version walks each
repo separately and resolves relative links within that repo's own directory.

Also fixes a real bug in the pasted v1 script (check_dead_links.py): its
`if __name__ == "__main__": check_links()` calls an undefined function name -
the function is `check_dead_links()`. v2 already fixes this; use v2 as the base
regardless.

One more correction the pasted scripts don't make: a root-relative link
("/images/foo.png") written inside a SIBLING tool repo does NOT resolve to that
repo's own local images/ folder - each sibling deploys under a GitHub Pages
project sub-path (.../<repo>/), so "/images/foo.png" in its HTML actually points
at the DOMAIN root's images/ folder in production. Only the root portfolio repo
(deployed at the true domain root) can resolve a root-relative link locally.
Sibling repos' root-relative links are instead resolved against the live domain
and checked as external URLs.

External links are deduplicated across the ENTIRE portfolio before checking -
the same footer/social links repeat on nearly every page across ~11 repos, and
checking each occurrence separately would multiply requests ~10x for no benefit.

Caveat printed with the report: an external check failure can mean the link is
genuinely dead, OR that the target site blocks HEAD/bot-like requests (LinkedIn
and some ad-tooling domains are known to do this) - treat failures as "needs a
manual look in a real browser," not as confirmed dead links.
"""
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://junpingkoch-web.github.io"
DESKTOP = Path(r"C:\Users\junpi\Desktop")
MY_PROJECT = Path(r"C:\Users\junpi\My Project")

# (name, path, deployed_at_domain_root)
REPOS = [
    ("junpingkoch-web.github.io", DESKTOP / "junpingkoch-web.github.io", True),
    ("ai-resume-builder", DESKTOP / "ai-resume-builder", False),
    ("alpine-route-planner", DESKTOP / "alpine-route-planner", False),
    ("Europe-Travel-Watch-Duty-Free-Calculator", DESKTOP / "Europe-Travel-Watch-Duty-Free-Calculator", False),
    ("random-grouping-website", DESKTOP / "random-grouping-website", False),
    ("swiss-city-guide", DESKTOP / "swiss-city-guide", False),
    ("timezone-planner", DESKTOP / "timezone-planner", False),
    ("watch-price-tracker", DESKTOP / "watch-price-tracker", False),
    ("watch-valuator", DESKTOP / "watch-valuator", False),
    ("zodiac-stars", DESKTOP / "zodiac-stars", False),
    ("countdown-timer-app", MY_PROJECT / "countdown-timer-app", False),
    # watch-guide-blog intentionally excluded: Hugo site, source is markdown not
    # HTML - checking it needs a built `public/` output, different workflow.
]

EXCLUDE_DIRS = {".git", "node_modules", ".venv", "dist", "build"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def is_external(url):
    return url.startswith("http://") or url.startswith("https://")


def check_external_url(url, timeout=6):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status < 400
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):
            try:
                req = urllib.request.Request(url, headers=HEADERS, method="GET")
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                    return resp.status < 400
            except Exception:
                return False
        return False
    except Exception:
        return False


def resolve_local(file_dir: Path, repo_root: Path, link: str, at_domain_root: bool):
    """Resolve a relative link within its own repo. Root-relative ("/...") links
    are NEVER resolved against a local repo folder, not even the root repo's -
    even the root repo's own HTML links to sibling repos via root-relative paths
    (e.g. "/ai-resume-builder/"), which only exist on the live multi-repo domain,
    not as a local subfolder of any single repo. Only the live domain is
    authoritative for what "/" resolves to, so every root-relative link is
    deferred to the external HTTP check instead."""
    clean = link.split("#")[0].split("?")[0]
    if not clean:
        return None  # pure anchor, nothing to check
    if clean.startswith("/"):
        return "EXTERNAL"
    target = (file_dir / clean).resolve()
    if target.is_dir():
        target = target / "index.html"
    return target


def main():
    local_dead = []  # (repo, rel_file, link, link_type, reason)
    external_refs = {}  # url -> list[(repo, rel_file, link_type)]
    scanned_files = 0

    for repo_name, repo_root, at_domain_root in REPOS:
        if not repo_root.is_dir():
            print(f"WARNING: {repo_root} not found - skipping {repo_name}")
            continue
        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for fname in files:
                if not fname.endswith(".html"):
                    continue
                scanned_files += 1
                file_path = Path(root) / fname
                rel_file = f"{repo_name}/{file_path.relative_to(repo_root).as_posix()}"
                try:
                    soup = BeautifulSoup(file_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
                except Exception as e:
                    print(f"WARNING: failed to parse {rel_file}: {e}")
                    continue

                targets = [(t["href"].strip(), "<a href>") for t in soup.find_all("a", href=True)]
                targets += [(t["src"].strip(), "<img src>") for t in soup.find_all("img", src=True)]

                for link, ltype in targets:
                    if not link or link.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                        continue
                    if is_external(link):
                        external_refs.setdefault(link, []).append((repo_name, rel_file, ltype))
                        continue
                    resolved = resolve_local(file_path.parent, repo_root, link, at_domain_root)
                    if resolved is None:
                        continue
                    if resolved == "EXTERNAL":
                        full_url = BASE_URL + link.split("#")[0].split("?")[0]
                        external_refs.setdefault(full_url, []).append(
                            (repo_name, rel_file, ltype + " (root-relative, resolves to domain root)")
                        )
                        continue
                    if not resolved.exists():
                        local_dead.append((repo_name, rel_file, link, ltype, "本地文件不存在"))

    print(f"扫描完成：{len(REPOS)} 个仓库，{scanned_files} 个 HTML 文件")
    print(f"本地相对链接/图片死链：{len(local_dead)} 处")
    for repo, rel_file, link, ltype, reason in local_dead:
        print(f"  [LOCAL] {rel_file}  ->  {link}  [{ltype}] {reason}")

    print(f"\n去重后的外部链接总数：{len(external_refs)}（跨全站只各检查一次）")
    print("正在检查外部链接（可能需要几分钟）...")
    external_dead = []
    for i, (url, refs) in enumerate(sorted(external_refs.items()), 1):
        ok = check_external_url(url)
        if not ok:
            external_dead.append((url, refs))
        if i % 20 == 0:
            print(f"  ...已检查 {i}/{len(external_refs)}")

    print(f"\n外部链接疑似失效：{len(external_dead)} 处（可能包含反爬拦截的误报，见下方提醒）")
    for url, refs in external_dead:
        print(f"  [EXTERNAL?] {url}")
        for repo, rel_file, ltype in refs[:3]:
            print(f"       引用自: {rel_file} [{ltype}]")
        if len(refs) > 3:
            print(f"       ...以及另外 {len(refs) - 3} 处引用")

    report = ["# 全站死链排查报告\n",
              f"扫描 {len(REPOS)} 个仓库、{scanned_files} 个 HTML 文件。\n",
              f"## 本地死链（{len(local_dead)} 处，可信度高，建议直接修）\n",
              "| 仓库/文件 | 链接 | 类型 | 原因 |", "|---|---|---|---|"]
    for repo, rel_file, link, ltype, reason in local_dead:
        report.append(f"| `{rel_file}` | `{link}` | {ltype} | {reason} |")
    report.append(f"\n## 外部链接疑似失效（{len(external_dead)} 处，"
                   "需要人工在浏览器里确认，很多网站会拦截自动化请求返回假阳性）\n")
    report.append("| URL | 引用来源（最多列3处） |")
    report.append("|---|---|")
    for url, refs in external_dead:
        ref_str = "; ".join(r[1] for r in refs[:3])
        report.append(f"| `{url}` | {ref_str} |")

    out_path = Path(__file__).parent / "dead_links_report.md"
    out_path.write_text("\n".join(report), encoding="utf-8")
    print(f"\n详细报告已保存: {out_path}")


if __name__ == "__main__":
    main()
