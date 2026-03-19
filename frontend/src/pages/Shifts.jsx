import { useState } from "react";
import { useExplorer, useExplorerDispatch } from "../context/ExplorerContext";
import useShifts from "../hooks/useShifts";
import ShiftAlerts from "../components/panels/ShiftAlerts";
import { MIN_YEAR, MAX_YEAR } from "../utils/constants";
import { COMMODITY_LIST } from "../utils/commodities";
import { formatNumber } from "../utils/formatters";
import { shiftColor } from "../utils/colorScales";

const yearOptions = Array.from(
  { length: MAX_YEAR - MIN_YEAR + 1 },
  (_, i) => MIN_YEAR + i
);

function SummaryCard({ label, count, color }) {
  return (
    <div
      className="rounded-lg border p-4 bg-gray-800/40"
      style={{ borderColor: `${color}40` }}
    >
      <p className="text-xs text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-bold mt-1" style={{ color }}>
        {formatNumber(count)}
      </p>
    </div>
  );
}

export default function ShiftsPage() {
  const { commodity } = useExplorer();
  const dispatch = useExplorerDispatch();

  const [yearFrom, setYearFrom] = useState(MIN_YEAR);
  const [yearTo, setYearTo] = useState(MAX_YEAR);
  const [selectedCommodity, setSelectedCommodity] = useState(commodity);

  const { shifts, summary, loading, error } = useShifts(
    selectedCommodity,
    yearFrom,
    yearTo
  );

  const handleCommodityChange = (value) => {
    setSelectedCommodity(value);
    dispatch({ type: "SET_COMMODITY", payload: value });
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold">Trade Shift Analysis</h1>
            <p className="text-xs text-gray-500 mt-0.5">
              Detect surges, collapses, and emerging trade flows
            </p>
          </div>
          <a
            href="/"
            className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            Back to Explorer
          </a>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-6">
        <div className="flex flex-wrap items-end gap-4 bg-gray-900/60 rounded-xl border border-gray-800 p-4">
          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">
              Commodity
            </label>
            <select
              value={selectedCommodity}
              onChange={(e) => handleCommodityChange(e.target.value)}
              className="bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500"
            >
              {COMMODITY_LIST.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">
              From Year
            </label>
            <select
              value={yearFrom}
              onChange={(e) => setYearFrom(Number(e.target.value))}
              className="bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500"
            >
              {yearOptions.map((y) => (
                <option key={y} value={y} disabled={y >= yearTo}>
                  {y}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">
              To Year
            </label>
            <select
              value={yearTo}
              onChange={(e) => setYearTo(Number(e.target.value))}
              className="bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500"
            >
              {yearOptions.map((y) => (
                <option key={y} value={y} disabled={y <= yearFrom}>
                  {y}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/30 p-4">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <SummaryCard
              label="Surges"
              count={summary.surges ?? 0}
              color={shiftColor("surge")}
            />
            <SummaryCard
              label="Collapses"
              count={summary.collapses ?? 0}
              color={shiftColor("collapse")}
            />
            <SummaryCard
              label="New Flows"
              count={summary.new_flows ?? 0}
              color={shiftColor("new")}
            />
            <SummaryCard
              label="Abandoned"
              count={summary.abandoned_flows ?? 0}
              color={shiftColor("abandoned")}
            />
          </div>
        )}

        <div className="bg-gray-900/60 rounded-xl border border-gray-800 p-4">
          <h2 className="text-sm font-semibold text-gray-400 mb-4">
            All Detected Shifts
            {summary && (
              <span className="ml-2 text-gray-600 font-normal">
                ({summary.total_shifts ?? shifts.length} total)
              </span>
            )}
          </h2>
          <ShiftAlerts shifts={shifts} loading={loading} />
        </div>
      </main>
    </div>
  );
}
