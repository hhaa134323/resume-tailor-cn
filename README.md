# Resume Tailor CN

把母版简历内容按目标 JD 裁剪，渲染为一页 A4 PDF。内容和排版分离，改内容不碰样式，改样式不动内容。

## 工作方式

```
content.yaml (YAML 简历内容)
        |
        v
render.py ──Jinja2──→ HTML + CSS
        |
        v
  Playwright 无头浏览器 → A4 PDF
```

你的信息写在 YAML 文件里，`template.html` + `style.css` 管排版，`render.py` 把两者拼起来，调用 Chromium 无头浏览器渲染成 PDF。

### 一页自适应

`--auto-fit` 参数会自动把简历压到一页，分两步：

1. **CSS 压缩（无损）**：逐级收紧字号、行距、间距、页边距，不删内容。
2. **内容裁剪（有损）**：CSS 压到极限还不够时，按优先级删除——先删专业技能条目，再删项目/实习的 bullet，最后删整个条目。

## 环境准备

- Python 3.10+
- Windows 11（作者环境；macOS / Linux 也兼容，命令微调见下文）

```bash
# 1. 建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate

# 2. 装依赖
pip install -r requirements.txt

# 3. 装 Playwright 浏览器
playwright install chromium
```

> **macOS / Linux 用户**：激活虚拟环境用 `source .venv/bin/activate`，其余命令一样。

`requirements.txt` 的内容：

```
playwright>=1.40.0     # 无头浏览器渲染 PDF
rich>=13.0.0           # 终端输出高亮
```

render.py 还依赖 `PyYAML`、`Jinja2`、`PyPDF2`，它们通常随 Playwright 或已安装的包间接满足；如果运行报 `ModuleNotFoundError`，手动补装：

```bash
pip install pyyaml jinja2 pypdf2
```

## 快速上手

```bash
# 1. 复制示例文件为自己的简历
cp cv\example_content.yaml cv\content.yaml

# 2. 编辑 content.yaml，替换为你的真实信息
#    姓名、电话、邮箱、教育经历、项目、实习、技能

# 3. 渲染 PDF
python cv\render.py cv\content.yaml --auto-fit

# 输出：cv/content.pdf（一页 A4）
```

### 可用的渲染选项

| 命令 | 作用 |
|------|------|
| `python cv/render.py cv/content.yaml` | 默认参数渲染 PDF |
| `python cv/render.py cv/content.yaml --auto-fit` | 自动收缩到一页 |
| `python cv/render.py cv/content.yaml --out cv/我的简历.pdf` | 指定输出文件名 |
| `python cv/render.py cv/content.yaml --dry-run` | 只生成 HTML 预览，不转 PDF |
| `python cv/render.py cv/content.yaml --compact 2` | 手动指定紧凑等级（0-3，越大越紧） |

## 按不同岗位定制

```bash
# 为每个公司建独立内容文件
cp cv\content.yaml cv\content_字节跳动.yaml
cp cv\content.yaml cv\content_腾讯.yaml

# 分别编辑，按 JD 调整个人定位和项目顺序
# 分别渲染
python cv\render.py cv\content_字节跳动.yaml --auto-fit
python cv\render.py cv\content_腾讯.yaml --auto-fit
```

每个 `content_公司.yaml` 独立渲染，互不影响。`.gitignore` 已排除所有 `content_*.yaml`（`example_content.yaml` 除外），不会误提交个人信息。

### YAML 结构说明

字段及其在简历上的位置：

| YAML 字段 | 对应排版位置 |
|-----------|-------------|
| `basics.name` | 页面顶部大号姓名 |
| `basics.phone` / `basics.email` | 联系方式 |
| `basics.intern_terms` | 出勤说明 |
| `positioning` | 个人定位（一段话） |
| `education.rows` | 学校/学院/专业/时间，四列表格 |
| `education.notes` | 课程/证书等补充说明，带 lead |
| `projects` | 项目经历，每项有 title, date, bullets |
| `internships` | 实习经历，每项有 org, role, date, bullets |
| `skills` | 专业技能，每项有 label, content |

bullet 的格式：`lead` 加粗作为分隔符，`text` 是正文，中间用中文冒号连接。

## 常见问题

### PDF 中文变成方框或乱码

字体文件缺失。确保系统已安装楷体（KaiTi / STKaiti）。Windows 通常自带，如果出现缺字：

1. 确认系统已安装"楷体"或"华文楷体"
2. 如果用了 macOS，可能需要安装中文字体或调整 CSS 中的 font-family 顺序
3. 调整后修改 `style.css` 中 `body` 的 `font-family`，把首选字体改成你确定有的字体

### 一页放不下，但 auto-fit 也没压住

`--auto-fit` 有极限。手动干预：

1. **删条目**：在 YAML 里删掉最不相关的项目或实习
2. **缩 bullet**：每个 bullet 的文字缩短，或删掉次要 bullet
3. **合并行**：技能条目合并成一条，教育经历如果学校多可以只留最近的
4. **手动 compact**：用 `--compact 3` 最紧凑等级渲染，看是否够

如果这些都不够，说明内容真的超过一页容量，必须裁剪。

### 简历内容改完后不想再装 Playwright

Playwright 约 200-300 MB（含 Chromium），如果只是后续手调 YAML 重渲，可以只在第一次装。后续换电脑或清理环境后重装即可。

### 不想用 Claude Code，能独立跑吗

能。`render.py` 是纯 Python 脚本，不依赖任何 AI 服务。装好依赖、写好 YAML，直接 `python cv/render.py` 就能出 PDF。详见"快速上手"。

## Claude Code Skill 用法

这个项目同时也设计为 Claude Code Skill。如果你在用 Claude Code，可以说：

> 帮我针对 XX 公司 XX 岗定制简历

它会自动走：读 JD 裁剪 YAML 内容 渲染 PDF HR 评审 修改 定稿。

不装 Claude Code 不影响核心功能——`render.py` 始终可以独立运行。

### 相关命令

| 命令 | 作用 |
|------|------|
| `python cv/render.py cv/content_公司.yaml --auto-fit` | 渲染 PDF |
| `/hr-review`（Claude Code 中） | 模拟 HR 评审 |

## 项目结构

```
├── cv/
│   ├── render.py                 # 渲染入口：YAML Jinja2 Playwright PDF
│   ├── template.html             # Jinja2 简历模板
│   ├── style.css                 # 打印样式（中文楷体 + 英文 Times New Roman）
│   └── example_content.yaml      # 示例内容（虚构），替换后使用
├── .claude/
│   ├── agents/
│   │   └── hr-reviewer.md        # HR 评审子代理定义
│   └── commands/
│       └── hr-review.md          # /hr-review 命令定义
├── CLAUDE.md                     # Claude Code 项目约定
├── SKILL.md                      # Skill 说明文档
├── greeting_guide.md             # 打招呼语生成指南
├── requirements.txt              # Python 依赖
├── LICENSE                       # MIT
└── README.md                     # 本文件
```

## License

MIT
