import { useMemo, useCallback } from "react";
import Plot from "react-plotly.js";
import { useExplorerDispatch } from "../../context/ExplorerContext";
import { getCommodityColor } from "../../utils/commodities";

/**
 * Horizontal bar chart showing top trade partners.
 * @param {{ partners: Array<{iso3: string, name: string, value_usd: number}>, commodity: string, title?: string }} props
 */
export default function FlowBarChart({ partners, commodity, title }) {
  const dispatch = useExplorerDispatch();
  const color = getCommodityColor(commodity);

  const plotData = useMemo(() => {
    if (!partners || partners.length === 0) return null;

    const sorted = [...partners].sort((a, b) => a.value_usd - b.value_usd);

    return [
      {
        y: sorted.map((p) => p.name),
        x: sorted.map((p) => p.value_usd),
        type: "bar",
        orientation: "h",
        marker: { color, opacity: 0.85 },
        hovertemplate: "%{y}<br>$%{x:,.0f}<extra></extra>",
        customdata: sorted.map((p) => p.iso3),
      },
    ];
  }, [partners, color]);

  const layout = useMemo(
    () => ({
      font: { size: 11, color: "#d1d5db", family: "Inter, system-ui, sans-serif" },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 80, r: 20, t: title ? 30 : 10, b: 40 },
      autosize: true,
      title: title
        ? { text: title, font: { size: 13, color: "#e5e7eb" }, x: 0.01 }
        : undefined,
      xaxis: {
        gridcolor: "rgba(255,255,255,0.06)",
        tickfont: { color: "#9ca3af" },
        tickprefix: "$",
      },
      yaxis: {
        tickfont: { color: "#9ca3af" },
        automargin: true,
      },
      bargap: 0.15,
    }),
    [title]
  );

  const config = useMemo(
    () => ({
      displayModeBar: false,
      responsive: true,
    }),
    []
  );

  const handleClick = useCallback(
    (event) => {
      const point = event.points?.[0];
      if (point && point.customdata) {
        dispatch({ type: "SELECT_COUNTRY", payload: point.customdata });
      }
    },
    [dispatch]
  );

  if (!plotData) {
    return (
      <div className="flex items-center justify-center h-full min-h-[200px]">
        <p className="text-sm text-gray-500">No partner data available.</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full min-h-[200px]">
      <Plot
        data={plotData}
        layout={layout}
        config={config}
        useResizeHandler
        className="w-full h-full"
        style={{ width: "100%", height: "100%" }}
        onClick={handleClick}
      />
    </div>
  );
}
