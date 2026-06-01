# Resume Tailor CN — Claude Code 约定

## 工作方式

- 简历内容在 `cv/content_公司.yaml`，排版归 `template.html` + `style.css` + `render.py`
- 渲染命令：`python cv/render.py cv/content_公司.yaml --auto-fit`
- 招呼语由 Claude 在对话中输出，不自动发送
- `/hr-review` 调子代理做 HR 评审闭环

## 纪律

- **内容真实不编造**，个人定位按 JD 写但不夸大
- **去 AI 味**：招呼语禁止 "" / → / （）/「」/ /
- **一页强制**，用 `--auto-fit` 自动收缩
- **字体**：中文楷体 + 英文数字 Times New Roman
- **bullet 标记**：无方块，靠加粗 lead-in 分隔

## 修改前

改 `style.css` 前先确认不影响已有定制简历的版式。
