import json
from pathlib import Path
from urllib.parse import quote

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

    if not cat_dir.exists():
        print(f"[WARN] Categoria '{category}' ignorata: cartella non trovata ({cat_dir})")
        return

    has_dirs = False

    for route_dir in cat_dir.iterdir():
        if not route_dir.is_dir():
            continue

        has_dirs = True

        folder_name = route_dir.name

        # File principali
        geojson_path = route_dir / f"{folder_name}.geojson"
        html_path = route_dir / f"{folder_name}_info.html"
        elev_path = route_dir / f"{folder_name}_elevation.png"

        # Se manca il geojson → ignora il percorso
        if not geojson_path.exists():
            print(f"[WARN] Nessun GeoJSON trovato in {route_dir}")
            continue

        # Carica il GeoJSON del percorso
        with geojson_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Estrarre solo la geometria
        if data.get("type") == "FeatureCollection":
            geometry = data["features"][0]["geometry"]
        else:
            geometry = data["geometry"]

        # URL RAW con encoding
        rel = quote(str(route_dir).replace("\\", "/"))
        html_url = f"{GITHUB_RAW_BASE}/{rel}/{quote(folder_name)}_info.html"
        elev_url = f"{GITHUB_RAW_BASE}/{rel}/{quote(folder_name)}_elevation.png"

        # Popup HTML
        popup_html = (
            f"<h3>{folder_name}</h3>"
            f"<img src='{elev_url}' style='width:100%;margin-bottom:10px;' />"
            f"<iframe src='{html_url}' "
            f"style='width:100%;height:400px;border:none;'></iframe>"
        )

        # Costruzione della feature
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "name": folder_name,
                "description": popup_html,
                "category": category
            }
        }

        features.append(feature)

    if not has_dirs:
        print(f"[INFO] Categoria '{category}' vuota: nessun file generato.")
        return

    # FeatureCollection finale
    collection = {
        "type": "FeatureCollection",
        "features": features,
    }

    OUTPUT.mkdir(exist_ok=True)
    out_path = OUTPUT / out_file

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False)

    print(f"[OK] Generato: {out_path}")


def main():
    for cat, filename in CATEGORIES.items():
        build_category(cat, filename)


if __name__ == "__main__":
    main()
