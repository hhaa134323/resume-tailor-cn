# Resume Tailor CN — 中文简历定制 + HR 评审 Skill

## 是什么

一个 Claude Code Skill，输入目标 JD 和你的简历内容 Yaml，输出：

1. **一页定制简历 PDF** — 按 JD 调整个人定位、裁剪项目，渲染为排版精良的 A4 PDF
2. **打招呼语** — 针对每个岗位写一条像真人随手打的招呼
3. **模拟 HR 评审** — 用 hr-reviewer 子代理从 HR + 用人经理双视角挑刺，改到满意为止

## 怎么触发

作为 Claude Code 用户，在当前项目目录下说：

> "帮我针对 XX 公司 XX 岗定制简历"
> "跑 /hr-review"
> "帮我写打招呼语"

## 输入

| 输入 | 格式 | 说明 |
|------|------|------|
| JD 文本 | OCR 或粘贴 | 从 BOSS / 实习僧等平台获取的岗位描述 |
| 简历内容 | `cv/content_公司.yaml` | 按 `cv/example_content.yaml` 格式写你的真实信息 |

## 输出

| 输出 | 说明 |
|------|------|
| `cv/content_公司.pdf` | 定制后的一页简历 |
| 招呼语 | 一岗一条，输出为 Markdown 表 |
| HR 评审报告 | 6 维度结构化反馈 |

## 管线

```
content_公司.yaml → render.py (Jinja2 → HTML → Playwright PDF)
                 → 一页校验 (auto-fit + 梯度收缩)
                 → hr-reviewer (HR 双视角评审)
                 → 按反馈修改 → 重渲 → 定稿
```

## 设计原则

### 内容 / 格式分离
你的真实信息写在 YAML 里，排版归 `template.html` + `style.css` + `render.py` 管。改简历内容不碰样式，改样式不动内容。

### 一页强制
实习简历必须一页。`auto-fit` 先做 CSS 压缩（无损），还不够才裁剪内容（有损），始终优先保核心。

### 去 AI 味
招呼语和简历文案由 Claude 写，但禁止这些符号：双引号 ""、箭头 ➡️ →、圆括号（）、直角引号「」、斜杠 /。短句口语，像真人写的。

### HR 评审闭环
`/hr-review` 命令自动走：渲染 → 提取文本 → 调 hr-reviewer 评审 → 改 YAML → 重渲。可跑 1-2 轮直到 HR 给正面结论。

### 字体原则
中文用楷体（KaiTi / 楷体 / STKaiti），英文数字用 Times New Roman，浏览器按字形自动回退。Windows 自带字体，无需额外下载。

## 项目结构

```
├── cv/
│   ├── render.py                 # 渲染入口：YAML → Jinja2 → Playwright PDF
│   ├── template.html             # Jinja2 简历模板
│   ├── style.css                 # 打印样式（楷体+TNR、一页、无 bullet 标记）
│   └── example_content.yaml      # 示例内容文件（虚构），替换后使用
├── .claude/
│   ├── agents/
│   │   └── hr-reviewer.md        # HR 评审子代理
│   └── commands/
│       └── hr-review.md          # /hr-review 命令
├── SKILL.md                      # 本文件
├── greeting_guide.md             # 招呼语生成指南
├── CLAUDE.md                     # 项目约定
├── requirements.txt              # 依赖
├── LICENSE                       # MIT
└── README.md                     # 使用说明（待补）
```
