---
paths:
  - "index.html"
---

# Bento 卡片结构约定

新增/修改首页工具卡片时必须遵守：

## DOM 结构
`.bento-card`（放进对应 `.bento-category` 下的 `.bento-grid`）：
- 可选 `.bento-thumb-link`（`<a>` 包 `<img>`，3:2 比例，`object-fit:cover`）+ `.bento-caption`——**只有工具真的有配图才加**，没有就整段跳过，不要留空占位
- `.bento-body` 内含：`<h3 class="bento-title">`（emoji + 名称）→ `.cta-btn` 链接到工具 → `<details class="bento-details"><summary>Mehr erfahren · Learn more</summary>...</details>` 包住完整的双语（DE+EN）描述/使用说明
- 标题层级：卡片标题必须是 `<h3>`（分类标题是 `<h2>`，页面标题是 `<h1>`）——之前出过嵌套层级错误的 bug

## 分类顺序（用户明确要求的固定顺序，不要改）
1. Featured Mini Tools（AI Resume Builder 在左，Zodiac & Stars 在右）
2. Everyday & Productivity Tools
3. Travel Tools
4. Watch Tools
5. Blog（永远最后）

每个 `<h2 class="category-heading">` 是三语：`emoji DE文本 · EN文本 · 中文` 一行内写完
（例：`🗺️ Reise-Tools · Travel Tools · 旅行工具`）。

## 卡片标题语言
卡片标题的语言组合要匹配**被链接工具本身实际支持的语言**，不是固定公式——
比如 countdown-timer-app 自己的 UI 只有英德双语，它的卡片标题就只写 DE/EN，不强行加中文。
只有页面级的分类标题（`.category-heading`）是无条件三语。

## 高度对齐（已踩过的坑，别重新踩）
- `.bento-grid` 用默认 `stretch`，不要加 `align-items:start`
- `details.bento-details` 用 `margin-top:auto` 让"Mehr erfahren"锚定到卡片底部，行高自动对齐
- 例外：如果某张卡片重新变成没有配图的状态，图片对齐 bug 会复现——要么给它补图，要么给那一行单独加回 `align-items:start`

## 图片来源
- 来自 Unsplash（免授权费，无需署名），下载前必须先视觉确认（截图或用 Read 工具查看图片本身），
  不要只信 WebFetch 对图片的文字描述——曾把社交图标网格描述成"彩色骰子"
- 下载任何图片前需要用户明确同意（文件名/来源/大小）
