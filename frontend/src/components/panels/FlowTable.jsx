import { useState, useMemo } from "react";
import { useExplorer, useExplorerDispatch } from "../../context/ExplorerContext";
import { formatUSD, formatWeight, formatChangePct } from "../../utils/formatters";

const COLUMNS = [
  { key: "reporter_name", label: "Reporter", sortable: true },
  { key: "partner_name", label: "Partner", sortable: true },
  { key: "value_usd", label: "Value (USD)", sortable: true, align: "right" },
  { key: "weight_kg", label: "Weight", sortable: true, align: "right" },
  { key: "change_pct", label: "Change %", sortable: true, align: "right" },
];

function SortIcon({ direction }) {
  if (!direction) {
    return (
      <svg className="w-3 h-3 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
        <path d="M5 8l5-4 5 4H5zm0 4l5 4 5-4H5z" />
      </svg>
    );
  }
  return (
    <svg className="w-3 h-3 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
      {direction === "asc" ? (
        <path d="M5 12l5-8 5 8H5z" />
      ) : (
        <path d="M5 8l5 8 5-8H5z" />
      )}
    </svg>
  );
}

export default function FlowTable({ flows = [] }) {
  const { highlightedArc } = useExplorer();
  const dispatch = useExplorerDispatch();
  const [sortKey, setSortKey] = useState("value_usd");
  const [sortDir, setSortDir] = useState("desc");

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  const sortedFlows = useMemo(() => {
    if (!flows || flows.length === 0) return [];
    return [...flows].sort((a, b) => {
      const aVal = a[sortKey] ?? 0;
      const bVal = b[sortKey] ?? 0;
      if (typeof aVal === "string") {
        return sortDir === "asc"
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      return sortDir === "asc" ? aVal - bVal : bVal - aVal;
    });
  }, [flows, sortKey, sortDir]);

  const handleRowClick = (flow) => {
    dispatch({
      type: "HIGHLIGHT_ARC",
      payload: {
        reporter: flow.reporter_iso3,
        partner: flow.partner_iso3,
      },
    });
  };

  const isHighlighted = (flow) => {
    if (!highlightedArc) return false;
    return (
      highlightedArc.reporter === flow.reporter_iso3 &&
      highlightedArc.partner === flow.partner_iso3
    );
  };

  if (!flows || flows.length === 0) {
    return (
      <div className="flex items-center justify-center h-full min-h-[200px]">
        <p className="text-sm text-gray-500">No flow data to display.</p>
      </div>
    );
  }

  return (
    <div className="overflow-auto h-full">
      <table className="w-full text-sm">
        <thead className="sticky top-0 bg-gray-900/95 backdrop-blur-sm z-10">
          <tr>
            {COLUMNS.map((col) => (
              <th
                key={col.key}
                className={`px-3 py-2 text-xs font-semibold uppercase tracking-wider text-gray-500 border-b border-gray-700/50 cursor-pointer hover:text-gray-300 select-none ${
                  col.align === "right" ? "text-right" : "text-left"
                }`}
                onClick={() => col.sortable && handleSort(col.key)}
              >
                <span className="inline-flex items-center gap-1">
                  {col.label}
                  {col.sortable && (
                    <SortIcon
                      direction={sortKey === col.key ? sortDir : null}
                    />
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedFlows.map((flow, idx) => {
            const highlighted = isHighlighted(flow);
            return (
              <tr
                key={`${flow.reporter_iso3}-${flow.partner_iso3}-${idx}`}
                className={`cursor-pointer transition-colors ${
                  highlighted
                    ? "bg-cyan-500/15 border-l-2 border-l-cyan-400"
                    : "hover:bg-gray-800/50 border-l-2 border-l-transparent"
                }`}
                onClick={() => handleRowClick(flow)}
              >
                <td className="px-3 py-2 text-gray-300 whitespace-nowrap">
                  {flow.reporter_name || flow.reporter_iso3}
                </td>
                <td className="px-3 py-2 text-gray-300 whitespace-nowrap">
                  {flow.partner_name || flow.partner_iso3}
                </td>
                <td className="px-3 py-2 text-gray-300 text-right whitespace-nowrap">
                  {formatUSD(flow.value_usd)}
                </td>
                <td className="px-3 py-2 text-gray-400 text-right whitespace-nowrap">
                  {flow.weight_kg != null ? formatWeight(flow.weight_kg) : "--"}
                </td>
                <td className="px-3 py-2 text-right whitespace-nowrap">
                  {flow.change_pct != null ? (
                    <span
                      className={
                        flow.change_pct >= 0 ? "text-green-400" : "text-red-400"
                      }
                    >
                      {formatChangePct(flow.change_pct)}
                    </span>
                  ) : (
                    <span className="text-gray-600">--</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
