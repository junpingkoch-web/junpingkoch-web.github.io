#!/usr/bin/env python3
"""Regenerate this repo's sitemap.xml for the whole junpingkoch-web portfolio.

This is NOT a single-repo directory walk. Each tool in the portfolio is its own
git repo (see ~/.claude/skills/web-tool-scaffold and the ecosystem memory) deployed
as its own GitHub Pages project page. Per robots.txt at the true domain root, this
repo's sitemap.xml is the ONLY sitemap that matters for those tool pages - every
sibling repo's own local sitemap.xml is unreferenced and effectively dead.
watch-guide-blog is the one exception: it's a Hugo site with its own separately
generated sitemap.xml (also declared in robots.txt), so only its home page is
listed here - its posts are NOT walked into this file.

Run from this repo's root:  python generate_sitemap.py
"""
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

BASE_URL = "https://junpingkoch-web.github.io/"
ROOT_REPO = Path(__file__).resolve().parent
SIBLINGS_DIR = ROOT_REPO.parent  # Desktop

# Sibling tool repos: (local path, priority, changefreq). The deployed URL slug is
# read from `git remote get-url origin`, NOT the folder name - watch-valuator's
# folder deploys under the slug "Secondhand-Watch-Valuator", confirmed 2026-09-02.
SIBLING_REPOS = [
    (SIBLINGS_DIR / "ai-resume-builder", "0.8", "weekly"),
    (SIBLINGS_DIR / "alpine-route-planner", "0.8", "weekly"),
    (SIBLINGS_DIR / "Europe-Travel-Watch-Duty-Free-Calculator", "0.8", "weekly"),
    (SIBLINGS_DIR / "random-grouping-website", "0.8", "weekly"),
    (SIBLINGS_DIR / "swiss-city-guide", "0.8", "weekly"),
    (SIBLINGS_DIR / "timezone-planner", "0.8", "weekly"),
    (SIBLINGS_DIR / "watch-price-tracker", "0.8", "weekly"),
    (SIBLINGS_DIR / "watch-valuator", "0.8", "weekly"),
    (SIBLINGS_DIR / "zodiac-stars", "0.8", "weekly"),
    (Path(r"C:\Users\junpi\My Project\countdown-timer-app"), "0.8", "weekly"),
    # swiss-boarding-schools intentionally excluded: no .git / not pushed yet as of
    # 2026-09-02 (see ecosystem memory 2026-08-21 entry) - would 404 if listed here.
    # Add it once it's actually live on GitHub Pages.
]

# Sub-pages inside a sibling repo that deserve their own sitemap entry, keyed by the
# repo's local folder name. Only added if the sub-page's own index.html actually
# exists on disk - never guessed.
SUB_PAGES = {
    "countdown-timer-app": [
        ("christmas-countdown", "0.6", "monthly"),
        ("pomodoro", "0.6", "monthly"),
    ],
}

# watch-guide-blog: Hugo site, has its own generated sitemap - only list its home page.
WATCH_GUIDE_BLOG = ("watch-guide-blog", "0.9", "weekly")

# This repo's own static pages.
ROOT_PAGES = [
    ("", "1.0", "weekly"),
    ("about.html", "0.5", "monthly"),
    ("tech-sales.html", "0.6", "monthly"),
    ("contact.html", "0.5", "monthly"),
    ("privacy.html", "0.3", "monthly"),
    ("terms.html", "0.3", "monthly"),
    ("impressum.html", "0.3", "monthly"),
]


def git_slug(repo_path: Path):
    """Deployed GitHub Pages slug for a sibling repo, from its real git remote."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"WARNING: {repo_path} has no git remote / isn't pushed yet - skipping", file=sys.stderr)
        return None
    url = result.stdout.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[: -len(".git")]
    return url.rsplit("/", 1)[-1]


def main():
    entries = []  # (loc, priority, changefreq)

    for path, priority, changefreq in ROOT_PAGES:
        entries.append((BASE_URL + path, priority, changefreq))

    entries.append((BASE_URL + WATCH_GUIDE_BLOG[0] + "/", WATCH_GUIDE_BLOG[1], WATCH_GUIDE_BLOG[2]))

    for repo_path, priority, changefreq in SIBLING_REPOS:
        if not repo_path.is_dir():
            print(f"WARNING: {repo_path} not found on disk - skipping", file=sys.stderr)
            continue
        slug = git_slug(repo_path)
        if slug is None:
            continue
        entries.append((BASE_URL + slug + "/", priority, changefreq))

        for sub, sub_priority, sub_changefreq in SUB_PAGES.get(repo_path.name, []):
            if (repo_path / sub / "index.html").is_file():
                entries.append((BASE_URL + slug + "/" + sub + "/", sub_priority, sub_changefreq))
            else:
                print(f"WARNING: expected sub-page {repo_path / sub} not found - skipping", file=sys.stderr)

    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, priority, changefreq in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    out_path = ROOT_REPO / "sitemap.xml"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} URLs to {out_path}")


if __name__ == "__main__":
    main()
