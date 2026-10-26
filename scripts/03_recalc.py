from __future__ import annotations

import json
import re
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "private" / "sources" / "MMS design report (1).pdf"
PARAMETERS = ROOT / "src" / "data" / "parameters.json"
HELD_PARAMETERS = ROOT / "private" / "review" / "held_parameters.json"


def value_after(label: str, text: str) -> float | int:
    normalized = " ".join(text.split())
    matches = list(re.finditer(
        rf"{re.escape(label)}\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)",
        normalized,
        re.IGNORECASE,
    ))
    if not matches:
        raise ValueError(f"Could not locate {label!r} in the source table.")
    value = float(matches[-1].group(1))
    return int(value) if value.is_integer() else value


def main() -> None:
    document = fitz.open(SOURCE)
    transmission_page = document[8].get_text("text")
    rolling_page = document[8].get_text("text")
    source_values = {
        "drive_teeth": value_after("Drive Sprocket", transmission_page),
        "driven_teeth": value_after("Driven Sprocket", transmission_page),
        "rolling_resistance_N": value_after("Rolling Resistance(Fr)", rolling_page),
        "gradient_resistance_N": value_after("Gradient Resistance(Fg)", rolling_page),
        "aerodynamic_drag_N": value_after("Aerodynamic Drag Force(Fad)", rolling_page),
    }
    ratio = source_values["driven_teeth"] / source_values["drive_teeth"]
    tractive_force = (
        source_values["rolling_resistance_N"]
        + source_values["gradient_resistance_N"]
        + source_values["aerodynamic_drag_N"]
    )
    results = [
        {
            "id": "sprocket_ratio",
            "section": "drivetrain",
            "label": "Sprocket ratio",
            "symbol": "i",
            "equation_tex": "i = N_{driven} / N_{drive}",
            "inputs": [
                {"symbol": "N_{driven}", "value": source_values["driven_teeth"], "unit": "teeth"},
                {"symbol": "N_{drive}", "value": source_values["drive_teeth"], "unit": "teeth"},
            ],
            "result": round(ratio, 3),
            "unit": "—",
            "status": "recalculated",
            "public": True,
            "hold_reason": None,
            "source_doc": "design_report",
            "source_page": 9,
        },
        {
            "id": "tractive_force_sum",
            "section": "drivetrain",
            "label": "Tractive-force sum",
            "symbol": "F_t",
            "equation_tex": "F_t = F_r + F_g + F_{ad}",
            "inputs": [
                {"symbol": "F_r", "value": source_values["rolling_resistance_N"], "unit": "N"},
                {"symbol": "F_g", "value": source_values["gradient_resistance_N"], "unit": "N"},
                {"symbol": "F_{ad}", "value": source_values["aerodynamic_drag_N"], "unit": "N"},
            ],
            "result": round(tractive_force, 3),
            "unit": "N",
            "status": "recalculated",
            "public": True,
            "hold_reason": None,
            "source_doc": "design_report",
            "source_page": 9,
        },
    ]
    held = json.loads(HELD_PARAMETERS.read_text(encoding="utf-8"))
    PARAMETERS.write_text(json.dumps(held + results, indent=2) + "\n", encoding="utf-8")
    print("Formula                                  | Inputs                  | Recomputed | Source")
    print("-----------------------------------------|-------------------------|------------|--------")
    print(
        f"42 / 15                                 | 42 teeth / 15 teeth     | {ratio:>10.3f} | 2.8"
    )
    print(
        f"38.259 + 0 + 66.85                       | N + N + N               | {tractive_force:>10.3f} | 105.109 N"
    )


if __name__ == "__main__":
    main()
