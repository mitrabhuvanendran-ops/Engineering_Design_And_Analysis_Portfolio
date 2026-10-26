from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytesseract
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BANNED_PATH = ROOT / "private" / "review" / "banned_strings.txt"

if Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe").exists():
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-](?:19|20)\d{2}|(?:19|20)\d{2}-\d{1,2}-\d{1,2})\b"
)
YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")
ID_PATTERN = re.compile(r"\b[A-Z]{2,}/[A-Z0-9]{4,}/[A-Z]{2,}/\d{4,}\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(
    r"(?<!\w)\+\d{1,3}[\s.-]\d{4,5}[\s.-]\d{4,5}(?!\w)"
    r"|(?<!\w)[6-9]\d{9}(?!\w)"
    r"|(?<!\w)\d{3}[-.]\d{3}[-.]\d{4}(?!\w)"
)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def main() -> int:
    if not DIST.is_dir():
        print("ERROR: dist/ does not exist; run the production build first.")
        return 1

    banned = [
        line.strip().casefold()
        for line in BANNED_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    failures: list[str] = []
    scanned = 0

    for path in sorted(DIST.rglob("*")):
        if not path.is_file():
            continue
        scanned += 1
        relative = path.relative_to(DIST).as_posix()
        if "private" in relative.casefold() or "sources" in relative.casefold():
            failures.append(f"private path in build: {relative}")

        filename_text = relative.casefold()
        if any(value in filename_text for value in banned):
            failures.append(f"banned filename: {relative}")
        if DATE_PATTERN.search(relative) or ID_PATTERN.search(relative):
            failures.append(f"date/ID pattern in filename: {relative}")

        if path.suffix.casefold() in IMAGE_SUFFIXES:
            with Image.open(path) as image:
                extracted = pytesseract.image_to_string(image)
                metadata = " ".join(str(value) for value in image.getexif().values())
            searchable = f"{extracted}\n{metadata}".casefold()
            failures.extend(
                f"image text/metadata hit in {relative}: {value}"
                for value in banned
                if value in searchable
            )
            if DATE_PATTERN.search(searchable) or YEAR_PATTERN.search(searchable) or ID_PATTERN.search(extracted):
                failures.append(f"date/ID pattern in image: {relative}")
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = ""
        searchable = content.casefold()
        failures.extend(
            f"banned text in {relative}: {value}" for value in banned if value in searchable
        )
        if DATE_PATTERN.search(content) or ID_PATTERN.search(content):
            failures.append(f"date/ID pattern in {relative}")
        if EMAIL_PATTERN.search(content) or PHONE_PATTERN.search(content):
            failures.append(f"email/phone pattern in {relative}")

        if path.suffix.casefold() == ".json":
            try:
                payload = json.loads(content)
            except json.JSONDecodeError as error:
                failures.append(f"invalid JSON in {relative}: {error}")
                continue

            def has_private_false(value: object) -> bool:
                if isinstance(value, dict):
                    return value.get("public") is False or any(
                        has_private_false(item) for item in value.values()
                    )
                if isinstance(value, list):
                    return any(has_private_false(item) for item in value)
                return False

            if has_private_false(payload):
                failures.append(f"public:false JSON entry in {relative}")

    if failures:
        print(f"Privacy audit FAILED: scanned {scanned} files.")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Privacy audit PASSED: scanned {scanned} dist files; no private data, OCR, ID, date, email, or phone hits.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
