"""
render.py — YAML → Jinja2 → Playwright PDF
============================================
读写分离：caca 只改 content.yaml，格式归我管。

用法:
  python cv/render.py                          # 默认渲 content.yaml → content.pdf
  python cv/render.py content.yaml --out 简历_公司.pdf
  python cv/render.py content.yaml --auto-fit   # 自动收缩到 1 页
  python cv/render.py content.yaml --dry-run    # 只输出 HTML 预览

注意：依赖 Playwright 无头 Chromium 做 HTML→PDF 渲染，
     需要额外一步：playwright install chromium
     不是用于浏览器自动化或反爬对抗。
"""

import sys, os, copy, tempfile, shutil
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from PyPDF2 import PdfReader

CV_DIR = Path(__file__).resolve().parent

# ── 各 compact 等级的排版参数 ────────────────────────────────
COMPACT_PROFILES = {
    # level: (font_base, font_heading, font_name, lh, section_gap, bullet_gap, margin_top, margin_bottom, margin_x)
    0: ("11pt",   "12.5pt", "17pt", "1.40", "6pt",  "1.5pt", "14mm", "14mm", "16mm"),
    1: ("10.5pt", "12pt",   "16pt", "1.38", "4pt",  "1pt",   "12mm", "12mm", "14mm"),
    2: ("10pt",   "11.5pt", "15pt", "1.35", "3pt",  "0.5pt", "10mm", "10mm", "12mm"),
    3: ("9.5pt",  "11pt",   "14pt", "1.30", "2pt",  "0.5pt",  "8mm",  "8mm",  "10mm"),
}

# ── 收缩策略流水线 ──────────────────────────────────────────
# 每个策略：compact 等级 + 可选 content 裁减动作
STRATEGIES = [
    {"name": "tighten",       "compact": 1, "action": None},
    {"name": "reduce_font",   "compact": 2, "action": None},
    {"name": "reduce_margin", "compact": 3, "action": None},
]
# 内容裁减循环：反复删直到 1 页
REMOVAL_ACTIONS = ["pop_skill", "pop_bullet", "pop_entry"]


# ── IO ────────────────────────────────────────────────────────

def load_content(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── 内容裁减（原地修改 content dict） ────────────────────────

def pop_skill(c: dict) -> bool:
    s = c.get("skills", [])
    if s: s.pop(); return True
    return False

def pop_bullet(c: dict) -> bool:
    for section in ["projects", "internships"]:
        items = c.get(section, [])
        for item in reversed(items):
            b = item.get("bullets", [])
            if b:
                b.pop()
                if not b:
                    items.remove(item)
                return True
    notes = c.get("education", {}).get("notes", [])
    if notes:
        notes.pop()
        return True
    return False

def pop_entry(c: dict) -> bool:
    for section in ["projects", "internships"]:
        items = c.get(section, [])
        if items:
            items.pop()
            return True
    return False

REMOVAL_FN = {"pop_skill": pop_skill, "pop_bullet": pop_bullet, "pop_entry": pop_entry}


# ── 渲染 ──────────────────────────────────────────────────────

def render_html(content: dict, compact: int = 0) -> str:
    """Jinja2 渲染 → HTML 字符串。"""
    env = Environment(loader=FileSystemLoader(str(CV_DIR)))
    tmpl = env.get_template("template.html")

    fs, fh, fn, lh, sg, bg, mt, mb, mx = COMPACT_PROFILES.get(compact, COMPACT_PROFILES[0])

    data = {
        "basics":           content.get("basics", {}),
        "positioning":      content.get("positioning", ""),
        "education":        content.get("education", {}),
        "projects":         content.get("projects", []),
        "internships":      content.get("internships", []),
        "skills":           content.get("skills", []),
        # 排版参数（灌进 inline style）
        "font_size_base":   fs,
        "font_size_heading": fh,
        "font_size_name":   fn,
        "line_height":      lh,
        "section_gap":      sg,
        "bullet_gap":       bg,
        "page_margin_top":  mt,
        "page_margin_bottom": mb,
        "page_margin_x":    mx,
    }
    return tmpl.render(**data)


def render_pdf(html_str: str, output_path: str | Path) -> str:
    """Playwright 无头浏览器 → A4 PDF（去页眉页脚）。"""
    with tempfile.TemporaryDirectory(prefix="cv_render_") as tmp:
        tmp = Path(tmp)
        html_file = tmp / "resume.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_str)
        # 复制 style.css
        css_src = CV_DIR / "style.css"
        if css_src.exists():
            shutil.copy2(str(css_src), str(tmp / "style.css"))

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(html_file.absolute().as_uri())
            page.wait_for_load_state("networkidle")
            page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
            browser.close()

    return output_path


def count_pages(pdf_path: str | Path) -> int:
    with open(pdf_path, "rb") as f:
        return len(PdfReader(f).pages)


# ── 快速渲染（不做收缩） ─────────────────────────────────────

def fast_render(content: dict, output_path: str | Path, compact: int = 0):
    html = render_html(content, compact=compact)
    render_pdf(html, output_path)
    p = count_pages(output_path)
    print(f"PDF: {output_path}  ({p} pages)")
    return p


# ── 自动适配一页 ──────────────────────────────────────────────

def auto_fit(content: dict, output_path: str | Path, max_pages: int = 1):
    """
    梯度收缩直到 <= max_pages。
    先用 CSS 压缩（无损），再删内容（有损），交替进行。
    """

    def _try(working, compact) -> int:
        html = render_html(working, compact=compact)
        with tempfile.TemporaryDirectory(prefix="cv_try_") as tmp:
            pdf = Path(tmp) / "try.pdf"
            render_pdf(html, pdf)
            return count_pages(pdf)

    original = copy.deepcopy(content)
    rounds = 0

    for strat in STRATEGIES:
        html = render_html(original, compact=strat["compact"])
        with tempfile.TemporaryDirectory(prefix="cv_try_") as tmp:
            pdf = Path(tmp) / "try.pdf"
            render_pdf(html, pdf)
            p = count_pages(pdf)
        print(f"  [{strat['name']}] CSS compact={strat['compact']} -> {p} pages")
        rounds += 1
        if p <= max_pages:
            out = render_pdf(html, output_path)
            print(f"\nOK: {count_pages(out)} page(s) -> {out}")
            return True

    # 打开有损模式：维持 compact=3，逐步删内容
    working = copy.deepcopy(original)
    for action in REMOVAL_ACTIONS:
        for _ in range(20):  # 每种动作最多试 20 次
            ok = REMOVAL_FN[action](working)
            if not ok:
                break
            p = _try(working, compact=3)
            print(f"  [{action}] -> {p} pages")
            rounds += 1
            if p <= max_pages:
                out = render_pdf(render_html(working, compact=3), output_path)
                print(f"\nOK: {count_pages(out)} page(s) -> {out}")
                return True

    print(f"\nWARNING: cannot fit into {max_pages} page(s) after {rounds} rounds")
    return False


# ── HTML 预览 ─────────────────────────────────────────────────

def dry_run(content: dict, output_path: str | Path, compact: int = 0):
    html = render_html(content, compact=compact)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML: {output_path}")


# ── CLI ────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="YAML -> HTML+CSS -> PDF")
    parser.add_argument("content", nargs="?",
                        default=str(CV_DIR / "content.yaml"))
    parser.add_argument("--out", default=None)
    parser.add_argument("--auto-fit", action="store_true",
                        help="自动收缩到 1 页")
    parser.add_argument("--compact", type=int, default=0, choices=[0, 1, 2, 3])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    content = load_content(args.content)
    out = Path(args.out or Path(args.content).with_suffix(".pdf")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        dry_run(content, out.with_suffix(".html"), compact=args.compact)
    elif args.auto_fit:
        auto_fit(content, out)
    else:
        fast_render(content, out, compact=args.compact)


if __name__ == "__main__":
    main()
