---
description: Read-only technical SEO audit of this site — meta tags, headings, alt text, sitemap/robots, internal links
---

Audit this site for technical SEO issues. Check:
1. `<title>` and meta description are present and a reasonable length (title ~50-60 chars, description ~120-160 chars) on the main page(s)
2. Exactly one `<h1>` per page, and a sensible H2/H3 hierarchy under it
3. Every `<img>` has a non-empty `alt` attribute
4. `robots.txt` and `sitemap.xml` exist and are internally consistent — the sitemap URL referenced in `robots.txt` actually resolves, and the URLs listed in `sitemap.xml` match the site's real deployed paths
5. Internal links (`href="..."` pointing at this site or sibling tools) don't reference files/paths that don't exist
6. Any JSON-LD (`<script type="application/ld+json">`) is syntactically valid JSON

Report findings as a prioritized list (broken > missing > suboptimal), each with the file and line number. Don't fix anything automatically — report first, let me decide what to act on.
