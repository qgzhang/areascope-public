import { useState } from 'react';
import AreaSummary from './AreaSummary';
// import MapView from './MapView';

function ReactPlayground() {
  const [count, setCount] = useState(0);
  const [mode, setMode] =
    useState<'suburb' | 'polygon'>('suburb');

  return (
    <div>
      <AreaSummary
  name="Kenmore"
  addressCount={4200}
/>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increase
      </button>

      <h2>Selection mode</h2>

      <button onClick={() => setMode('suburb')}>
        Suburb
      </button>

      <button onClick={() => setMode('polygon')}>
        Polygon
      </button>

      <p>Current mode: {mode}</p>

      {mode === 'suburb' && (
        <p>Click a suburb on the map.</p>
      )}

      {mode === 'polygon' && (
        <p>Draw a polygon on the map.</p>
      )}
    </div>
    
  );
}

export default ReactPlayground;