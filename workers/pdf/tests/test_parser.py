from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import UUID, uuid4

import fitz  # type: ignore[import-not-found,import-untyped]

from workers.common.pipeline import Pipeline
from workers.common.task import TaskPayload, TaskType
from workers.pdf.downloader import DownloadResult
from workers.pdf.parser import ParsedPdf, PdfParser
from workers.pdf.steps import DownloadPdfStep, ParsePdfStep


def _build_sample_pdf(pdf_path: Path) -> None:
    document = fitz.open()

    page_one = document.new_page(width=595, height=842)
    page_one.insert_textbox(
        fitz.Rect(72, 56, 523, 120),
        "Structured Parsing for Paper Intelligence",
        fontsize=22,
        fontname="Times-Bold",
        align=fitz.TEXT_ALIGN_CENTER,
    )
    page_one.insert_text(
        (72, 146),
        "Abstract",
        fontsize=13,
        fontname="Times-Bold",
    )
    page_one.insert_textbox(
        fitz.Rect(72, 158, 523, 220),
        (
            "This paper studies parser quality for academic PDFs. "
            "It extracts section structure, references, and figure captions "
            "for downstream enrichment workflows."
        ),
        fontsize=11,
        fontname="Times-Roman",
    )
    page_one.insert_text(
        (72, 266),
        "1 Introduction",
        fontsize=13,
        fontname="Times-Bold",
    )
    page_one.insert_textbox(
        fitz.Rect(72, 278, 280, 470),
        (
            "Left column first sentence explains the dataset. "
            "Left column second sentence stays before the right column content."
        ),
        fontsize=11,
        fontname="Times-Roman",
    )
    page_one.insert_textbox(
        fitz.Rect(315, 278, 523, 470),
        (
            "The right column continues the introduction after the left column content. "
            "It describes the two-column reading order heuristic."
        ),
        fontsize=11,
        fontname="Times-Roman",
    )

    page_two = document.new_page(width=595, height=842)
    page_two.insert_text(
        (72, 92),
        "2 Method",
        fontsize=13,
        fontname="Times-Bold",
    )
    page_two.insert_textbox(
        fitz.Rect(72, 104, 280, 250),
        (
            "The parser groups blocks by page geometry and font size. "
            "This keeps section boundaries stable across pages."
        ),
        fontsize=11,
        fontname="Times-Roman",
    )
    page_two.insert_textbox(
        fitz.Rect(315, 104, 523, 250),
        (
            "Figure captions are linked to the nearest overlapping image block. "
            "Structured JSON is emitted for later LLM enrichment."
        ),
        fontsize=11,
        fontname="Times-Roman",
    )

    pixmap = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 160, 110), False)
    pixmap.clear_with(0x4A90E2)
    page_two.insert_image(
        fitz.Rect(72, 300, 260, 430),
        pixmap=pixmap,
    )
    page_two.insert_text(
        (72, 448),
        "Figure 1: Parser architecture overview.",
        fontsize=10,
        fontname="Times-Italic",
    )
    page_two.insert_text(
        (72, 534),
        "References",
        fontsize=13,
        fontname="Times-Bold",
    )
    page_two.insert_textbox(
        fitz.Rect(72, 548, 523, 720),
        (
            "[1] Ada Lovelace. Analytical Engines for Science. 1843.\n"
            "[2] Grace Hopper. Compiler Design for Papers. 1952."
        ),
        fontsize=10,
        fontname="Times-Roman",
    )

    document.save(pdf_path)
    document.close()


def _parse_sample_pdf(tmp_path: Path) -> tuple[Path, PdfParser, ParsedPdf]:
    pdf_path = tmp_path / "2503.12345.pdf"
    _build_sample_pdf(pdf_path)
    parser = PdfParser(figure_output_dir=tmp_path / "figures")
    parsed_pdf = asyncio.run(
        parser.parse(
            pdf_path=str(pdf_path),
            arxiv_id="2503.12345",
        )
    )
    return pdf_path, parser, parsed_pdf


def test_parser_extracts_structured_text_from_academic_pdf(tmp_path: Path) -> None:
    _, _, parsed_pdf = _parse_sample_pdf(tmp_path)

    assert parsed_pdf.title == "Structured Parsing for Paper Intelligence"
    assert parsed_pdf.abstract.startswith("This paper studies parser quality for academic PDFs.")
    assert [section.header for section in parsed_pdf.sections] == [
        "1 Introduction",
        "2 Method",
    ]
    assert parsed_pdf.references == (
        "[1] Ada Lovelace. Analytical Engines for Science. 1843.",
        "[2] Grace Hopper. Compiler Design for Papers. 1952.",
    )
    assert parsed_pdf.page_count == 2
    assert "References" in parsed_pdf.full_text


def test_parser_keeps_two_column_content_in_reading_order(tmp_path: Path) -> None:
    _, _, parsed_pdf = _parse_sample_pdf(tmp_path)

    introduction = parsed_pdf.sections[0].content
    left_text = "Left column first sentence explains the dataset."
    right_text = "The right column continues the introduction after the left column content."

    assert left_text in introduction
    assert right_text in introduction
    assert introduction.index(left_text) < introduction.index(right_text)


def test_parser_extracts_figures_as_files_with_captions(tmp_path: Path) -> None:
    _, _, parsed_pdf = _parse_sample_pdf(tmp_path)

    assert len(parsed_pdf.figures) == 1
    figure = parsed_pdf.figures[0]
    image_path = Path(figure.image_path)

    assert figure.figure_number == "1"
    assert figure.caption == "Figure 1: Parser architecture overview."
    assert figure.page_number == 2
    assert image_path.exists()
    assert image_path.suffix == ".png"
    assert image_path.read_bytes()


def test_parse_pdf_step_chains_after_download_step(tmp_path: Path) -> None:
    pdf_path = tmp_path / "2503.12345.pdf"
    _build_sample_pdf(pdf_path)
    parser = PdfParser(figure_output_dir=tmp_path / "figures")
    paper_id = uuid4()

    class FakeDownloader:
        def __init__(self, stored_pdf_path: Path) -> None:
            self.stored_pdf_path = stored_pdf_path
            self.calls: list[tuple[str, UUID | None]] = []

        async def fetch_and_store(
            self,
            *,
            arxiv_id: str,
            paper_id: UUID | None = None,
        ) -> DownloadResult:
            self.calls.append((arxiv_id, paper_id))
            return DownloadResult(
                arxiv_id=arxiv_id,
                pdf_path=str(self.stored_pdf_path),
                pdf_status="stored",
                sha256="deadbeef",
                size_bytes=self.stored_pdf_path.stat().st_size,
                attempts=1,
            )

    downloader = FakeDownloader(pdf_path)
    pipeline = Pipeline(
        [
            DownloadPdfStep(downloader=downloader),  # type: ignore[arg-type]
            ParsePdfStep(parser=parser),
        ]
    )
    task = TaskPayload(
        task_type=TaskType.FETCH,
        workspace_id=uuid4(),
        paper_id=paper_id,
        idempotency_key="pdf-parse-flow-001",
        payload={"arxiv_id": "2503.12345"},
    )

    results = asyncio.run(pipeline.run_flow(task))

    assert len(results) == 2
    assert downloader.calls == [("2503.12345", paper_id)]
    assert results[1].result["final"]["pdf_parse_status"] == "parsed"
    assert results[1].result["final"]["parsed_pdf"]["title"] == (
        "Structured Parsing for Paper Intelligence"
    )
    assert results[1].result["next_task_type"] == "enrich"
