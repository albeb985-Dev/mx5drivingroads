import json
from pathlib import Path
from string import Template

BASE = Path("data")
OUTPUT = Path("docs")
TEMPLATE_PATH = Path("templates/popup_template.html")

CATEGORIES = {
    "route-trips": "route-trips.geojson",
    "raduni": "raduni.geojson",
    "best-roads": "best-roads.geojson",
}

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/albeb985-Dev/mx5drivingroads/main"


def render_popup_html(context):
    """Renderizza il template HTML con i dati del percorso."""
    with TEMPLATE_PATH.open("r", encoding="utf-8") as f:
        tpl = Template(f.read())
    return tpl.safe_substitute(context)


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
        gpx_path = route_dir / f"{folder_name}.gpx"

        if not geojson_path.exists():
            print(f"[WARN] Nessun GeoJSON trovato in {route_dir}")
            continue

        # Carica il GeoJSON
        with geojson_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Estrarre solo la geometria
        if data.get("type") == "FeatureCollection":
            geometry = data["features"][0]["geometry"]
        else:
            geometry = data["geometry"]

        # URL RAW dei file nel branch main
        rel = route_dir.relative_to(Path("."))

        elevation_url = f"{GITHUB_RAW_BASE}/{rel}/{folder_name}_elevation.png"
        gpx_url = f"{GITHUB_RAW_BASE}/{rel}/{folder_name}.gpx"

        # Carica descrizione dal file HTML (se esiste)
        if html_path.exists():
            description = html_path.read_text(encoding="utf-8")
        else:
            description = "Nessuna descrizione disponibile."

        # Render template
        popup_html = render_popup_html({
            "title": folder_name.replace("-", " ").title(),
            "category": category,
            "elevation_image": elevation_url,
            "description": description,
            "gpx_url": gpx_url
        })

        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "name": folder_name.replace("-", " ").title(),
                "description": popup_html,
                "category": category
            }
        }

        features.append(feature)

    if not has_dirs:
        print(f"[INFO] Categoria '{category}' vuota: nessun file generato.")
        return

    collection = {
        "type": "FeatureCollection",
        "features": features,
    }

    OUTPUT.mkdir(exist_ok=True)
    out_path = OUTPUT / out_file

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)

    print(f"[OK] Generato: {out_path}")


def main():
    for cat, filename in CATEGORIES.items():
        build_category(cat, filename)


if __name__ == "__main__":
    main()
