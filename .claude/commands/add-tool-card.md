---
description: Add a new sibling tool's card to the homepage bento grid
argument-hint: [tool name and one-line description]
---

Add a bento card for: $ARGUMENTS

Before writing anything, confirm the sibling tool's repo already exists and is published at `https://junpingkoch-web.github.io/<repo-name>/` — don't add a card for a tool that isn't live yet.

Follow the structure in `.claude/rules/bento-card-structure.md` exactly: correct category section (ask which of the 5 fixed categories it belongs in if not obvious), `<h3>` title level, `.cta-btn` link, collapsible bilingual `<details>` description, and an image only if you have one (Unsplash, visually confirmed, user-approved download — never invent a placeholder image).

After adding the card, check row alignment isn't broken (see the height-alignment note in the rules file) and update the total card count if it's referenced anywhere.
