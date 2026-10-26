from __future__ import annotations

import json
import re
from pathlib import Path

import pytesseract
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SIMULATIONS_PATH = ROOT / "src" / "data" / "simulations.json"
BANNED_PATH = ROOT / "private" / "review" / "banned_strings.txt"
PUBLIC_ROOT = ROOT / "public"

if Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe").exists():
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DATE_PATTERN = re.compile(r"(?<!\d)(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:19|20)\d{2})(?!\d)")
ID_PATTERN = re.compile(r"\b[A-Z]{2,}/[A-Z0-9-]{3,}(?:/[A-Z0-9-]+)*\b", re.IGNORECASE)


def main() -> None:
    simulations = json.loads(SIMULATIONS_PATH.read_text(encoding="utf-8"))
    banned = [
        line.strip().casefold()
        for line in BANNED_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    for simulation in simulations:
        source = ROOT / simulation["source"]
        output = PUBLIC_ROOT / simulation["file"]
        if not source.is_file():
            raise FileNotFoundError(f"Simulation source image is missing: {source}")

        with Image.open(source) as image:
            image = image.convert("RGB")
            left, top, right, bottom = simulation["crop"]
            width, height = image.size
            image = image.crop(
                (
                    round(width * left),
                    round(height * top),
                    round(width * right),
                    round(height * bottom),
                )
            )
            if max(image.size) > 1600:
                scale = 1600 / max(image.size)
                image = image.resize(
                    (round(image.width * scale), round(image.height * scale)),
                    Image.Resampling.LANCZOS,
                )
            output.parent.mkdir(parents=True, exist_ok=True)
            image.save(output, "WEBP", quality=88, method=6)

        with Image.open(output) as cleaned:
            extracted = pytesseract.image_to_string(cleaned)
            searchable = extracted.casefold()
            hits = [value for value in banned if value in searchable]
            if DATE_PATTERN.search(searchable) or ID_PATTERN.search(extracted):
                hits.append("date or ID pattern")
            if hits:
                output.unlink()
                raise ValueError(
                    f"Simulation image {simulation['id']} contains readable private text: "
                    f"{', '.join(sorted(set(hits)))}"
                )
            simulation["width"], simulation["height"] = cleaned.size

    SIMULATIONS_PATH.write_text(
        json.dumps(simulations, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Prepared and OCR-screened {len(simulations)} ANSYS simulation images.")


if __name__ == "__main__":
    main()
