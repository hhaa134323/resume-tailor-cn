# Resume Tailor CN

一个简历定制工具。你用大白话告诉 AI 助手「帮我按这个岗位改简历」，它就替你改好内容、排好版，导出成一页 A4 的 PDF。日常使用完全不需要你写代码。

它是怎么运作的，一句话讲清楚：你的简历内容和排版是分开的。内容存在一个文本文件里，排版样式已经调好固定住，一个脚本负责把内容套进模板生成 PDF。这些活儿都交给 AI 助手去跑，你只管开口说要什么。

## 你需要准备什么

- 一台电脑，作者用的是 Windows 11，Mac 也可以。
- 一个 AI 编程助手，任选一个：Claude Code、Cursor、Cline 等都行。
- 第一次使用要装一次运行环境。如果你不懂这些，不用自己折腾，打开项目后直接对 AI 助手说一句「帮我把这个项目的运行环境装好」，它会一步步替你装完。

## 第一步：把这个工具交给你的 AI 助手

这个仓库里有一份 SKILL.md，它是专门写给 AI 看的说明书，告诉 AI 这个工具该怎么用。你要做的，就是让你的助手能读到它。不同助手放的位置不一样：

- **Claude Code**：最省事。直接用 Claude Code 打开这个项目文件夹，它会自动读取 SKILL.md 和 CLAUDE.md，不用额外设置。
- **Cursor**：把 SKILL.md 的内容复制到项目里的 `.cursor/rules/` 文件夹下，存成一个 `.md` 文件，Cursor 的内置 AI 会把它当成项目规则。
- **VS Code（Cline 或 Roo Code）**：把 SKILL.md 的内容整合进对应扩展的指令文件里。
- **JetBrains 系（内置 AI Assistant）**：把 SKILL.md 内容放到 `.junie/guidelines/` 下。

以上这步本身也可以让 AI 助手帮你做，你只要说「帮我把 SKILL.md 配置成你的项目规则」即可。配好之后，AI 就知道怎么用这套工具了。

## 第二步：用大白话让它干活

配好之后，你只需要在对话框里说人话。下面这些话都能让它开始工作：

- 「帮我针对 XX 公司的 XX 岗位定制简历」
- 「这是这个岗位的招聘要求，按它改我的简历并导出 PDF」，然后把招聘要求粘进去
- 「帮我写这个岗位的打招呼语」
- 「跑一遍模拟 HR 评审」，或者直接输入 `/hr-review`

它会自动完成一整套流程：读懂岗位要求，裁剪和调整你的简历内容，生成 PDF，需要的话再做一轮模拟 HR 评审、按反馈改稿、重新导出。

第一次用的时候，先把你的真实简历信息告诉它，或者让它读你现有的简历文件，它会替你填进内容文件，之后每次换岗位就在这个基础上调整。

## 你会拿到什么

成品是一份 PDF，存在项目的 `cv` 文件夹里。一页 A4，中文用楷体、英文和数字用 Times New Roman，排版已经固定调好，你不用操心格式。

针对不同公司投递时，可以让助手为每家公司单独存一份内容文件，互不影响。这些个人内容文件已经设置成不会被上传到 GitHub，不用担心信息泄露。

## 常见问题

- **PDF 里中文变成方框或乱码**：说明电脑缺楷体字体。Windows 一般自带楷体，如果出现这个问题，跟助手说「中文显示成方框了，帮我换成系统里有的字体」即可。
- **内容一页放不下**：跟助手说「太长了，帮我压到一页」，它会先收紧排版，还不够就帮你删掉最不相关的经历。
- **个人信息安全**：示例文件里的姓名、学校、公司都是虚构的。你自己的内容文件已被设置为不会提交到 GitHub。
- **打招呼语不会自动发送**：助手只负责写出来，发到招聘平台这一步要你自己复制粘贴。

## 进阶：开发者手动用法（可选）

如果你熟悉命令行，也可以不经过 AI，自己跑脚本。这部分对不写代码的人没用，可以跳过。

环境准备：

\`\`\`bash
python -m venv .venv
# Windows 激活：.venv\Scripts\activate
# Mac / Linux 激活：source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
# 如提示缺包：pip install pyyaml jinja2 pypdf2
\`\`\`

渲染命令：

| 命令 | 作用 |
|------|------|
| \`python cv/render.py cv/content.yaml\` | 按默认排版生成 PDF |
| \`python cv/render.py cv/content.yaml --auto-fit\` | 自动收缩到一页 |
| \`python cv/render.py cv/content.yaml --compact 2\` | 手动指定紧凑等级，0 到 3，越大越紧 |
| \`python cv/render.py cv/content.yaml --dry-run\` | 只生成 HTML 预览，不转 PDF |
| \`python cv/render.py cv/content.yaml --out 简历.pdf\` | 指定输出文件名 |

内容文件 `cv/example_content.yaml` 里有完整的字段示例，复制一份改成自己的即可。

## 项目结构

\`\`\`
├── cv/
│   ├── render.py             渲染脚本：读内容、套模板、生成 PDF
│   ├── template.html         简历模板
│   ├── style.css             排版样式，中文楷体加英文 Times New Roman
│   └── example_content.yaml  内容示例，虚构信息，复制后改成自己的
├── .claude/
│   ├── agents/hr-reviewer.md     模拟 HR 评审的子助手
│   └── commands/hr-review.md     /hr-review 命令定义
├── CLAUDE.md                 项目约定
├── SKILL.md                  写给 AI 的说明书
├── greeting_guide.md         打招呼语生成指南
├── requirements.txt          Python 依赖
└── LICENSE                   MIT
\`\`\`

## License

MIT
