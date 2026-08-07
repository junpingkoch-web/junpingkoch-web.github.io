# Project: junpingkoch-web.github.io（个人作品集主站）

个人作品集首页，以 bento 卡片网格展示并链接到一系列小型免费网页工具（各自独立仓库），
通过 GitHub Pages 部署。零构建静态站点：没有 npm/构建/测试命令。

## Commands
- 本地预览：无独立命令，用共享的 dev-server 配置（见下方"预览"章节）
- 部署：改完直接 `git push`，GitHub Pages 自动重新发布，没有构建步骤

## 文件结构
- `index.html` — 首页，bento 卡片网格
- `about.html` / `contact.html` / `privacy.html` / `terms.html` — 信任页
- `images/` — 卡片配图（来自 Unsplash，免授权费）
- `ads.txt` — 真实 AdSense publisher 行，可直接复用，不是占位符
- `sitemap.xml`

## 首页 Bento 卡片约定
详细结构规则见 `.claude/rules/bento-card-structure.md`（按路径作用域只在改 `index.html` 时加载）。

## 预览
本地预览服务器配置在**共享文件** `C:\Users\junpi\.claude\.claude\launch.json` 里
（每个 sibling 仓库一个 Python `http.server` 配置块，端口从 5500 递增），
不是这个仓库自己的 `.claude/launch.json`——加新配置要改共享文件。

## 部署流程
1. 改完直接 commit + push 到 `main`
2. GitHub Pages 自动重新发布，无需手动触发
3. Commit 作者身份用 `Junping Koch <junping.koch@gmail.com>`——这是每个仓库单独设置的，不是全局 git config

## Sibling 工具生态
这个仓库是家族站点的入口，链接到一系列独立仓库（watch-price-tracker、alpine-route-planner、
swiss-city-guide、ai-resume-builder 等），每个工具都是零构建静态站，部署在
`https://junpingkoch-web.github.io/<repo-name>/`。给首页加新工具卡片时，要先确认对应工具仓库已经存在并已发布。

## 明确禁止的事
- 不要引入构建工具/框架/npm 依赖——保持零构建静态站的定位，这是整个工具家族的统一约定
- 不要把 `ca-pub-XXXXXXXXXXXXXXX` 占位符误当成真实 ID 替换掉，除非用户明确要求换真实 AdSense 单元
- 新增图片前先在浏览器里视觉确认（截图或用 Read 工具查看图片本身），不要只信 WebFetch 的文字描述——
  之前多次把图标网格描述成"彩色骰子"这类幻觉

## Claude 工作方式
- **改动前先读一遍相关章节的记忆**（`portfolio-site-bento-redesign`、`junpingkoch-web-tool-ecosystem`），
  避免重新踩已经踩过的坑（如 `align-items:start` 的图片对齐问题、`hidden` 属性被 `display:flex` 覆盖的坑）
- **颜色/视觉方向的选择权在用户**：如果要改配色，提供 3-4 个带 hex 值的命名方案通过选择题问用户，不要单方面替用户决定
- **下载任何素材前需要用户明确同意**：说明文件名、来源、大小，在浏览器里截图确认后再保存到本地

## 持续维护
每次你需要重复纠正 Claude 同一件事三次以上，就把结论补进这个文件对应章节。
