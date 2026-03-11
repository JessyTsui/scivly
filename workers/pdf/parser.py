"""PDF parsing helpers for structured full-text extraction."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

import fitz  # type: ignore[import-not-found,import-untyped]

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIGURE_OUTPUT_PATH = REPO_ROOT / ".data" / "figures"
SAFE_DOCUMENT_ID_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")
ABSTRACT_PATTERN = re.compile(r"^abstract\b[:.\s-]*(.*)$", re.IGNORECASE)
REFERENCES_PATTERN = re.compile(r"^(references|bibliography)$", re.IGNORECASE)
FIGURE_CAPTION_PATTERN = re.compile(r"^(figure|fig\.?)\s*(\d+)?[:.\s-]+", re.IGNORECASE)
REFERENCE_ENTRY_PATTERN = re.compile(r"^(?:\[\d+\]|\d+\.)\s+")
SECTION_NUMBER_PATTERN = re.compile(r"^(?:\d+(?:\.\d+)*)\s+")
MIN_FIGURE_DIMENSION = 40.0


def _normalize_text(value: str) -> str:
    return " ".join(value.split())


def _bbox_width(bbox: tuple[float, float, float, float]) -> float:
    return bbox[2] - bbox[0]


def _bbox_height(bbox: tuple[float, float, float, float]) -> float:
    return bbox[3] - bbox[1]


def _bbox_center_x(bbox: tuple[float, float, float, float]) -> float:
    return (bbox[0] + bbox[2]) / 2.0


def _horizontal_overlap_ratio(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> float:
    overlap = max(0.0, min(first[2], second[2]) - max(first[0], second[0]))
    width = max(_bbox_width(first), _bbox_width(second), 1.0)
    return overlap / width


def _coerce_bbox(values: Any) -> tuple[float, float, float, float]:
    left, top, right, bottom = values
    return (
        float(left),
        float(top),
        float(right),
        float(bottom),
    )


@dataclass(slots=True, frozen=True)
class TextLine:
    text: str
    page_number: int
    bbox: tuple[float, float, float, float]
    max_font_size: float
    avg_font_size: float
    font_names: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class TextBlock:
    block_id: str
    text: str
    page_number: int
    bbox: tuple[float, float, float, float]
    lines: tuple[TextLine, ...]
    max_font_size: float
    avg_font_size: float
    font_names: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ParsedSection:
    header: str
    content: str

    def as_dict(self) -> dict[str, str]:
        return {
            "header": self.header,
            "content": self.content,
        }


@dataclass(slots=True, frozen=True)
class ParsedFigure:
    figure_number: str | None
    caption: str | None
    image_path: str
    page_number: int
    bbox: tuple[float, float, float, float]
    width: float
    height: float
    format: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "figure_number": self.figure_number,
            "caption": self.caption,
            "image_path": self.image_path,
            "page_number": self.page_number,
            "bbox": list(self.bbox),
            "width": self.width,
            "height": self.height,
            "format": self.format,
        }


@dataclass(slots=True, frozen=True)
class ParsedPdf:
    source_pdf_path: str
    title: str
    abstract: str
    sections: tuple[ParsedSection, ...]
    references: tuple[str, ...]
    figures: tuple[ParsedFigure, ...]
    full_text: str
    page_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_pdf_path": self.source_pdf_path,
            "title": self.title,
            "abstract": self.abstract,
            "sections": [section.as_dict() for section in self.sections],
            "references": list(self.references),
            "figures": [figure.as_dict() for figure in self.figures],
            "full_text": self.full_text,
            "page_count": self.page_count,
        }


class PdfParser:
    """Extract structured paper text and figures from a PDF."""

    def __init__(
        self,
        *,
        figure_output_dir: Path | str | None = None,
        s3_client: Any | None = None,
    ) -> None:
        self.figure_output_dir = Path(
            figure_output_dir or DEFAULT_FIGURE_OUTPUT_PATH
        ).expanduser()
        self._s3_client = s3_client

    async def parse(
        self,
        *,
        pdf_path: str,
        paper_id: UUID | None = None,
        arxiv_id: str | None = None,
    ) -> ParsedPdf:
        document_id = _resolve_document_id(
            pdf_path=pdf_path,
            paper_id=paper_id,
            arxiv_id=arxiv_id,
        )
        return await asyncio.to_thread(
            self._parse_sync,
            pdf_path,
            document_id,
        )

    def _parse_sync(self, pdf_path: str, document_id: str) -> ParsedPdf:
        document_bytes = self._read_pdf_bytes(pdf_path)
        with fitz.open(stream=document_bytes, filetype="pdf") as document:
            page_blocks = self._extract_text_blocks(document)
            figures, caption_block_ids = self._extract_figures(
                document=document,
                page_blocks=page_blocks,
                document_id=document_id,
            )
            ordered_lines = self._collect_ordered_lines(
                document=document,
                page_blocks=page_blocks,
                excluded_block_ids=caption_block_ids,
            )
            body_font_size = _estimate_body_font_size(ordered_lines)
            title = self._extract_title(
                document=document,
                page_blocks=page_blocks,
                body_font_size=body_font_size,
            )
            abstract_text, abstract_end_index = self._extract_abstract(
                lines=ordered_lines,
                body_font_size=body_font_size,
            )
            references, references_start_index = self._extract_references(ordered_lines)
            sections = self._extract_sections(
                lines=ordered_lines,
                start_index=abstract_end_index,
                end_index=references_start_index,
                body_font_size=body_font_size,
            )
            full_text = self._compose_full_text(
                title=title,
                abstract_text=abstract_text,
                sections=sections,
                references=references,
            )
            return ParsedPdf(
                source_pdf_path=pdf_path,
                title=title,
                abstract=abstract_text,
                sections=tuple(sections),
                references=tuple(references),
                figures=tuple(figures),
                full_text=full_text,
                page_count=document.page_count,
            )

    def _read_pdf_bytes(self, pdf_path: str) -> bytes:
        normalized_path = pdf_path.strip()
        if not normalized_path:
            raise ValueError("pdf_path is required")

        if normalized_path.startswith("s3://"):
            parsed = urlparse(normalized_path)
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")
            if not bucket or not key:
                raise ValueError(f"Unsupported S3 PDF path: {normalized_path}")
            response = self._get_s3_client().get_object(Bucket=bucket, Key=key)
            return bytes(response["Body"].read())

        path = Path(normalized_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"PDF does not exist: {normalized_path}")
        return path.read_bytes()

    def _get_s3_client(self) -> Any:
        if self._s3_client is None:
            try:
                import boto3  # type: ignore[import-not-found,import-untyped]
            except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional dependency state
                raise ModuleNotFoundError(
                    "boto3 is required to parse PDFs stored in S3/R2."
                ) from exc
            self._s3_client = boto3.client("s3")
        return self._s3_client

    def _extract_text_blocks(self, document: Any) -> dict[int, list[TextBlock]]:
        page_blocks: dict[int, list[TextBlock]] = {}
        for page_index in range(document.page_count):
            page = document[page_index]
            blocks: list[TextBlock] = []
            for block_index, block in enumerate(page.get_text("dict").get("blocks", [])):
                if block.get("type") != 0:
                    continue
                lines: list[TextLine] = []
                block_fonts: list[float] = []
                font_names: set[str] = set()
                for raw_line in block.get("lines", []):
                    spans = raw_line.get("spans", [])
                    line_text = _normalize_text(
                        "".join(span.get("text", "") for span in spans).strip()
                    )
                    if not line_text:
                        continue
                    span_sizes = [
                        float(span.get("size", 0.0))
                        for span in spans
                        if span.get("text", "").strip()
                    ]
                    line_font_names = tuple(
                        str(span.get("font", "")).strip()
                        for span in spans
                        if span.get("font", "")
                    )
                    if not span_sizes:
                        continue
                    lines.append(
                        TextLine(
                            text=line_text,
                            page_number=page_index + 1,
                            bbox=_coerce_bbox(raw_line["bbox"]),
                            max_font_size=max(span_sizes),
                            avg_font_size=sum(span_sizes) / len(span_sizes),
                            font_names=line_font_names,
                        )
                    )
                    block_fonts.extend(span_sizes)
                    font_names.update(line_font_names)
                if not lines:
                    continue
                block_text = "\n".join(line.text for line in lines)
                blocks.append(
                    TextBlock(
                        block_id=f"{page_index + 1}:{block_index}",
                        text=block_text,
                        page_number=page_index + 1,
                        bbox=_coerce_bbox(block["bbox"]),
                        lines=tuple(lines),
                        max_font_size=max(block_fonts),
                        avg_font_size=sum(block_fonts) / len(block_fonts),
                        font_names=tuple(sorted(font_names)),
                    )
                )
            page_blocks[page_index + 1] = blocks
        return page_blocks

    def _collect_ordered_lines(
        self,
        *,
        document: Any,
        page_blocks: dict[int, list[TextBlock]],
        excluded_block_ids: set[str],
    ) -> list[TextLine]:
        ordered_lines: list[TextLine] = []
        for page_number in range(1, document.page_count + 1):
            page = document[page_number - 1]
            ordered_blocks = _order_page_blocks(
                blocks=[
                    block
                    for block in page_blocks.get(page_number, [])
                    if block.block_id not in excluded_block_ids
                ],
                page_width=float(page.rect.width),
                page_height=float(page.rect.height),
            )
            for block in ordered_blocks:
                ordered_lines.extend(block.lines)
        return ordered_lines

    def _extract_title(
        self,
        *,
        document: Any,
        page_blocks: dict[int, list[TextBlock]],
        body_font_size: float,
    ) -> str:
        first_page = document[0]
        candidate_lines: list[TextLine] = []
        for block in _order_page_blocks(
            blocks=page_blocks.get(1, []),
            page_width=float(first_page.rect.width),
            page_height=float(first_page.rect.height),
        ):
            for line in block.lines:
                if line.bbox[1] > float(first_page.rect.height) * 0.35:
                    continue
                if ABSTRACT_PATTERN.match(line.text):
                    continue
                candidate_lines.append(line)

        if candidate_lines:
            max_font_size = max(line.max_font_size for line in candidate_lines)
            title_lines: list[str] = []
            for line in sorted(candidate_lines, key=lambda item: (item.bbox[1], item.bbox[0])):
                if line.max_font_size >= max(max_font_size - 1.0, body_font_size + 2.0):
                    title_lines.append(line.text)
                elif title_lines:
                    break
            title = _normalize_text(" ".join(title_lines))
            if title:
                return title

        metadata_title = _normalize_text(str(document.metadata.get("title", "")))
        return "" if metadata_title.lower() == "untitled" else metadata_title

    def _extract_abstract(
        self,
        *,
        lines: list[TextLine],
        body_font_size: float,
    ) -> tuple[str, int]:
        for index, line in enumerate(lines):
            match = ABSTRACT_PATTERN.match(line.text)
            if not match:
                continue
            abstract_parts: list[str] = []
            inline_abstract = _normalize_text(match.group(1))
            if inline_abstract:
                abstract_parts.append(inline_abstract)

            next_index = index + 1
            while next_index < len(lines):
                candidate = lines[next_index]
                candidate_text = candidate.text.strip()
                if not candidate_text:
                    next_index += 1
                    continue
                if REFERENCES_PATTERN.match(candidate_text):
                    break
                if FIGURE_CAPTION_PATTERN.match(candidate_text):
                    break
                if self._looks_like_section_header(candidate, body_font_size):
                    break
                abstract_parts.append(candidate_text)
                next_index += 1

            return _normalize_text(" ".join(abstract_parts)), next_index

        return "", 0

    def _extract_sections(
        self,
        *,
        lines: list[TextLine],
        start_index: int,
        end_index: int,
        body_font_size: float,
    ) -> list[ParsedSection]:
        sections: list[ParsedSection] = []
        current_header: str | None = None
        current_lines: list[str] = []

        for line in lines[start_index:end_index]:
            text = line.text.strip()
            if not text or FIGURE_CAPTION_PATTERN.match(text):
                continue
            if ABSTRACT_PATTERN.match(text):
                continue
            if self._looks_like_section_header(line, body_font_size):
                if current_header or current_lines:
                    content = _normalize_text(" ".join(current_lines))
                    if content:
                        sections.append(
                            ParsedSection(
                                header=current_header or "Body",
                                content=content,
                            )
                        )
                current_header = _normalize_text(text)
                current_lines = []
                continue
            current_lines.append(text)

        if current_header or current_lines:
            content = _normalize_text(" ".join(current_lines))
            if content:
                sections.append(
                    ParsedSection(
                        header=current_header or "Body",
                        content=content,
                    )
                )

        return sections

    def _extract_references(self, lines: list[TextLine]) -> tuple[list[str], int]:
        for index, line in enumerate(lines):
            if not REFERENCES_PATTERN.match(line.text.strip()):
                continue
            references: list[str] = []
            current_entry: list[str] = []
            for reference_line in lines[index + 1 :]:
                text = reference_line.text.strip()
                if not text:
                    continue
                if REFERENCE_ENTRY_PATTERN.match(text):
                    if current_entry:
                        references.append(_normalize_text(" ".join(current_entry)))
                    current_entry = [text]
                    continue
                current_entry.append(text)

            if current_entry:
                references.append(_normalize_text(" ".join(current_entry)))
            return references, index
        return [], len(lines)

    def _extract_figures(
        self,
        *,
        document: Any,
        page_blocks: dict[int, list[TextBlock]],
        document_id: str,
    ) -> tuple[list[ParsedFigure], set[str]]:
        figures: list[ParsedFigure] = []
        caption_block_ids: set[str] = set()
        output_dir = self.figure_output_dir / document_id
        output_dir.mkdir(parents=True, exist_ok=True)

        seen_instances: set[tuple[int, int, int, int, int, int]] = set()
        figure_index = 0
        for page_number in range(1, document.page_count + 1):
            page = document[page_number - 1]
            page_text_blocks = page_blocks.get(page_number, [])
            for image_ref in page.get_images(full=True):
                xref = int(image_ref[0])
                for rect in page.get_image_rects(xref, transform=False):
                    bbox = (
                        float(rect.x0),
                        float(rect.y0),
                        float(rect.x1),
                        float(rect.y1),
                    )
                    if (
                        _bbox_width(bbox) < MIN_FIGURE_DIMENSION
                        or _bbox_height(bbox) < MIN_FIGURE_DIMENSION
                    ):
                        continue

                    dedupe_key = (
                        page_number,
                        xref,
                        int(round(bbox[0])),
                        int(round(bbox[1])),
                        int(round(bbox[2])),
                        int(round(bbox[3])),
                    )
                    if dedupe_key in seen_instances:
                        continue
                    seen_instances.add(dedupe_key)

                    figure_index += 1
                    image_info = document.extract_image(xref)
                    image_ext = str(image_info.get("ext") or "png").lower()
                    image_path = output_dir / f"figure-{figure_index:03d}.{image_ext}"
                    image_path.write_bytes(bytes(image_info["image"]))

                    caption_block = _find_caption_block(
                        image_bbox=bbox,
                        blocks=page_text_blocks,
                        excluded_block_ids=caption_block_ids,
                    )
                    if caption_block is not None:
                        caption_block_ids.add(caption_block.block_id)
                        caption = _normalize_text(caption_block.text)
                    else:
                        caption = None

                    figure_number = None
                    if caption:
                        match = FIGURE_CAPTION_PATTERN.match(caption)
                        if match:
                            figure_number = match.group(2)

                    figures.append(
                        ParsedFigure(
                            figure_number=figure_number,
                            caption=caption,
                            image_path=str(image_path.resolve()),
                            page_number=page_number,
                            bbox=bbox,
                            width=_bbox_width(bbox),
                            height=_bbox_height(bbox),
                            format=image_ext,
                        )
                    )

        return figures, caption_block_ids

    def _compose_full_text(
        self,
        *,
        title: str,
        abstract_text: str,
        sections: list[ParsedSection],
        references: list[str],
    ) -> str:
        parts: list[str] = []
        if title:
            parts.append(title)
        if abstract_text:
            parts.append(f"Abstract\n{abstract_text}")
        for section in sections:
            parts.append(f"{section.header}\n{section.content}")
        if references:
            parts.append("References\n" + "\n".join(references))
        return "\n\n".join(parts)

    def _looks_like_section_header(self, line: TextLine, body_font_size: float) -> bool:
        text = _normalize_text(line.text)
        if not text:
            return False
        if REFERENCES_PATTERN.match(text):
            return True
        if FIGURE_CAPTION_PATTERN.match(text):
            return False
        if len(text) > 100 or text.endswith("."):
            return False
        if text.lower() in {"acknowledgements", "appendix"}:
            return True
        font_boost = line.max_font_size >= body_font_size + 0.8
        boldish = any("bold" in font.lower() for font in line.font_names)
        numbered = bool(SECTION_NUMBER_PATTERN.match(text))
        uppercase = text.isupper() and len(text.split()) <= 8
        title_case = (
            len(text.split()) <= 10
            and text[0].isupper()
            and text == text.title()
        )
        return numbered or uppercase or (font_boost and (boldish or title_case))


def _order_page_blocks(
    *,
    blocks: list[TextBlock],
    page_width: float,
    page_height: float,
) -> list[TextBlock]:
    if len(blocks) < 2:
        return sorted(blocks, key=lambda block: (block.bbox[1], block.bbox[0]))

    narrow_blocks = [
        block
        for block in blocks
        if _bbox_width(block.bbox) <= page_width * 0.48 and block.bbox[1] >= page_height * 0.18
    ]
    left_narrow = [
        block for block in narrow_blocks if _bbox_center_x(block.bbox) < page_width / 2.0
    ]
    right_narrow = [
        block for block in narrow_blocks if _bbox_center_x(block.bbox) >= page_width / 2.0
    ]
    has_two_columns = len(left_narrow) >= 2 and len(right_narrow) >= 2
    if not has_two_columns:
        return sorted(blocks, key=lambda block: (block.bbox[1], block.bbox[0]))

    column_start_y = min(block.bbox[1] for block in narrow_blocks)
    top_blocks: list[TextBlock] = []
    left_column: list[TextBlock] = []
    right_column: list[TextBlock] = []
    residual: list[TextBlock] = []

    for block in blocks:
        if block.bbox[1] < column_start_y:
            top_blocks.append(block)
            continue
        if _bbox_width(block.bbox) <= page_width * 0.55:
            if _bbox_center_x(block.bbox) < page_width / 2.0:
                left_column.append(block)
            else:
                right_column.append(block)
            continue
        residual.append(block)

    return (
        sorted(top_blocks, key=lambda block: (block.bbox[1], block.bbox[0]))
        + sorted(left_column, key=lambda block: (block.bbox[1], block.bbox[0]))
        + sorted(right_column, key=lambda block: (block.bbox[1], block.bbox[0]))
        + sorted(residual, key=lambda block: (block.bbox[1], block.bbox[0]))
    )


def _estimate_body_font_size(lines: list[TextLine]) -> float:
    candidate_sizes = [
        line.avg_font_size
        for line in lines
        if len(line.text.split()) >= 4 and len(line.text) <= 240
    ]
    if not candidate_sizes:
        return 11.0
    return float(median(candidate_sizes))


def _find_caption_block(
    *,
    image_bbox: tuple[float, float, float, float],
    blocks: list[TextBlock],
    excluded_block_ids: set[str],
) -> TextBlock | None:
    best_score = float("-inf")
    best_block: TextBlock | None = None

    for block in blocks:
        if block.block_id in excluded_block_ids:
            continue
        text = _normalize_text(block.text)
        if not text:
            continue

        block_bbox = block.bbox
        overlap = _horizontal_overlap_ratio(image_bbox, block_bbox)
        below_distance = block_bbox[1] - image_bbox[3]
        above_distance = image_bbox[1] - block_bbox[3]
        below = 0.0 <= below_distance <= 120.0
        above = 0.0 <= above_distance <= 80.0
        if not below and not above and not FIGURE_CAPTION_PATTERN.match(text):
            continue

        score = overlap * 100.0
        if FIGURE_CAPTION_PATTERN.match(text):
            score += 200.0
        if below:
            score += 75.0 - below_distance
        if above:
            score += 20.0 - above_distance
        if score > best_score:
            best_score = score
            best_block = block

    return best_block


def _resolve_document_id(
    *,
    pdf_path: str,
    paper_id: UUID | None,
    arxiv_id: str | None,
) -> str:
    if paper_id is not None:
        candidate = str(paper_id)
    elif arxiv_id:
        candidate = arxiv_id
    else:
        parsed = urlparse(pdf_path)
        candidate = Path(parsed.path or pdf_path).stem
    return SAFE_DOCUMENT_ID_PATTERN.sub("_", candidate).strip("_") or "paper"
