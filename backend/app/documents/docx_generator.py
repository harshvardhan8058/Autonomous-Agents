"""DOCX Generator — renders the executed plan into a professional document."""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

from app.schemas.models import Plan, TaskExecution
from app.tools.dates import timestamp_display
from app.tools.timeline import build_timeline
from app.tools.titles import document_title

_ACCENT = RGBColor(0x1F, 0x3A, 0x5F)
_MUTED = RGBColor(0x6B, 0x72, 0x80)


def generate_docx(
    plan: Plan, executions: list[TaskExecution], output_path: Path
) -> None:
    doc = Document()
    _style_base(doc)

    _title_page(doc, plan)
    _table_of_contents(doc)
    _executive_summary(doc, plan)
    _timeline_table(doc, plan)
    _sections(doc, executions)
    _footer(doc)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))


def _style_base(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    for level, size in (("Heading 1", 18), ("Heading 2", 14)):
        style = doc.styles[level]
        style.font.color.rgb = _ACCENT
        style.font.size = Pt(size)


def _title_page(doc: Document, plan: Plan) -> None:
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(document_title(plan.goal))
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = _ACCENT

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = subtitle.add_run(f"Generated {timestamp_display()}")
    sub_run.font.size = Pt(11)
    sub_run.font.color.rgb = _MUTED
    doc.add_page_break()


def _table_of_contents(doc: Document) -> None:
    doc.add_heading("Table of Contents", level=1)
    paragraph = doc.add_paragraph()
    fld = paragraph._p.makeelement(qn("w:fldSimple"), {})
    fld.set(qn("w:instr"), 'TOC \\o "1-2" \\h \\z \\u')
    paragraph._p.append(fld)
    note = doc.add_paragraph()
    note_run = note.add_run("Right-click and select “Update Field” to populate.")
    note_run.font.size = Pt(9)
    note_run.font.color.rgb = _MUTED
    doc.add_page_break()


def _executive_summary(doc: Document, plan: Plan) -> None:
    doc.add_heading("Executive Summary", level=1)
    doc.add_paragraph(plan.goal)
    if plan.assumptions:
        doc.add_paragraph("Key assumptions:").runs[0].bold = True
        for assumption in plan.assumptions:
            doc.add_paragraph(assumption, style="List Bullet")


def _timeline_table(doc: Document, plan: Plan) -> None:
    doc.add_heading("Delivery Timeline", level=1)
    rows = build_timeline(plan.tasks)
    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 1"
    for i, header in enumerate(("Phase", "Priority", "Target")):
        cell = table.rows[0].cells[i]
        cell.text = header
        cell.paragraphs[0].runs[0].font.bold = True
    for row in rows:
        cells = table.add_row().cells
        cells[0].text = row["phase"]
        cells[1].text = row["priority"]
        cells[2].text = row["target"]


def _sections(doc: Document, executions: list[TaskExecution]) -> None:
    for execution in executions:
        if execution.section is None:
            continue
        doc.add_heading(execution.section.heading, level=1)
        for paragraph in execution.section.paragraphs:
            doc.add_paragraph(paragraph)
        for bullet in execution.section.bullets:
            doc.add_paragraph(bullet, style="List Bullet")


def _footer(doc: Document) -> None:
    footer = doc.sections[0].footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run(
        f"Autonomous AI Agent · Generated {timestamp_display()} · Confidential"
    )
    run.font.size = Pt(8)
    run.font.color.rgb = _MUTED
