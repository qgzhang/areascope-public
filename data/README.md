# DATA

## Property Address locations

https://data.brisbane.qld.gov.au/explore/dataset/property-address-locations/export/
CC BY 4.0
29/09/2026
The original coordinate system as EPSG:28356, the target CRS as EPSG:4326


## Queensland Roads and Tracks

Publisher:
Queensland Government

Purpose:
Foundation road/track centreline data used for
AreaScope road-network analysis.

Licence:
Creative Commons Attribution 4.0

AreaScope import:
Brisbane-region subset.

Stored CRS:
EPSG:4326

Measurement CRS:
EPSG:7856

Transformations:
- source CRS → EPSG:4326
- line features only
- Brisbane bounding-box subset
- spatial index created on geom

Important limitation:
The dataset is not a navigable road-network product.
AreaScope therefore reports road-centreline length,
not route or travel distance.

## ABS Census Mesh Blocks

Publisher:
Australian Bureau of Statistics

Datasets:
- ASGS Edition 3 Mesh Block boundaries, 2021
- Census Mesh Block Counts, 2021

Purpose:
Population and dwelling estimates for AreaScope
selected areas.

Boundary datum:
GDA2020 source data

AreaScope geometry CRS:
EPSG:4326

Imported statistics:
- usual resident population
- dwelling count

Method:
Whole Mesh Blocks use their full published counts.

Partially intersected Mesh Blocks are initially
estimated according to the proportion of Mesh Block
area falling inside the selected AreaScope polygon.

Limitations:
- Census reference year is 2021.
- partial Mesh Blocks require spatial estimation.
- Census cells are subject to ABS confidentiality
  protections.
- dwelling counts are not equivalent to physical
  delivery points.


## Elevation / Terrain

Source:
Geoscience Australia

Product:
SRTM-derived 1 Second Digital Elevation Model

Purpose:
AreaScope elevation and terrain indicators.

Approximate source resolution:
30 metres.

Licence:
Creative Commons Attribution 4.0.

Raw format:
GeoTIFF.

AreaScope processing:
- downloaded Brisbane-area subset
- reprojected to EPSG:7856
- bilinear resampling
- stored as local processed GeoTIFF

Metrics:
- minimum elevation
- maximum elevation
- mean elevation
- elevation range
- mean terrain slope
- 90th percentile slope
- percentage of terrain >= 8 degrees

Important limitations:
- terrain slope is not equivalent to road gradient
- SRTM is not suitable for property-level precision
- terrain classes are AreaScope operational
  heuristics rather than engineering classifications