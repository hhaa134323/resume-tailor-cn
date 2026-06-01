# Resume Tailor CN

把母版简历按目标 JD 裁剪，渲染为一页 A4 PDF。内容和排版分离：YAML 管内容，HTML + CSS 管排版，render.py 拼合后调用 Chromium 无头浏览器输出 PDF。

可以作为 Claude Code Skill 使用，也支持纯手动运行，不依赖任何 AI 服务。

## 作为 Skill 喂给 AI

这个仓库自带 SKILL.md，AI agent（Claude Code、Cursor、Cline、其他兼容 agent）读到后能理解完整的工作流程。

把仓库交给 AI 的方式：

- **Claude Code**：把项目根目录作为 Claude Code 的工作目录启动，它会自动读取根目录的 SKILL.md 和 CLAUDE.md，按技能执行。
- **全局安装**（可选）：把仓库放到 `~/.claude/skills/resume-tailor-cn/`，或在 Claude Code 设置中通过路径引用。
- **其他 agent**：把 SKILL.md 的内容作为系统指令提供给 AI，或按各工具约定整合（见下方安装小节）。

核心渲染脚本 render.py 始终可以独立运行，不依赖任何 agent。

## 安装

### Claude Code

在 Claude Code 中直接 cd 到项目目录即可使用。项目根目录的 SKILL.md 和 CLAUDE.md 定义了完整的工作方式和约束。

如果想把技能全局注册：

```bash
# 软链到 Claude Code skills 目录（如果该目录存在）
ln -s D:/AgentProjects/resume-skill-public ~/.claude/skills/resume-tailor-cn
```

或直接在 Claude Code 中用 `claude --add-dir D:/AgentProjects/resume-skill-public` 引用。

### Cursor

把 SKILL.md 内容复制到 `.cursor/rules/` 下（例如 `.cursor/rules/resume-tailor.md`），Cursor 的内置 AI 会自动识别为项目规则。

### VS Code（Cline / Roo Code）

Cline 和 Roo Code 等扩展支持项目级指令文件。把 SKILL.md 的内容整合进对应的指令配置文件即可。

### JetBrains（AI Assistant）

JetBrains AI Assistant 支持项目级 guidelines。把 SKILL.md 内容放到 `.junie/guidelines/` 下。

### 纯手动 / 任意 agent

不安装任何插件。直接 clone 仓库，安装 Python 依赖，编辑 YAML 后运行 render.py。所有功能正常使用。详见下方"快速上手"。

## 环境准备

- Python 3.10+
- Windows 11（作者环境；macOS / Linux 同样兼容，命令微调见括号说明）

```bash
# 1. 建虚拟环境
python -m venv .venv

# 2. 激活
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Playwright 的 Chromium 浏览器
playwright install chromium
```

requirements.txt 实际安装的包：

| 包 | 用途 |
|------|------|
| playwright>=1.40.0 | 无头浏览器渲染 PDF |
| rich>=13.0.0 | 终端输出高亮（当前版本暂未在 render.py 中导入，预留） |

render.py 运行时还会使用 PyYAML、Jinja2、PyPDF2（通常随 Playwright 或已安装的包间接满足），如果报 ModuleNotFoundError，手动补装：

```bash
pip install pyyaml jinja2 pypdf2
```

## 快速上手

### 1. 准备简历内容

```bash
# 复制示例文件
cp cv/example_content.yaml cv/content.yaml
# Windows 也支持:
# copy cv\example_content.yaml cv\content.yaml
```

### 2. 编辑 YAML

用文本编辑器打开 `cv/content.yaml`，把里面的姓名、电话、邮箱、教育经历、项目、实习、技能替换成你自己的。格式参考 `cv/example_content.yaml`。

### 3. 渲染 PDF

```bash
python cv/render.py cv/content.yaml --auto-fit
```

输出文件：`cv/content.pdf`（一页 A4，如果内容超过一页会自动压缩）。

### 按不同岗位定制

```bash
# 每个目标公司建一个独立内容文件
cp cv/content.yaml cv/content_公司A.yaml
cp cv/content.yaml cv/content_公司B.yaml
```

每个 YAML 文件独立编辑，按对应 JD 调整个人定位、项目排序和技能重点。分别渲染：

```bash
python cv/render.py cv/content_公司A.yaml --auto-fit
python cv/render.py cv/content_公司B.yaml --auto-fit
```

`.gitignore` 已排除所有 `content_*.yaml`（`example_content.yaml` 除外），不会误提交个人信息。

### YAML 结构

| 字段 | 对应排版位置 |
|------|-------------|
| `basics.name` | 页首大号姓名 |
| `basics.phone` / `basics.email` | 联系方式 |
| `basics.intern_terms` | 出勤说明 |
| `positioning` | 个人定位（一段话） |
| `education.rows` | 学校 / 学院 / 专业 / 时间，四列表格 |
| `education.notes` | 课程、证书等补充说明，带加粗 lead-in |
| `projects` | 项目经历，每项含 title、date、bullets |
| `internships` | 实习经历，每项含 org、role、date、bullets |
| `skills` | 专业技能，每项含 label、content |

bullet 格式：`lead` 加粗做分隔符，`text` 是正文，中间用中文冒号连接。

## 功能一览

| 功能 | 说明 |
|------|------|
| YAML 内容 → PDF 渲染 | 内容格式分离，改内容不碰样式，改样式不动内容 |
| 一页自适应校验 | `--auto-fit` 先 CSS 压缩（收紧字号、行距、间距、边距），还不够时按优先级裁剪内容（删技能条目 -> 删 bullet -> 删整个条目） |
| 4 级紧凑预设 | `--compact 0-3` 手动选择排版密度等级 |
| 中文楷体 + 英文 Times New Roman | 浏览器按字形自动回退，Windows 自带字体无需额外下载 |
| HTML 预览模式 | `--dry-run` 只生成 HTML，不转 PDF，快速预览排版 |
| 招呼语生成 | `greeting_guide.md` 定义生成规范，去 AI 味，按岗位分档定制 |
| HR 评审子代理 | `hr-reviewer` agent 从 HR + 用人经理双视角做结构化评审 |
| `/hr-review` 斜杠命令 | 自动走：渲染 → 提取 PDF 文本 → 调 hr-reviewer → 改 YAML → 重渲，最多 2 轮闭环 |

### render.py 命令行选项

| 命令 | 作用 |
|------|------|
| `python cv/render.py cv/content.yaml` | 默认参数渲染 PDF（紧凑等级 0） |
| `python cv/render.py cv/content.yaml --auto-fit` | 自动收缩到一页 |
| `python cv/render.py cv/content.yaml --out 简历.pdf` | 指定输出文件名 |
| `python cv/render.py cv/content.yaml --dry-run` | 只生成 HTML 预览，不转 PDF |
| `python cv/render.py cv/content.yaml --compact 2` | 手动指定紧凑等级（0-3，越大越紧） |

不传 content 路径时默认读取 `cv/content.yaml`，输出到同名 `.pdf` 文件。

## 调用方式

### Claude Code 斜杠命令

| 命令 | 作用 |
|------|------|
| `/hr-review` | 渲染当前简历 → 提取文本 → hr-reviewer 子代理评审 → 按反馈修改 → 重渲。默认用最近修改的 `cv/content_*.yaml`，也可指定文件名 |

### 自然语言触发（Claude Code 中）

以下表述可以触发技能：

- "帮我针对 XX 公司 XX 岗位定制简历"
- "跑 /hr-review"
- "帮我写打招呼语"
- "按这份 JD 改简历并渲染成 PDF"

AI agent 会自动走：读 JD → 裁剪 YAML 内容 → 渲染 PDF → （可选）HR 评审 → 修改 → 定稿。

## 注意事项

### 中文渲染缺字

PDF 中文变成方框或乱码，说明系统缺少楷体字体。Windows 通常自带楷体（KaiTi / 华文楷体），如果出现缺字：

1. 确认系统已安装"楷体"或"华文楷体"
2. macOS / Linux 可能需要额外安装中文字体
3. 调整 `style.css` 中 `body` 的 `font-family` 顺序，把首选字体改成你确定有的字体

### 一页放不下

`--auto-fit` 有极限。按以下顺序手动干预：

1. 删条目：在 YAML 里删掉最不相关的项目或实习
2. 缩 bullet：缩短每条 bullet 的文字，或删掉次要 bullet
3. 合并行：技能条目合并，教育经历如果学校多可以只留最近的
4. 用 `--compact 3` 最紧凑等级渲染

以上都不够，说明内容确实超过一页容量，必须裁剪。

### 母版路径

render.py 以自身所在目录（`cv/`）作为资源根目录，template.html 和 style.css 都从那里加载。不要在项目根目录之外运行 render.py。

### 模拟内容与脱敏

`cv/example_content.yaml` 中的姓名、学校、公司、联系方式均为虚构示例。`cv/content_*.yaml` 已被 .gitignore 排除，不会误提交。实际使用时注意不要在提交中带入真实个人信息。

### 招呼语不自动发送

招呼语由 AI 在对话中输出，需要你手动复制到招聘平台发送。

## 项目结构

```
├── cv/
│   ├── render.py                 # 渲染入口：YAML → Jinja2 → HTML → Playwright PDF
│   ├── template.html             # Jinja2 简历模板
│   ├── style.css                 # 打印样式（中文楷体 + 英文 TNR）
│   └── example_content.yaml      # 示例内容（虚构），替换后使用
├── .claude/
│   ├── agents/
│   │   └── hr-reviewer.md        # HR 评审子代理定义
│   └── commands/
│       └── hr-review.md          # /hr-review 命令定义
├── CLAUDE.md                     # 项目约定
├── SKILL.md                      # Skill 说明
├── greeting_guide.md             # 招呼语生成指南
├── requirements.txt              # Python 依赖
├── LICENSE                       # MIT
└── README.md                     # 本文件
```

## License

MIT
