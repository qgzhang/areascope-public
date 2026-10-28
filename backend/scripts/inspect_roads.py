from pathlib import Path

import pyogrio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "roads"
    / "queensland_roads_tracks.gpkg"
)


print(f"File: {DATA_PATH}")

layers = pyogrio.list_layers(DATA_PATH)

print("\nLayers:")
for layer in layers:
    print(layer)


for layer_name, geometry_type in layers:

    print("\n" + "=" * 60)
    print(f"Layer: {layer_name}")
    print(f"Geometry: {geometry_type}")

    info = pyogrio.read_info(
        DATA_PATH,
        layer=layer_name,
    )

    print(f"Feature count: {info['features']}")
    print(f"CRS: {info['crs']}")

    print("\nFields:")
    for field in info["fields"]:
        print(f"  {field}")