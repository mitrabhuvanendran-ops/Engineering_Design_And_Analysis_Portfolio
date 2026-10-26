from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "src" / "data"
PUBLIC_ROOT = ROOT / "public"


def public_metric(metric: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in metric.items()
        if key not in {"public", "source_doc", "source_page", "hold_reason"}
    }


def main() -> None:
    site = json.loads((DATA_ROOT / "site.json").read_text(encoding="utf-8"))
    parameters = json.loads((DATA_ROOT / "parameters.json").read_text(encoding="utf-8"))
    simulations = json.loads((DATA_ROOT / "simulations.json").read_text(encoding="utf-8"))
    wireframes = json.loads((DATA_ROOT / "wireframes.json").read_text(encoding="utf-8"))
    figures = json.loads((DATA_ROOT / "figures.json").read_text(encoding="utf-8"))

    public_figures = {
        str(figure["id"]): figure
        for figure in figures
        if figure.get("public") is True
    }
    simulation_figures = {
        str(simulation["id"]): simulation for simulation in simulations
    }
    visual_figures = {str(item["id"]): item for item in wireframes}

    def public_figure(figure_id: str, alt: str) -> dict[str, object]:
        simulation = simulation_figures.get(figure_id)
        if simulation is not None:
            return {
                "src": "./" + str(simulation["file"]).replace("\\", "/"),
                "width": simulation["width"],
                "height": simulation["height"],
                "alt": alt,
            }
        visual = visual_figures.get(figure_id)
        if visual is not None:
            return {
                "src": "./" + str(visual["file"]).replace("\\", "/"),
                "width": visual["width"],
                "height": visual["height"],
                "alt": alt,
            }
        figure = public_figures.get(figure_id)
        if figure is None:
            raise ValueError(f"Figure {figure_id} is not cleared for public use.")
        return {
            "src": "./" + str(figure["file"]).replace("\\", "/"),
            "width": figure["width"],
            "height": figure["height"],
            "alt": alt,
        }

    public_hero = {
        key: value
        for key, value in site["hero"].items()
        if key not in {"imageId", "imageAlt"}
    }
    public_hero["image"] = public_figure(
        str(site["hero"]["imageId"]), str(site["hero"]["imageAlt"])
    )

    metrics_by_id = {
        metric["id"]: public_metric(metric)
        for metric in parameters
        if metric.get("public") is True
    }

    public_subsystems = []
    for subsystem in site["subsystems"]:
        public_ergonomics = subsystem.get("ergonomics")
        if public_ergonomics is not None:
            public_ergonomics = {
                **public_ergonomics,
                "views": [
                    {
                        key: value
                        for key, value in view.items()
                        if key not in {"imageId", "alt"}
                    }
                    | {"image": public_figure(str(view["imageId"]), str(view["caption"]))}
                    for view in public_ergonomics["views"]
                ],
            }

        cases = [
            {
                key: value
                for key, value in case.items()
                if key not in {"imageId", "alt"}
            }
            | {"image": public_figure(str(case["imageId"]), str(case["caption"]))}
            for case in subsystem["simulations"]
        ]

        cad_visuals = []
        for visual in subsystem.get("cadVisuals", []):
            cad_visuals.append({
                "title": visual["title"],
                "caption": visual["caption"],
                "image": public_figure(str(visual["imageId"]), str(visual["alt"])),
            })

        subsystem_calcs = [
            metrics_by_id[calc_id]
            for calc_id in subsystem.get("calculationIds", [])
            if calc_id in metrics_by_id
        ]

        public_subsystem = {
            "id": subsystem["id"],
            "title": subsystem["title"],
            "subtitle": subsystem["subtitle"],
            "specs": subsystem.get("specs", []),
            "designTitle": subsystem["designTitle"],
            "design": subsystem["design"],
            "approach": subsystem["approach"],
            "cadVisuals": cad_visuals,
            "simulations": cases,
            "calculations": subsystem_calcs
        }
        if "wireframeId" in subsystem and subsystem["wireframeId"]:
            public_subsystem["wireframe"] = public_figure(
                str(subsystem["wireframeId"]), str(subsystem.get("wireframeAlt", ""))
            )
        if public_ergonomics is not None:
            public_subsystem["ergonomics"] = public_ergonomics

        public_subsystems.append(public_subsystem)

    public_data = {
        "title": site["title"],
        "hero": public_hero,
        "subsystems": public_subsystems,
        "metrics": list(metrics_by_id.values()),
        "footerNote": site["footerNote"],
    }

    PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)
    output = PUBLIC_ROOT / "site-data.json"
    output.write_text(json.dumps(public_data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    case_count = sum(len(item["simulations"]) for item in public_subsystems)
    calc_count = sum(len(item["calculations"]) for item in public_subsystems)
    cad_count = sum(len(item["cadVisuals"]) for item in public_subsystems)
    print(
        f"Wrote sanitized public data: {len(public_subsystems)} subsystems, "
        f"{cad_count} CAD visuals, {case_count} simulation images, {calc_count} calculations."
    )


if __name__ == "__main__":
    main()