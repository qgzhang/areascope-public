import type { Polygon, MultiPolygon } from 'geojson';

export type SelectionTool =
  | 'suburb'
  | 'polygon'
  | 'edit';

export type SelectedArea = {
  source: 'suburb' | 'polygon';

  label: string;

  geometry: Polygon | MultiPolygon;

  localityCode?: string;
};