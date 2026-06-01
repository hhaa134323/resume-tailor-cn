"""
ocr_jd.py — JD 截图中文 OCR
=============================
扫描输入文件夹（默认 jobs/<日期>/）下的图片，对每张图做中文 OCR，
每张图输出一个 jd_序号_公司.txt 到同一文件夹。

用法:
    python scripts/ocr_jd.py                          # 默认用当天日期文件夹
    python scripts/ocr_jd.py --folder jobs/example    # 指定文件夹
    python scripts/ocr_jd.py --folder jobs/example --preview  # 只显示识别结果，不写文件
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
TEXT_EXTS = {".txt"}  # 也接受已存好的文本（测试/手工录入用）


def default_folder() -> str:
    """当天日期对应的文件夹名，如 jobs/0601"""
    return f"jobs/{datetime.now().strftime('%m%d')}"


def find_input_files(folder: str) -> list[Path]:
    """扫描文件夹，按文件名排序返回图片和 txt 文件"""
    files = []
    for f in Path(folder).iterdir():
        if f.suffix.lower() in IMAGE_EXTS | TEXT_EXTS and f.is_file():
            files.append(f)
    files.sort(key=lambda p: p.name)
    return files


def ocr_image(image_path: Path) -> str:
    """对单张图片做 OCR，返回识别后的文本"""
    try:
        from rapidocr_onnxruntime import RapidOCR
        engine = RapidOCR()
    except ImportError:
        print(
            "错误: 需要 rapidocr_onnxruntime\n"
            "  安装: pip install rapidocr_onnxruntime\n"
            "  备选: 把 JD 存为 txt 文件放入输入文件夹",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        result, elapse = engine(str(image_path))
    except Exception as e:
        return f"[OCR 错误: {e}]"

    if result is None:
        return "[未识别到文本]"

    lines = []
    for line in result:
        if len(line) >= 2:
            text = line[1]
            if text and text.strip():
                lines.append(text.strip())

    return "\n".join(lines)


def read_text_file(path: Path) -> str:
    """读取已存的 txt 文件"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description="JD 截图中文 OCR")
    parser.add_argument(
        "--folder", default=None,
        help=f"输入文件夹，默认 {default_folder()}"
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="只打印识别结果，不写文件"
    )
    args = parser.parse_args()

    folder = args.folder or default_folder()
    folder_path = Path(folder)

    if not folder_path.exists():
        print(f"文件夹不存在: {folder_path}", file=sys.stderr)
        print(f"请先创建 {folder_path}/ 并把 JD 截图放进去", file=sys.stderr)
        print(f"或用 --folder 指定其他目录", file=sys.stderr)
        sys.exit(1)

    files = find_input_files(folder)
    if not files:
        print(f"在 {folder_path} 下未找到图片或 txt 文件", file=sys.stderr)
        sys.exit(1)

    # 过滤已有 jd_ 前缀的输出文件，避免二次处理
    raw_files = [f for f in files if not f.name.startswith("jd_")]
    if not raw_files:
        print(f"所有文件都已是 jd_ 前缀（说明已处理过），没有新文件需要 OCR")
        return

    print(f"找到 {len(raw_files)} 个待处理文件，开始...\n")

    for i, file_path in enumerate(raw_files, 1):
        base = file_path.stem        # 文件名（不含扩展名）

        if file_path.suffix.lower() in IMAGE_EXTS:
            print(f"  [{i}/{len(raw_files)}] OCR: {file_path.name} ...", flush=True)
            text = ocr_image(file_path)
        else:
            print(f"  [{i}/{len(raw_files)}] 读取: {file_path.name} ...")
            text = read_text_file(file_path)

        if args.preview:
            print(f"\n{'='*50}")
            print(f"  jd_{base}")
            print(f"{'='*50}")
            print(text)
            print()
        else:
            output_name = f"jd_{base}.txt"
            output_path = folder_path / output_name
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"    -> 已写入 {output_name}")

    summary = f"\n处理完成。共 {len(files)} 个文件"
    if not args.preview:
        summary += f"，结果在 {folder_path}/"
    print(summary)


if __name__ == "__main__":
    main()
