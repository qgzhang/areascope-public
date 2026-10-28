const API_URL =
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

import type {
  Feature,
  MultiPolygon,
  Polygon,
} from 'geojson';

export type LocalityProperties = {
  loc_code: string;
  locality: string;
  lga: string;
  area_sqkm: number | null;
};

export type LocalityFeature = Feature<
  Polygon | MultiPolygon,
  LocalityProperties
>;

export async function getLocalityAt(
  lng: number,
  lat: number,
): Promise<LocalityFeature | null> {

  const params = new URLSearchParams({
    lng: String(lng),
    lat: String(lat),
  });

  const response = await fetch(
    `${API_URL}/api/localities/at?${params}`,
  );

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(
      `HTTP error: ${response.status}`,
    );
  }

  return response.json();
}


export type HealthResponse = {
  status: string;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json();
}


export type AreaAnalysis = {
  area_km2: number;

  total_address_records: number;

  official_address_records: number;

  other_address_records: number;

  official_density_per_km2: number;

  road_centreline_km: number;

  road_density_km_per_km2: number;

  official_addresses_per_road_km:  number | null;

  estimated_population_2021: number;

  estimated_dwellings_2021: number;

  population_density_per_km2: number;

  mesh_blocks_intersected: number;

  partial_mesh_blocks: number;

  census_year: number;

  demographic_estimation_method: string;

  data_coverage_note: string;

  terrain_available: boolean;

  elevation_min_m: number | null;

  elevation_max_m: number | null;

  elevation_mean_m: number | null;

  elevation_range_m: number | null;

  mean_slope_deg: number | null;

  p90_slope_deg: number | null;

  steep_area_percent: number | null;

  terrain_class: string | null;

  terrain_source?: string;

};

export async function analyseArea(
  geometry: Polygon | MultiPolygon,
  signal?: AbortSignal,
): Promise<AreaAnalysis> {

  const response = await fetch(
    `${API_URL}/api/analysis`,
    {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify({
        geometry,
      }),

      signal,
    },
  );

  if (!response.ok) {
    throw new Error(
      `Analysis failed: HTTP ${response.status}`,
    );
  }

  return response.json();
}

export type EstimateAssumptions = {
  eligible_address_ratio: number;

  seconds_per_delivery: number;

  service_distance_factor: number;

  walking_speed_kmh: number;

  exception_rate: number;

  seconds_per_exception: number;

  fixed_setup_minutes: number;

  labour_rate_per_hour: number;

  other_costs: number;

  target_margin: number;
};

export type WorkEstimate = {
  eligible_delivery_points: number;

  estimated_service_distance_km: number;

  terrain_multiplier: number;

  handling_hours: number;

  movement_hours: number;

  exception_hours: number;

  setup_hours: number;

  estimated_hours: number;

  estimated_exceptions: number;

  labour_cost: number;

  other_costs: number;

  estimated_cost: number;

  suggested_quote: number;

  cost_per_point: number | null;

  quote_per_point: number | null;

  estimated_points_per_hour: number | null;

  model_status: string;

  model_note: string;
  model_version: string;

};

export type EstimateResponse = {
  analysis: AreaAnalysis;

  assumptions: EstimateAssumptions;

  estimate: WorkEstimate;
};

export async function estimateArea(
  geometry: Polygon | MultiPolygon,
  assumptions: EstimateAssumptions,
  signal?: AbortSignal,
): Promise<EstimateResponse> {

  const response = await fetch(
    `${API_URL}/api/estimate`,
    {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify({
        geometry,
        assumptions,
      }),

      signal,
    },
  );

  if (!response.ok) {
    throw new Error(
      `Estimate failed: HTTP ${response.status}`,
    );
  }

  return response.json();
}