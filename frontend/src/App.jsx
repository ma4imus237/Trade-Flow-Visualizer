import { Routes, Route } from "react-router-dom";
import { ExplorerProvider } from "./context/ExplorerContext";

function App() {
  return (
    <ExplorerProvider>
      <Routes>
        <Route path="/" element={<div>Trade Flow Visualizer - Loading...</div>} />
      </Routes>
    </ExplorerProvider>
  );
}

export default App;
