import { useEffect, useRef, useState  } from 'react';

import {
  GeoJSONSource,
  Map,
  NavigationControl,
  setWorkerUrl,
} from 'maplibre-gl';

import {
  getLocalityAt,
  type LocalityFeature,
} from '../api/api';

import 'maplibre-gl/dist/maplibre-gl.css';

import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';

setWorkerUrl(workerUrl);

function MapView() {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const map = useRef<Map | null>(null);
  const [ selectedLocality,  setSelectedLocality ] = useState<LocalityFeature | null>(null);

  useEffect(() => {
    if (!mapContainer.current) {
      return;
    }

    if (map.current) {
      return;
    }

    map.current = new Map({
      container: mapContainer.current,

      style: 'https://demotiles.maplibre.org/style.json',

      center: [153.0251, -27.4698],

      zoom: 10,
    });

    map.current.addControl(
      new NavigationControl(),
      'top-right',
    );

    //After constructing the map, when it loads:
    map.current.on('load', () => {

      map.current?.addSource(
        'selected-locality',
        {
          type: 'geojson',

          data: {
            type: 'FeatureCollection',
            features: [],
          },
        },
      );


      map.current?.addLayer({
        id: 'selected-locality-fill',

        type: 'fill',

        source: 'selected-locality',

        paint: {
          'fill-color': '#2563eb',
          'fill-opacity': 0.2,
        },
      });


      map.current?.addLayer({
        id: 'selected-locality-outline',

        type: 'line',

        source: 'selected-locality',

        paint: {
          'line-color': '#1d4ed8',
          'line-width': 3,
        },
      });
    });

    // a click handler:
    map.current.on(
      'click',
      async (event) => {

        try {
          const feature =
            await getLocalityAt(
              event.lngLat.lng,
              event.lngLat.lat,
            );


          setSelectedLocality(feature);


          const source =
            map.current?.getSource(
              'selected-locality',
            ) as GeoJSONSource | undefined;


          if (!source) {
            return;
          }


          if (feature) {
            source.setData(feature);
          } else {
            source.setData({
              type: 'FeatureCollection',
              features: [],
            });
          }

        } catch (error) {

          console.error(
            'Failed to find locality:',
            error,
          );
        }
      },
    );    




    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  return (
    <div className="map-wrapper">

      <div
        ref={mapContainer}
        className="map-container"
      />

      {selectedLocality && (
        <div className="locality-info">

          <strong>
            {selectedLocality.properties.locality}
          </strong>

          <div>
            {selectedLocality.properties.lga}
          </div>

        </div>
      )}

    </div>
  );
}

export default MapView;