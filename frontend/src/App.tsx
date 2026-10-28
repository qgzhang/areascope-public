import './App.css';
import MapView from './components/MapView';
import ApiStatus from './components/ApiStatus';
// import ReactPlayground from './components/ReactPlayground';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>AreaScope</h1>
          <p>Area intelligence for field operations</p>
        </div>

        <ApiStatus />

      </header>

      {/* <ReactPlayground /> */}

      <main className="app-main">
        <MapView />
      </main>
    </div>
  );
}

export default App;