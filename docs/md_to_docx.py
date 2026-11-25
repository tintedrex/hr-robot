"""Convert simple project Markdown docs to Word (.docx)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt


def set_cell_shading(cell, fill: str) -> None:
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    shading.set(qn("w:val"), "clear")
    cell._tePr = cell._tc.get_or_add_tcPr()
    cell._tc.get_or_add_tcPr().append(shading)


def add_runs(paragraph, text: str) -> None:
    # Support **bold** and `code` segments
    parts = re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
        else:
            paragraph.add_run(part)


def is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line))


def parse_table_row(line: str) -> list[str]:
    # Protect escaped pipes inside cells (e.g. Jetson \| MCU)
    placeholder = "\u0000"
    protected = line.replace("\\|", placeholder)
    protected = protected.strip().strip("|")
    return [c.strip().replace(placeholder, "|") for c in protected.split("|")]


def convert(md_path: Path, docx_path: Path) -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    i = 0
    in_code = False
    code_lines: list[str] = []

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                in_code = False
                p = doc.add_paragraph()
                run = p.add_run("\n".join(code_lines))
                run.font.name = "Consolas"
                run.font.size = Pt(9)
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if line.strip() == "---":
            i += 1
            continue

        # Markdown image: ![alt](path)
        m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line.strip())
        if m_img:
            alt, rel = m_img.group(1), m_img.group(2)
            img_path = (md_path.parent / rel).resolve()
            if img_path.exists():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(str(img_path), width=Inches(6.0))
                if alt:
                    cap = doc.add_paragraph(alt)
                    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in cap.runs:
                        r.italic = True
                        r.font.size = Pt(9)
            else:
                p = doc.add_paragraph()
                add_runs(p, f"[Missing image: {rel}]")
            i += 1
            continue

        if line.startswith("# "):
            p = doc.add_heading(line[2:].strip(), level=0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            i += 1
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=1)
            i += 1
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=2)
            i += 1
            continue
        if line.startswith("#### "):
            doc.add_heading(line[5:].strip(), level=3)
            i += 1
            continue

        # Markdown table
        if "|" in line and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            rows = [parse_table_row(line)]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(parse_table_row(lines[i]))
                i += 1
            cols = max(len(r) for r in rows)
            # Normalize ragged markdown rows (e.g. trailing empty cells)
            normalized = [r + [""] * (cols - len(r)) for r in rows]
            table = doc.add_table(rows=len(normalized), cols=cols)
            table.style = "Table Grid"
            for r_idx, row in enumerate(normalized):
                for c_idx, cell_text in enumerate(row[:cols]):
                    cell = table.rows[r_idx].cells[c_idx]
                    cell.text = ""
                    p = cell.paragraphs[0]
                    add_runs(p, cell_text)
                    if r_idx == 0:
                        for run in p.runs:
                            run.bold = True
            doc.add_paragraph()
            continue

        # Numbered list
        m_num = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m_num:
            p = doc.add_paragraph(style="List Number")
            add_runs(p, m_num.group(2))
            i += 1
            continue

        # Bullet list
        if re.match(r"^[-*]\s+", line):
            p = doc.add_paragraph(style="List Bullet")
            add_runs(p, re.sub(r"^[-*]\s+", "", line))
            i += 1
            continue

        if not line.strip():
            i += 1
            continue

        p = doc.add_paragraph()
        add_runs(p, line.strip())
        i += 1

    docx_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(docx_path)
    print(f"Wrote {docx_path}")


def main() -> int:
    docs = Path(__file__).resolve().parent
    pairs = [
        (docs / "HR-SRS-SW-v0.1.md", docs / "HR-SRS-SW-v0.1.docx"),
        (docs / "HR-SAD-v0.1.md", docs / "HR-SAD-v0.1.docx"),
        (docs / "HR-ICD-v0.1.md", docs / "HR-ICD-v0.1.docx"),
        (docs / "HR-TEST-SW-v0.1.md", docs / "HR-TEST-SW-v0.1.docx"),
        (docs / "HR-SAFE-v0.1.md", docs / "HR-SAFE-v0.1.docx"),
        (docs / "HR-SRS-SW-v0.2.md", docs / "HR-SRS-SW-v0.2.docx"),
        (docs / "HR-SAD-v0.2.md", docs / "HR-SAD-v0.2.docx"),
        (docs / "HR-ICD-v0.2.md", docs / "HR-ICD-v0.2.docx"),
        (docs / "HR-TEST-SW-v0.2.md", docs / "HR-TEST-SW-v0.2.docx"),
        (docs / "HR-SAFE-v0.2.md", docs / "HR-SAFE-v0.2.docx"),
        (docs / "HR-SIM-SETUP-v0.1.md", docs / "HR-SIM-SETUP-v0.1.docx"),
    ]
    for md, docx in pairs:
        if not md.exists():
            print(f"Missing {md}", file=sys.stderr)
            return 1
        convert(md, docx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
