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
- 二维码类图片（如 `images/qr-navigation-poster-a4*.png`）改完之后不要只看着好看就上线——必须实际
  解码验证每个码都指向正确链接（见下方"二维码海报生成流程"），肉眼看着像 QR 码不等于真的能扫

## Claude 工作方式
- **改动前先读一遍相关章节的记忆**（`portfolio-site-bento-redesign`、`junpingkoch-web-tool-ecosystem`），
  避免重新踩已经踩过的坑（如 `align-items:start` 的图片对齐问题、`hidden` 属性被 `display:flex` 覆盖的坑）
- **颜色/视觉方向的选择权在用户**：如果要改配色，提供 3-4 个带 hex 值的命名方案通过选择题问用户，不要单方面替用户决定
- **下载任何素材前需要用户明确同意**：说明文件名、来源、大小，在浏览器里截图确认后再保存到本地
- **零 JS 折叠/展开交互，用 checkbox+label 技巧**：导航栏汉堡菜单（`#nav-toggle`）和首页简介折叠
  （`#bio-toggle`）都是这个模式——`<input type="checkbox">` 放在 `<body>` 早期位置，配对的
  `<label for="...">` 当触发器，用 `~` 兄弟选择器控制目标区域的 `display`。checkbox 要用
  "视觉隐藏但可聚焦"的写法（`position:absolute; width:1px; height:1px; clip:rect(0,0,0,0);`），
  不要直接 `display:none`——否则键盘用户 Tab 不到，无法用空格键触发
- **法律页面（Impressum 等）联系方式含哪些信息，要先问用户**：姓名/邮箱/地址暴露程度是用户自己的
  隐私决定，不要替用户决定要不要公开地址
- **Unsplash 浏览器自动化时好时坏**：曾经出现连续多次 `navigate` 被拒绝、标签页无故关闭、
  截图超时（"Browser pane is not displayed"）。别在同一个方法上反复重试烧掉很多轮——试 2-3 次
  同一种手法不行，就直接跟用户提"要不要改用纯 CSS/SVG 图标（不依赖外部图片，现在就能上线）"这个
  备选方案，别硬耗。纯 SVG 图标要用 `currentColor` 继承颜色，配色复用站点自己的 CSS 变量
  （`--accent`/`--accent-strong`/`--bg`/`--border`），不要写死颜色值

## 二维码海报生成流程（`images/qr-navigation-poster-a4*.png`）
这类"文字+若干真实二维码"的印刷级图片，没有可编辑源文件时按下面流程重新生成，不要直接在图片编辑器里
拼贴或让 AI 画"看起来像"二维码的图案（那种码扫不出来）：
1. 用 `api.qrserver.com/v1/create-qr-code/?size=600x600&data=<url>` 给每个真实链接下载一张真二维码 PNG
2. 转 base64 内嵌进一个自包含的 HTML 模板，配色复用站点自己的 CSS 变量（`--bg`/`--surface`/`--border` 等）
3. 用本机 Chrome 的无头截图模式渲染成精确像素尺寸（A4@300dpi = 2480×3508px）：
   `chrome.exe --headless=new --disable-gpu --screenshot="<绝对路径>.png" --window-size=2480,3508 --force-device-scale-factor=1 file:///<绝对路径>.html`
   ——**`--screenshot` 的输出路径必须是绝对路径**，相对路径在这个环境里会报 `Access denied`
4. 内容自然高度几乎不会正好等于目标高度，不要凭 CSS 数值手算——往页面末尾插一个 marker 元素，
   用无头 Chrome 的 `--dump-dom` 读它的 `getBoundingClientRect().bottom` 拿到真实高度，
   再用 `transform: scale(目标高度/实际高度)` 包一层、`margin-left` 居中，保证输出正好是目标像素尺寸
5. **上线前必须验证二维码真的能扫**：用同样的 `getBoundingClientRect()` 技巧拿到每个码在最终图片里的
   精确坐标，起一个本地 `http.server`（file:// 协议下 canvas 会因为跨域被"污染"读不出像素），
   在页面里用 jsQR（`cdn.jsdelivr.net/npm/jsqr`）逐个裁剪解码，比对解码结果和期望链接是否完全一致
- 需要多语言版本时（如德语版海报），标题/说明文字翻译要贴合各工具在 `index.html` 里已经用过的
  德语措辞，不要另起一套新译法造成站内不一致

## 持续维护
每次你需要重复纠正 Claude 同一件事三次以上，就把结论补进这个文件对应章节。
