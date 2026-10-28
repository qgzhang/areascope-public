import { useEffect, useState } from 'react';

import {
  analyseArea,
  type AreaAnalysis,
} from '../api/api';

import type {
  SelectedArea,
} from '../types/area';


type AnalysisPanelProps = {
  selectedArea: SelectedArea | null;
};


export default function AnalysisPanel({
  selectedArea,
}: AnalysisPanelProps) {

  const [result, setResult] =
    useState<AreaAnalysis | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {

    if (!selectedArea) {
      setResult(null);
      setError(null);
      setLoading(false);
      return;
    }

    const controller = new AbortController();

    async function runAnalysis() {

      setLoading(true);
      setResult(null);
      setError(null);

      try {
        const data = await analyseArea(
          selectedArea!.geometry,
          controller.signal,
        );

        if (!controller.signal.aborted) {
          setResult(data);
        }

      } catch (err) {

        if (!controller.signal.aborted) {
          setError("Area analysis failed");
          console.error(err);
        }

      } finally {

        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    runAnalysis();

    return () => {
      controller.abort();
    };

  }, [selectedArea]);


  if (!selectedArea) {
    return (
      <aside className="analysis-panel">

        <h3>Area analysis</h3>

        <p>
          Select a suburb or draw an area
          to view the analysis.
        </p>

      </aside>
    );
  }

  return (
    <aside className="analysis-panel">

      <h3>Area analysis</h3>

      <p>{selectedArea.label}</p>

      {loading && <p>Calculating...</p>}

      {error && <p className="area-error">{error}</p>}

      {result && (
        <div className="analysis-results">

            <div>
            <strong>Selected area</strong>
            <p>{result.area_km2.toFixed(3)} km²</p>
            </div>

            <div>
            <strong>Official address records</strong>
            <p>
                {result.official_address_records
                .toLocaleString()}
            </p>
            </div>

            <div>
            <strong>Other address records</strong>
            <p>
                {result.other_address_records
                .toLocaleString()}
            </p>
            </div>

            <div>
            <strong>Official records / km²</strong>
            <p>
                {result.official_density_per_km2
                .toLocaleString()}
            </p>
            </div>

            <div>
              <strong>Road centreline</strong>

              <p>
                {result.road_centreline_km
                  .toFixed(2)} km
              </p>
            </div>


            <div>
              <strong>Road density</strong>

              <p>
                {result.road_density_km_per_km2
                  .toFixed(2)} km/km²
              </p>
            </div>


            <div>
              <strong>
                Official addresses / road km
              </strong>

              <p>
                {result.official_addresses_per_road_km
                  !== null
                  ? result
                      .official_addresses_per_road_km
                      .toFixed(1)
                  : 'N/A'}
              </p>
            </div>

            <div>
              <strong>
                Estimated population
              </strong>

              <p>
                {result.estimated_population_2021
                  .toLocaleString()}
              </p>
            </div>


            <div>
              <strong>
                Estimated dwellings
              </strong>

              <p>
                {result.estimated_dwellings_2021
                  .toLocaleString()}
              </p>
            </div>


            <div>
              <strong>
                Population density
              </strong>

              <p>
                {result.population_density_per_km2
                  .toLocaleString()} persons/km²
              </p>
            </div>

            <details>
              <summary>
                Demographic methodology
              </summary>

              <p>
                Census year:
                {' '}
                {result.census_year}
              </p>

              <p>
                Mesh Blocks:
                {' '}
                {result.mesh_blocks_intersected}
              </p>

              <p>
                Partial Mesh Blocks:
                {' '}
                {result.partial_mesh_blocks}
              </p>

              <p>
                {result.demographic_estimation_method}
              </p>
            </details>


            <small>
            {result.data_coverage_note}
            </small>

            <h4>Terrain</h4>

            {result.terrain_available ? (
              <>
                <div>
                  <strong>Elevation</strong>

                  <p>
                    {result.elevation_min_m?.toFixed(0)}
                    {' – '}
                    {result.elevation_max_m?.toFixed(0)}
                    {' m'}
                  </p>
                </div>

                <div>
                  <strong>Elevation range</strong>

                  <p>
                    {result.elevation_range_m?.toFixed(0)}
                    {' m'}
                  </p>
                </div>

                <div>
                  <strong>Mean slope</strong>

                  <p>
                    {result.mean_slope_deg?.toFixed(1)}
                    {'°'}
                  </p>
                </div>

                <div>
                  <strong>90th percentile slope</strong>

                  <p>
                    {result.p90_slope_deg?.toFixed(1)}
                    {'°'}
                  </p>
                </div>

                <div>
                  <strong>Steep area</strong>

                  <p>
                    {result.steep_area_percent?.toFixed(1)}
                    {'%'}
                  </p>
                </div>

                <div>
                  <strong>Terrain</strong>

                  <p>
                    {result.terrain_class}
                  </p>
                </div>
              </>
            ) : (
              <p>
                Terrain data is not available for this area.
              </p>
            )}

          </div>
        )}

    </aside>
  );
}