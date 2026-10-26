from __future__ import annotations

import json
import re
from pathlib import Path

import fitz
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "private" / "sources"
IMAGE_ROOT = ROOT / "private" / "extracted" / "images"
DATA_ROOT = ROOT / "src" / "data"
TEXT_ROOT = ROOT / "private" / "review"

SECTION_HINTS = (
    ("steering", ("steering", "ackermann", "tie rod")),
    ("braking", ("brake", "caliper", "disc")),
    ("drivetrain", ("transmission", "shaft", "sprocket", "motor")),
    ("chassis", ("chassis", "impact", "torsional")),
    ("electrical", ("battery", "electrical", "wiring")),
    ("assembly", ("assembly", "pedal", "seat mount")),
)
SENSITIVE_HINTS = (
    "dimension",
    "wheelbase",
    "track width",
    "weight",
    "mass",
    "voltage",
    "current",
    "battery",
    "bms",
    "controller",
    "fuse",
    "contactor",
    "turning radius",
    "stopping distance",
    "braking force",
    "torque",
    "impact load",
    "factor of safety",
)
IDENTITY_HINTS = (
    "morphine motorsport",
    "e-zeall",
    "participant id",
    "reference no",
    "date of submission",
    "rulebook_",
)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def guess_section(text: str) -> str:
    lowered = text.lower()
    for section, hints in SECTION_HINTS:
        if any(hint in lowered for hint in hints):
            return section
    return "overview"


def export_png(data: bytes, output: Path) -> None:
    from io import BytesIO

    with Image.open(BytesIO(data)) as image:
        image.convert("RGBA").save(output, "PNG", optimize=True)


def main() -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    TEXT_ROOT.mkdir(parents=True, exist_ok=True)

    figures: list[dict[str, object]] = []
    inventory_lines: list[str] = []
    summary: list[tuple[str, int]] = []

    for source in sorted(SOURCES.glob("*.pdf")):
        document = fitz.open(source)
        doc_slug = slugify(source.stem)
        document_image_dir = IMAGE_ROOT / doc_slug
        document_image_dir.mkdir(parents=True, exist_ok=True)
        text_lines: list[str] = []
        image_count = 0
        figure_pages: list[int] = []
        calculation_pages: list[int] = []
        table_pages: list[int] = []
        sensitive_pages: list[int] = []
        identity_pages: list[int] = []
        scope: list[str] = []
        inventory_lines.append(
            f"## {source.name}\n\n"
            f"- Pages: {len(document)}\n"
            f"- Metadata: title={document.metadata.get('title')!r}; "
            f"author={document.metadata.get('author')!r}; "
            f"created={document.metadata.get('creationDate')!r}\n"
        )

        for page_index, page in enumerate(document):
            page_number = page_index + 1
            page_text = page.get_text("text")
            page_label = re.sub(r"\s+", " ", page_text).strip()
            text_lines.append(f"\n\n===== PAGE {page_number} =====\n\n{page_text}")
            image_entries = page.get_images(full=True)
            lowered = page_text.casefold()
            if image_entries or re.search(r"\bfig(?:ure)?[\s.]*(?:\d|[a-z])", lowered):
                figure_pages.append(page_number)
            if re.search(r"calculation|formulation|equation|result table|results", lowered):
                calculation_pages.append(page_number)
            if re.search(r"\btable\b|\bindex\b", lowered):
                table_pages.append(page_number)
            if any(hint in lowered for hint in SENSITIVE_HINTS):
                sensitive_pages.append(page_number)
            if any(hint in lowered for hint in IDENTITY_HINTS) or re.search(
                r"\b(?:19|20)\d{2}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", page_text
            ):
                identity_pages.append(page_number)
            heading = next(
                (
                    line.strip()
                    for line in page_text.splitlines()
                    if len(line.strip()) > 3 and line.strip().isupper()
                ),
                "",
            )
            if heading and heading not in scope:
                scope.append(heading[:90])

            for image_number, image_entry in enumerate(image_entries, start=1):
                extracted = document.extract_image(image_entry[0])
                output = document_image_dir / f"p{page_number}_img{image_number}.png"
                export_png(extracted["image"], output)
                figures.append(
                    {
                        "id": f"{doc_slug}-p{page_number}-img{image_number}",
                        "file": str(output.relative_to(ROOT)).replace("\\", "/"),
                        "section": guess_section(page_label),
                        "caption": f"Source figure from page {page_number}",
                        "source_doc": source.name,
                        "source_page": page_number,
                        "needs_crop": True,
                        "public": False,
                    }
                )
                image_count += 1

            if not image_entries and len(page.get_drawings()) >= 12:
                output = document_image_dir / f"p{page_number}_img1.png"
                page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False).save(output)
                figures.append(
                    {
                        "id": f"{doc_slug}-p{page_number}-vector",
                        "file": str(output.relative_to(ROOT)).replace("\\", "/"),
                        "section": guess_section(page_label),
                        "caption": f"Vector page from page {page_number}",
                        "source_doc": source.name,
                        "source_page": page_number,
                        "needs_crop": True,
                        "public": False,
                    }
                )
                image_count += 1

        (TEXT_ROOT / f"{doc_slug}-source-text.txt").write_text(
            "".join(text_lines), encoding="utf-8"
        )
        inventory_lines.append(f"- Extracted image/vector pages: {image_count}\n")
        inventory_lines.extend(
            [
                f"- Scope headings: {', '.join(scope) or 'not detected'}",
                f"- Figure/image pages: {', '.join(map(str, figure_pages)) or 'none'}",
                f"- Calculation/result pages: {', '.join(map(str, calculation_pages)) or 'none'}",
                f"- Table/index pages: {', '.join(map(str, table_pages)) or 'none'}",
                f"- Sensitive-content pages: {', '.join(map(str, sensitive_pages)) or 'none'}",
                f"- Event/date/ID pages: {', '.join(map(str, identity_pages)) or 'none'}",
                "- Sensitive items: vehicle dimensions and mass; steering/braking/drivetrain results; "
                "battery, BMS, controller, fuse, and contactor limits; FEA loads, outputs, and claims.",
                "- Event/date/ID items: team, organizer, institution, participant/reference IDs, "
                "submission dates, event-year marks, and document metadata.",
                "",
            ]
        )
        summary.append((source.name, image_count))

    (DATA_ROOT / "figures.json").write_text(
        json.dumps(figures, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    (TEXT_ROOT / "inventory.md").write_text(
        "# Source inventory\n\n"
        "> Private working document. Source names, dates, IDs, and values are not public.\n\n"
        + "\n".join(inventory_lines),
        encoding="utf-8",
    )

    print("Document                                      | Extracted images/vector pages")
    print("----------------------------------------------|------------------------------")
    for name, count in summary:
        print(f"{name[:44]:44} | {count:>4}")
    print(f"Total figures indexed: {len(figures)}")


if __name__ == "__main__":
    main()
