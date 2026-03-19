import { Routes, Route } from "react-router-dom";
import { ExplorerProvider } from "./context/ExplorerContext";
import Explorer from "./pages/Explorer";
import CountryDetail from "./pages/CountryDetail";
import ShiftsPage from "./pages/Shifts";

function App() {
  return (
    <ExplorerProvider>
      <Routes>
        <Route path="/" element={<Explorer />} />
        <Route path="/country/:iso3" element={<CountryDetail />} />
        <Route path="/shifts" element={<ShiftsPage />} />
      </Routes>
    </ExplorerProvider>
  );
}

export default App;
