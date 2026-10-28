
import { useEffect, useRef, useState } from 'react';
import AnalysisPanel from './AnalysisPanel';
import EstimatePanel from './EstimatePanel';
import {
  Map as MapLibreMap,
  NavigationControl,
  setWorkerUrl,
} from 'maplibre-gl';

import type { GeoJSONSource } from 'maplibre-gl';

import {
  TerraDraw,
  TerraDrawPolygonMode,
  TerraDrawSelectMode,
} from 'terra-draw';

import { TerraDrawMapLibreGLAdapter } from
  'terra-draw-maplibre-gl-adapter';

import type { Polygon } from 'geojson';

import {
  getLocalityAt,
} from '../api/api';

import type {
  SelectedArea,
  SelectionTool,
} from '../types/area';

import 'maplibre-gl/dist/maplibre-gl.css';

import workerUrl from
  'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';

setWorkerUrl(workerUrl);


// An empty GeoJSON collection for clearing
// the official locality highlight.
const EMPTY_GEOJSON = {
  type: 'FeatureCollection' as const,
  features: [],
};


function MapView() {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const drawRef = useRef<TerraDraw | null>(null);

  const [ready, setReady] = useState(false);

  const [tool, setTool] =
    useState<SelectionTool>('suburb');

  const [selectedArea, setSelectedArea] =
    useState<SelectedArea | null>(null);

  const [error, setError] = useState<string | null>(null);

  // This ref lets MapLibre event handlers read the
  // latest tool without rebuilding the whole map.
  const toolRef = useRef<SelectionTool>('suburb');

  // Discard an old suburb API response if the user
  // has switched tools or clicked another suburb.
  const requestRef = useRef(0);


  function clearSuburbHighlight() {
    const source = mapRef.current?.getSource(
      'selected-locality',
    ) as GeoJSONSource | undefined;

    source?.setData(EMPTY_GEOJSON);
  }


  function changeTool(nextTool: SelectionTool) {
    const draw = drawRef.current;

    if (!draw) return;

    requestRef.current += 1;

    toolRef.current = nextTool;
    setTool(nextTool);
    setError(null);

    if (nextTool === 'suburb') {
      draw.setMode('static');
      draw.clear();

      clearSuburbHighlight();
      setSelectedArea(null);
    }

    if (nextTool === 'polygon') {
      draw.setMode('static');
      draw.clear();

      clearSuburbHighlight();
      setSelectedArea(null);

      draw.setMode('polygon');
    }

    if (nextTool === 'edit') {
      draw.setMode('select');
    }
  }


  function clearSelection() {
    changeTool('suburb');
  }


  const maptiler_key = import.meta.env.VITE_MAPTILER_KEY;

  useEffect(() => {
    if (!mapContainer.current) return;

    const map = new MapLibreMap({
      container: mapContainer.current,

      // style: 'https://demotiles.maplibre.org/style.json',  // demo tiles
      // style: "https://tiles.openfreemap.org/styles/liberty",  // OpenFreeMap tiles
      style: `https://api.maptiler.com/maps/streets-v4/style.json?key=${maptiler_key}`,  // MapTiler

      center: [153.0251, -27.4698],
      zoom: 10,
    });

    mapRef.current = map;

    map.addControl(
      new NavigationControl(),
      'bottom-left',
    );


    function onMapLoad() {
      // Keep the original locality highlighting
      // layer from Milestone 3B.

      map.addSource('selected-locality', {
        type: 'geojson',
        data: EMPTY_GEOJSON,
      });

      map.addLayer({
        id: 'selected-locality-fill',
        type: 'fill',
        source: 'selected-locality',
        paint: {
          'fill-color': '#2563eb',
          'fill-opacity': 0.2,
        },
      });

      map.addLayer({
        id: 'selected-locality-outline',
        type: 'line',
        source: 'selected-locality',
        paint: {
          'line-color': '#1d4ed8',
          'line-width': 3,
        },
      });


      // Initialise Terra Draw.

      const draw = new TerraDraw({
        adapter: new TerraDrawMapLibreGLAdapter({
          map,
        }),

        modes: [
          new TerraDrawPolygonMode(),

          new TerraDrawSelectMode({
            flags: {
              polygon: {
                feature: {
                  draggable: true,

                  coordinates: {
                    midpoints: true,
                    draggable: true,
                    deletable: true,
                  },
                },
              },
            },
          }),
        ],
      });

      drawRef.current = draw;

      draw.start();
      draw.setMode('static');


      // Handle the completion of drawing or editing.
      draw.on('finish', (id, context) => {
        const feature = draw.getSnapshotFeature(id);

        if (
          !feature ||
          feature.geometry.type !== 'Polygon'
        ) {
          return;
        }

        setSelectedArea({
          source: 'polygon',
          label: 'Custom area',
          geometry: feature.geometry as Polygon,
        });

        // After a new shape is finished,
        // automatically enter Edit mode.
        if (context.action === 'draw') {
          toolRef.current = 'edit';
          setTool('edit');

          draw.setMode('select');
        }
      });


      setReady(true);
    }


    map.on('load', onMapLoad);


    // Suburb lookup applies ONLY in suburb mode.
    async function onMapClick(
      event: { lngLat: { lng: number; lat: number } },
    ) {
      if (toolRef.current !== 'suburb') return;

      const requestId = ++requestRef.current;

      try {
        setError(null);

        const feature = await getLocalityAt(
          event.lngLat.lng,
          event.lngLat.lat,
        );

        // Ignore an outdated lookup response.
        if (
          toolRef.current !== 'suburb' ||
          requestId !== requestRef.current
        ) {
          return;
        }

        const source = map.getSource(
          'selected-locality',
        ) as GeoJSONSource | undefined;

        source?.setData(
          feature ?? EMPTY_GEOJSON,
        );

        if (feature) {
          setSelectedArea({
            source: 'suburb',

            label: feature.properties.locality,

            localityCode:
              feature.properties.loc_code,

            geometry: feature.geometry,
          });
        } else {
          setSelectedArea(null);
        }
      } catch (err) {
        if (requestId !== requestRef.current) return;

        setError('Locality lookup failed.');
        console.error(err);
      }
    }


    map.on('click', onMapClick);


    return () => {
      requestRef.current += 1;

      map.off('load', onMapLoad);
      map.off('click', onMapClick);

      drawRef.current?.stop();
      drawRef.current = null;

      map.remove();
      mapRef.current = null;
    };
  }, []);


  const vertexCount =
    selectedArea?.source === 'polygon' &&
      selectedArea.geometry.type === 'Polygon'
      ? selectedArea.geometry.coordinates[0].length - 1
      : null;


  return (
    <div className="map-wrapper">

      <div className="right-panel-stack">

        <AnalysisPanel
          selectedArea={selectedArea}
        />

        <EstimatePanel
          selectedArea={selectedArea}
        />

      </div>

      <div
        ref={mapContainer}
        className="map-container"
      />

      <div className="area-toolbar">
        <strong>Select area</strong>

        <button
          disabled={!ready}
          className={tool === 'suburb' ? 'active' : ''}
          onClick={() => changeTool('suburb')}
        >
          Select suburb
        </button>

        <button
          disabled={!ready}
          className={tool === 'polygon' ? 'active' : ''}
          onClick={() => changeTool('polygon')}
        >
          Draw polygon
        </button>

        <button
          disabled={
            !ready ||
            selectedArea?.source !== 'polygon'
          }
          className={tool === 'edit' ? 'active' : ''}
          onClick={() => changeTool('edit')}
        >
          Edit polygon
        </button>

        <button
          disabled={!ready}
          onClick={clearSelection}
        >
          Clear
        </button>

        {error && <p className="area-error">{error}</p>}
      </div>


      {selectedArea && (
        <div className="area-info">
          <strong>{selectedArea.label}</strong>

          <div>
            Source: {selectedArea.source}
          </div>

          {vertexCount !== null && (
            <div>Vertices: {vertexCount}</div>
          )}

          <details>
            <summary>View GeoJSON</summary>

            <pre>
              {JSON.stringify(
                selectedArea.geometry,
                null,
                2,
              )}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

export default MapView;