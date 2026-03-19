import { useState, useEffect } from "react";
import { useExplorer } from "../../context/ExplorerContext";
import SankeyDiagram from "../charts/SankeyDiagram";
import FlowTable from "./FlowTable";
import ShiftAlerts from "./ShiftAlerts";
import CountryProfile from "./CountryProfile";
import useSankey from "../../hooks/useSankey";
import useShifts from "../../hooks/useShifts";
import { MIN_YEAR } from "../../utils/constants";

const TABS = [
  { id: "sankey", label: "Sankey" },
  { id: "table", label: "Table" },
  { id: "shifts", label: "Shifts" },
];

export default function ExplorerSidebar() {
  const { commodity, year, flowType, selectedCountry } = useExplorer();
  const [activeTab, setActiveTab] = useState("sankey");

  const { data: sankeyData } = useSankey(commodity, year, flowType);
  const { shifts, loading: shiftsLoading } = useShifts(
    commodity,
    MIN_YEAR,
    year
  );

  const flows = sankeyData?.links
    ? sankeyData.links.map((link) => {
        const reporter = sankeyData.nodes[link.source];
        const partner = sankeyData.nodes[link.target];
        return {
          reporter_iso3: reporter?.id || "",
          reporter_name: reporter?.name || "",
          partner_iso3: partner?.id || "",
          partner_name: partner?.name || "",
          value_usd: link.value,
          weight_kg: null,
          change_pct: null,
        };
      })
    : [];

  return (
    <div className="relative flex flex-col h-full bg-gray-900/80 backdrop-blur-sm">
      <div className="flex border-b border-gray-700/50 shrink-0">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 px-3 py-2.5 text-xs font-semibold uppercase tracking-wider transition-colors ${
              activeTab === tab.id
                ? "text-cyan-400 border-b-2 border-cyan-400 bg-gray-800/40"
                : "text-gray-500 hover:text-gray-300 border-b-2 border-transparent"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-hidden">
        {activeTab === "sankey" && (
          <div className="h-full p-2">
            <SankeyDiagram />
          </div>
        )}
        {activeTab === "table" && (
          <div className="h-full">
            <FlowTable flows={flows} />
          </div>
        )}
        {activeTab === "shifts" && (
          <div className="h-full overflow-y-auto p-2">
            <ShiftAlerts shifts={shifts} loading={shiftsLoading} />
          </div>
        )}
      </div>

      {selectedCountry && <CountryProfile />}
    </div>
  );
}
