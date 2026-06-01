# /hr-review — 模拟 HR 评审 → 改简历闭环

Run this command to: render the current resume → extract text → call hr-reviewer agent → apply feedback → re-render.

## 用法

```
/hr-review [content_file]
```

如果不指定 `content_file`，默认用最近修改的 `cv/content_*.yaml`。

## 流程（我来依次执行）

### Step 1：确认目标简历
- 找出你要评审的 `content_公司.yaml`
- 同时确认对应的 JD 文本（通常在 `job{MMDD}/` 下，或 content YAML 的注释中有提及）
- 如果没有 JD 文本，我会先用 `grep`/`find` 在 `job{MMDD}/` 下找对应岗位的 `jobs_raw.txt` 中的文本，你要能告诉我目标公司名

### Step 2：渲染 PDF
- `python cv/render.py <content_file> --auto-fit`
- 产出：最终 PDF

### Step 3：提取 PDF 文字
- 用 PyPDF2 提取文本（忽略排版噪音，拿到纯内容即可）

### Step 4：调用 hr-reviewer 评审
- 通过 Agent tool 以 `subagent_type: "Explore"` 启动 hr-reviewer
- 输入：简历文本 + JD 文本
- 要求结构化输出覆盖所有人设要求的 6 个维度

### Step 5：读评审 → 改内容 YAML
- 在**不违反任何既有约束**的前提下修改 `content_公司.yaml`：
  - 保持一页
  - 内容真实不编造
  - 去 AI 味（像真人写的）
  - 个人定位按 JD 写
  - bullet 保持 ▢
  - 字体条件保持不变（楷体+TNR）
- 对 HR 的每一条可落地建议做出回应：
  - 「采纳了」→ 具体改了什么
  - 「不采纳，因为……」→ 给出理由（如违反约束、不真实等）

### Step 6：重渲 + 再评审（可选，最多 2 轮）
- 重渲 PDF
- 再调用 hr-reviewer 确认改进
- 如果 HR 给「会约面」就停；否则最多做 2 轮

### Step 7：输出总结
打印给用户：
1. HR 评审原文（全部 6 个维度）
2. 我采纳了什么改动 + 不采纳什么 + 理由
3. 终版 PDF 路径
4. HR 对终版的结论（约面/不约面 + 还剩什么意见）
