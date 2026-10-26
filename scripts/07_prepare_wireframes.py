from __future__ import annotations

import json
from pathlib import Path

import pytesseract
from PIL import Image, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
WIRE_FRAMES_PATH = ROOT / "src" / "data" / "wireframes.json"
BANNED_PATH = ROOT / "private" / "review" / "banned_strings.txt"
PUBLIC_ROOT = ROOT / "public"

if Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe").exists():
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def main() -> None:
    wireframes = json.loads(WIRE_FRAMES_PATH.read_text(encoding="utf-8"))
    banned = [
        line.strip().casefold()
        for line in BANNED_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    for diagram in wireframes:
        source_root = ROOT if diagram.get("treatment") == "source" else PUBLIC_ROOT
        source = source_root / diagram["source"]
        output = PUBLIC_ROOT / diagram["file"]
        if not source.is_file():
            raise FileNotFoundError(f"Cleared CAD source image is missing: {source}")

        with Image.open(source) as image:
            if diagram.get("treatment") == "source":
                line_art = image.convert("RGB")
            else:
                grayscale = ImageOps.grayscale(image)
                edges = ImageOps.autocontrast(grayscale.filter(ImageFilter.FIND_EDGES))
                line_art = edges.point(lambda value: 0 if value > 52 else 255)
            if max(line_art.size) > 1600:
                scale = 1600 / max(line_art.size)
                line_art = line_art.resize(
                    (round(line_art.width * scale), round(line_art.height * scale)),
                    Image.Resampling.LANCZOS,
                )
            output.parent.mkdir(parents=True, exist_ok=True)
            line_art.save(output, "WEBP", quality=90, method=6)

        with Image.open(output) as cleaned:
            searchable = pytesseract.image_to_string(cleaned).casefold()
            hits = [value for value in banned if value in searchable]
            if hits:
                output.unlink()
                raise ValueError(
                    f"Wireframe {diagram['id']} contains readable private text: "
                    f"{', '.join(hits)}"
                )
            diagram["width"], diagram["height"] = cleaned.size

    WIRE_FRAMES_PATH.write_text(
        json.dumps(wireframes, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Prepared and OCR-screened {len(wireframes)} subsystem wireframe diagrams.")


if __name__ == "__main__":
    main()
