# /tailor-from-jd — JD 截图 → 岗位评估 → 定制简历 → 招呼语

端到端流程：读 JD 文件夹 → 逐个评估 → 重点岗定制简历 → 可选 HR 评审 → 写招呼语。

## 用法

```
/tailor-from-jd [--folder jobs/文件夹] [--skip-review]
```

- `--folder`：JD 截图或文本所在的文件夹，默认 `jobs/<日期>/`
- `--skip-review`：跳过 HR 评审环节

## 流程（我来依次执行）

### Step 1：找 JD 文本
- 去指定的文件夹下找 `jd_*.txt`（OCR 输出或用户放好的文本）
- 如果没有，检查是否有图片文件，先自动调 `ocr_jd.py` 做 OCR

### Step 2：逐个评估
- 对每个 `jd_*.txt`，调用 `jd-analyzer` 子代理做评估
- 输入：JD 文本 + `cv/example_content.yaml`（或用户指定的内容文件）
- 输出：匹配分、分档、命中点、缺口、建议
- 按匹配分从高到低排序展示给用户

### Step 3：用户确认
- 打印排序后的评估结果，让用户确认要对哪些岗位做定制
- 默认对「重点定制」档的岗位做深度定制

### Step 4：定制内容
- 复制 `cv/example_content.yaml` → `cv/content_公司.yaml`
- 写个人定位（扣 JD 具体关键词，1-2 行）
- 按 JD 裁剪：保留最相关的项目/实习，删最弱的
- 清理 AI 味符号（双引号、斜杠、全角括号、箭头等）
- 输出给用户确认

### Step 5：渲染 PDF
- `python cv/render.py cv/content_公司.yaml --auto-fit`
- 如果超 1 页自动收缩；不足 1 页（大片空白）则提示用户补内容
- 产出路径默认 `cv/content_公司.pdf`

### Step 6：可选 HR 评审
- 如果用户没传 `--skip-review`，问是否要跑 `/hr-review`
- 如果确认，调用 hr-reviewer 子代理
- 按反馈改 YAML → 重渲（最多 2 轮）

### Step 7：写招呼语
- 按 `greeting_guide.md` 规则写
- 首句成果钩子 + 扣 JD + 公开作品链接 + 轻召唤
- 重点岗深度定制，普通岗用模板
- 输出 Markdown 表

### Step 8：输出总结
```
评估结果：
  [公司A] [岗位] → xx分 | 重点定制 → 简历: cv/content_A.pdf → 招呼语: ✓
  [公司B] [岗位] → xx分 | 普通模板 → 招呼语: ✓

招呼语：
  | 公司 | 岗位 | 招呼语 |
  |------|------|--------|
```
