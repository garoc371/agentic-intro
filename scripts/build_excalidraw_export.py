#!/usr/bin/env python3

import json
import math
import sys
from pathlib import Path


def estimate_text_box(text: str, font_size: int) -> tuple[float, float]:
    lines = text.split("\n")
    max_chars = max((len(line) for line in lines), default=0)
    width = max_chars * font_size * 0.52
    height = len(lines) * font_size * 1.25
    return width, height


def make_seed(counter: int) -> int:
    return 1000 + counter * 17


def base_element(element_type: str, element_id: str, x: float, y: float) -> dict:
    counter = base_element.counter
    base_element.counter += 1
    seed = make_seed(counter)
    return {
        "type": element_type,
        "id": element_id,
        "x": x,
        "y": y,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": seed,
        "version": 1,
        "versionNonce": seed + 5,
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
    }


base_element.counter = 1


def make_text(element_id: str, x: float, y: float, text: str, font_size: int, stroke_color: str = "#1e1e1e") -> dict:
    width, height = estimate_text_box(text, font_size)
    base = base_element("text", element_id, x, y)
    base.update(
        {
            "width": width,
            "height": height,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "hachure",
            "text": text,
            "fontSize": font_size,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "baseline": math.floor(font_size * 1.1),
            "containerId": None,
            "originalText": text,
            "lineHeight": 1.25,
        }
    )
    return base


def build_export(input_path: Path) -> dict:
    source = json.loads(input_path.read_text())
    raw_elements = source["elements"]
    export_elements = []

    for raw in raw_elements:
        raw_type = raw["type"]
        if raw_type == "cameraUpdate":
            continue

        if raw_type == "text":
            export_elements.append(
                make_text(
                    raw["id"],
                    raw["x"],
                    raw["y"],
                    raw["text"],
                    int(raw.get("fontSize", 20)),
                    raw.get("strokeColor", "#1e1e1e"),
                )
            )
            continue

        if raw_type in {"rectangle", "ellipse", "diamond"}:
            base = base_element(raw_type, raw["id"], raw["x"], raw["y"])
            base.update(
                {
                    "width": raw["width"],
                    "height": raw["height"],
                    "strokeColor": raw.get("strokeColor", "#1e1e1e"),
                    "backgroundColor": raw.get("backgroundColor", "transparent"),
                    "fillStyle": raw.get("fillStyle", "solid"),
                    "strokeWidth": raw.get("strokeWidth", 2),
                    "strokeStyle": raw.get("strokeStyle", "solid"),
                    "opacity": raw.get("opacity", 100),
                    "roundness": raw.get("roundness"),
                }
            )
            export_elements.append(base)

            label = raw.get("label")
            if label:
                font_size = int(label.get("fontSize", 20))
                text = label["text"]
                width, height = estimate_text_box(text, font_size)
                text_x = raw["x"] + (raw["width"] - width) / 2
                text_y = raw["y"] + (raw["height"] - height) / 2
                export_elements.append(
                    make_text(f"{raw['id']}-text", text_x, text_y, text, font_size)
                )
            continue

        if raw_type == "arrow":
            base = base_element("arrow", raw["id"], raw["x"], raw["y"])
            base.update(
                {
                    "width": raw["width"],
                    "height": raw["height"],
                    "strokeColor": raw.get("strokeColor", "#1e1e1e"),
                    "strokeWidth": raw.get("strokeWidth", 2),
                    "strokeStyle": raw.get("strokeStyle", "solid"),
                    "points": raw["points"],
                    "startArrowhead": raw.get("startArrowhead"),
                    "endArrowhead": raw.get("endArrowhead"),
                    "roundness": raw.get("roundness"),
                }
            )
            export_elements.append(base)

            label = raw.get("label")
            if label:
                font_size = int(label.get("fontSize", 18))
                text = label["text"]
                width, height = estimate_text_box(text, font_size)
                last_point = raw["points"][-1]
                text_x = raw["x"] + (last_point[0] / 2) - (width / 2)
                text_y = raw["y"] + (last_point[1] / 2) - height - 10
                export_elements.append(
                    make_text(
                        f"{raw['id']}-text",
                        text_x,
                        text_y,
                        text,
                        font_size,
                        raw.get("strokeColor", "#1e1e1e"),
                    )
                )
            continue

        raise ValueError(f"Unsupported element type: {raw_type}")

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": export_elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }


def main() -> int:
    if len(sys.argv) != 3:
      print("usage: build_excalidraw_export.py <input.json> <output.json>", file=sys.stderr)
      return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    output_path.write_text(json.dumps(build_export(input_path), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
