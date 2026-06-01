# Resume Tailor CN — 中文简历定制 + 岗位评估 + HR 评审 Skill

## 是什么

一个 AI 助手用的简历定制技能。给你一个到 AI 编程助手的对话框——无论是
Claude Code、Cursor、Cline 还是其他 AI 编程工具——你从 JD 截图到拿到
定制简历 PDF 和招呼语，只需要说人话，不需要写代码。

完整流程：

1. **OCR JD 截图** → 从截图里读出岗位描述
2. **岗位评估** → 按规则打分分档，诚实标缺口
3. **定制简历** → 按 JD 裁剪项目、写个人定位、渲染为一页 PDF
4. **HR 评审** → 模拟 HR 挑刺，改到满意为止
5. **写招呼语** → 每条首句成果钩子，像真人发微信

## 怎么触发

作为 Claude Code 用户，在当前项目目录下说：

> "帮我处理这批 JD，重点岗位定制简历"
> "帮我把 jobs/example 里的 JD 评估一遍"
> "针对这个岗位定制简历并导出 PDF"
> "跑 /hr-review"
> "跑 /tailor-from-jd"
> "帮我写打招呼语"

## 自然语言用法（适用于任何 AI 编程助手）

如果你用的是 Cursor、Cline、或其他 AI 编程助手，不用打斜杠命令，
直接用大白话说：

### 场景一：先 OCR 再评估

> 我有几张 JD 截图放在 jobs/example/ 文件夹里，先帮我把截图 OCR 成文字，
> 然后逐个岗位评估打分，告诉我哪些值得投。

助手会：
1. 运行 `python scripts/ocr_jd.py --folder jobs/example` 把截图转为文本
2. 读取 `cv/example_content.yaml` 中的候选人简历信息
3. 对每个岗位按评估规则做打分分档
4. 输出评估结果和推荐钩子作品

### 场景二：直接读 JD 定制简历

> 我有一份岗位描述，帮我定制简历。JD 在 jobs/example/jd_星辰科技_AI产品助理.txt，
> 我的简历在 cv/example_content.yaml。

助手会：
1. 读 JD 文本和简历
2. 按评估规则做匹配分析
3. 复制内容文件做裁剪和定位
4. 渲染为一页 PDF
5. 写招呼语

### 场景三：全流程闭环

> 帮我把 jobs/example/ 里的 JD 截图处理一遍：OCR、评估、重点岗定制简历、
> 跑 HR 评审、写招呼语。

助手会走完整流程，按匹配度排序，只对重点岗深度定制。

## 输入

| 输入 | 格式 | 说明 |
|------|------|------|
| JD 截图 | `jobs/<日期>/*.jpg/png` | 从 BOSS / 实习僧等平台截图，用 OCR 转文字 |
| JD 文本 | `jobs/<日期>/jd_*.txt` | OCR 产出，或你直接粘贴存成的 txt |
| 简历内容 | `cv/content_公司.yaml` | 按 `cv/example_content.yaml` 写你的真实信息 |

## 输出

| 输出 | 说明 |
|------|------|
| 评估结果 | 每个岗位的匹配分、分档、命中点、缺口 |
| `cv/content_公司.pdf` | 定制后的一页简历 |
| 招呼语 | 一岗一条，输出为 Markdown 表 |
| HR 评审报告 | 6 维度结构化反馈 |

## 管线

```
jobs/<日期>/截图
  → scripts/ocr_jd.py         # 图片→文本
  → jd-analyzer 子代理         # 读 JD + 简历 → 打分分档
  → (重点岗) 定制 content.yaml → render.py → PDF
  → hr-reviewer                # 模拟 HR 评审
  → greeting_guide.md 规则     # 写招呼语
```

## 设计原则

### 内容 / 格式分离
你的真实信息写在 YAML 里，排版归 `template.html` + `style.css` + `render.py` 管。
改简历内容不碰样式，改样式不动内容。

### 一页强制
实习简历必须一页。`auto-fit` 先做 CSS 压缩（无损），还不够才裁剪内容（有损），
始终优先保核心。

### 诚实不编造
岗位评估和简历定制都不编造不夸大。JD 有要求但候选人不满足的，如实标为缺口。
不把「方向接近」说成「完全匹配」。

### 去 AI 味
招呼语和简历文案由 AI 写，但禁止这些符号：双引号 ""、箭头 ➡️ →、圆括号（）、
直角引号「」、斜杠 /。短句口语，像真人写的。

### HR 评审闭环
`/hr-review` 命令自动走：渲染 → 提取文本 → 调 hr-reviewer 评审 → 改 YAML → 重渲。
可跑 1-2 轮直到 HR 给正面结论。

## 项目结构

```
├── cv/
│   ├── render.py                 渲染入口：YAML → Jinja2 → Playwright PDF
│   ├── template.html             Jinja2 简历模板
│   ├── style.css                 打印样式
│   └── example_content.yaml      示例内容文件（虚构），替换后使用
├── scripts/
│   └── ocr_jd.py                 JD 截图中文 OCR
├── docs/
│   └── jd_assessment.md          岗位评估规则（给 AI 读）
├── jobs/
│   └── example/                  虚构 JD 示例
├── .claude/
│   ├── agents/
│   │   ├── jd-analyzer.md        岗位评估子代理
│   │   └── hr-reviewer.md        HR 评审子代理
│   └── commands/
│       ├── tailor-from-jd.md     /tailor-from-jd 端到端命令
│       └── hr-review.md          /hr-review 命令
├── SKILL.md                      本文件
├── greeting_guide.md             招呼语生成指南
├── CLAUDE.md                     项目约定
├── requirements.txt              依赖
├── LICENSE                       MIT
└── README.md                     使用说明
```
