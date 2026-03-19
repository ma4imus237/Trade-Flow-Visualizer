import { Routes, Route } from "react-router-dom";
import { ExplorerProvider } from "./context/ExplorerContext";
import Explorer from "./pages/Explorer";

function App() {
  return (
    <ExplorerProvider>
      <Routes>
        <Route path="/" element={<Explorer />} />
        <Route
          path="/country/:iso3"
          element={
            <div className="flex h-screen items-center justify-center bg-gray-950 text-white">
              Country Detail - Coming Soon
            </div>
          }
        />
        <Route
          path="/shifts"
          element={
            <div className="flex h-screen items-center justify-center bg-gray-950 text-white">
              Shifts - Coming Soon
            </div>
          }
        />
      </Routes>
    </ExplorerProvider>
  );
}

export default App;
