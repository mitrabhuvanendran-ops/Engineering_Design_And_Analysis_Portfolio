from __future__ import annotations

import json
import re
from pathlib import Path

import pytesseract
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURES_PATH = ROOT / "src" / "data" / "figures.json"
BANNED_PATH = ROOT / "private" / "review" / "banned_strings.txt"
FLAGS_PATH = ROOT / "private" / "review" / "figure_flags.md"
PUBLIC_ROOT = ROOT / "public" / "figures"

if Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe").exists():
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

CANDIDATES = {
    "cad-model-report-template-ezeallracing-p7-img2": ("kart-assembly.webp", 0),
    "cad-model-report-template-ezeallracing-p8-img1": ("chassis.webp", 0),
    "cad-model-report-template-ezeallracing-p8-img2": ("assembly-solid.webp", 0),
    "cad-model-report-template-ezeallracing-p8-img3": ("assembly-wireframe.webp", 48),
    "cad-model-report-template-ezeallracing-p9-img1": ("steering.webp", 0),
    "cad-model-report-template-ezeallracing-p10-img1": ("braking.webp", 0),
    "cad-model-report-template-ezeallracing-p11-img1": ("drivetrain.webp", 0),
    "cad-model-report-template-ezeallracing-p12-img1": ("pedals.webp", 48),
    "cad-model-report-template-ezeallracing-p13-img1": ("seat-mount.webp", 0),
    "cad-model-report-template-ezeallracing-p14-img1": ("battery-mount.webp", 0),
}

DATE_PATTERN = re.compile(r"(?<!\d)(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:19|20)\d{2})(?!\d)")
ID_PATTERN = re.compile(r"\b[A-Z]{2,}/[A-Z0-9-]{3,}(?:/[A-Z0-9-]+)*\b", re.IGNORECASE)


def main() -> None:
    figures: list[dict[str, object]] = json.loads(FIGURES_PATH.read_text(encoding="utf-8"))
    banned = [
        line.strip().casefold()
        for line in BANNED_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_id = {str(figure["id"]): figure for figure in figures}
    PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)
    flags: list[str] = ["# Figure privacy flags", "", "OCR was run on each selected, cleaned WebP."]

    for figure_id, (output_name, crop_bottom) in CANDIDATES.items():
        figure = by_id[figure_id]
        source_file = str(figure.get("source_file", ""))
        if not source_file or not (ROOT / source_file).is_file():
            match = re.search(r"-p(\d+)-img(\d+)$", figure_id)
            if not match:
                raise ValueError(f"Cannot resolve original image for {figure_id}.")
            doc_slug = figure_id[: match.start()]
            source_file = (
                f"private/extracted/images/{doc_slug}/"
                f"p{match.group(1)}_img{match.group(2)}.png"
            )
        figure["source_file"] = source_file
        source = ROOT / source_file
        output = PUBLIC_ROOT / output_name

        with Image.open(source) as image:
            image = image.convert("RGB")
            if crop_bottom:
                image = image.crop((0, 0, image.width, image.height - crop_bottom))
            if max(image.size) > 2000:
                scale = 2000 / max(image.size)
                image = image.resize(
                    (round(image.width * scale), round(image.height * scale)),
                    Image.Resampling.LANCZOS,
                )
            image.save(output, "WEBP", quality=88, method=6)

        with Image.open(output) as cleaned:
            text = pytesseract.image_to_string(cleaned)
            exif_values = " ".join(str(value) for value in cleaned.getexif().values())
            width, height = cleaned.size

        searchable = f"{text}\n{exif_values}".casefold()
        hits = [value for value in banned if value in searchable]
        if DATE_PATTERN.search(searchable):
            hits.append("date/year pattern")
        if ID_PATTERN.search(text):
            hits.append("ID pattern")

        if hits:
            figure["public"] = False
            figure["hold_reason"] = ", ".join(sorted(set(hits)))
            output.unlink()
            flags.append(f"- `{output_name}`: held ({figure['hold_reason']}).")
        else:
            figure["file"] = f"figures/{output_name}"
            figure["needs_crop"] = False
            figure["public"] = True
            figure["width"] = width
            figure["height"] = height
            figure.pop("hold_reason", None)
            flags.append(f"- `{output_name}`: OCR clear; visually reviewed.")

    FIGURES_PATH.write_text(json.dumps(figures, indent=2) + "\n", encoding="utf-8")
    FLAGS_PATH.write_text("\n".join(flags) + "\n", encoding="utf-8")
    print(f"Cleaned {len(CANDIDATES)} candidate figures; see private/review/figure_flags.md.")


if __name__ == "__main__":
    main()
