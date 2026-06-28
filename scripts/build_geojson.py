import json
import os
from pathlib import Path

BASE = Path("data")
OUTPUT = Path("docs")

CATEGORIES = {
    "route-trips": "route-trips.geojson",
    "raduni": "raduni.geojson",
    "best-roads": "best-roads.geojson",
}

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/albeb985-Dev/mx5drivingroads/main"

def build_category(category: str, out_file: str):
    features = []
    cat_dir = BASE / category

    for route_dir in cat_dir.iterdir():
        if not route_dir.is_dir():
            continue

        geojson_path = route_dir / "track.geojson"
        if not geojson_path.exists():
            continue

        with geojson_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # assumiamo che track.geojson contenga una Feature o FeatureCollection
        if data.get("type") == "FeatureCollection":
            route_features = data["features"]
        else:
            route_features = [data]

        # meta opzionale
        meta_path = route_dir / "meta.json"
        meta = {}
        if meta_path.exists():
            with meta_path.open("r", encoding="utf-8") as f:
                meta = json.load(f)

        # URL dei file nel repo
        rel = route_dir.relative_to(Path("."))
        html_url = f"{GITHUB_RAW_BASE}/{rel}/info.html"
        elev_url = f"{GITHUB_RAW_BASE}/{rel}/elevation.png"

        for feat in route_features:
            props = feat.setdefault("properties", {})
            props.setdefault("name", meta.get("title", route_dir.name))

            # popup HTML: iframe + immagine altimetrica
            props["description"] = (
                f"<h3>{props['name']}</h3>"
                f"<img src='{elev_url}' style='width:100%;' />"
                f"<iframe src='{html_url}' "
                f"style='width:100%;height:400px;border:none;'></iframe>"
            )

            # categoria utile per filtri futuri
            props["category"] = category

            features.append(feat)

    collection = {
        "type": "FeatureCollection",
        "features": features,
    }

    OUTPUT.mkdir(exist_ok=True)
    out_path = OUTPUT / out_file
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False)

def main():
    for cat, filename in CATEGORIES.items():
        build_category(cat, filename)

if __name__ == "__main__":
    main()
