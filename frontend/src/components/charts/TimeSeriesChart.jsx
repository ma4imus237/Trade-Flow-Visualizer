import { useMemo, useCallback } from "react";
import Plot from "react-plotly.js";
import { useExplorerDispatch } from "../../context/ExplorerContext";
import useTimeseries from "../../hooks/useTimeseries";
import { getCommodityColor } from "../../utils/commodities";

export default function TimeSeriesChart({ reporter, partner, commodity, title }) {
  const dispatch = useExplorerDispatch();
  const { data, loading, error } = useTimeseries(reporter, partner, commodity);

  const color = getCommodityColor(commodity);

  const plotData = useMemo(() => {
    if (!data || data.length === 0) return null;

    return [
      {
        x: data.map((d) => d.year),
        y: data.map((d) => d.value_usd),
        type: "scatter",
        mode: "lines+markers",
        line: { color, width: 2, shape: "spline" },
        marker: { color, size: 6 },
        hovertemplate: "Year: %{x}<br>Value: $%{y:,.0f}<extra></extra>",
      },
    ];
  }, [data, color]);

  const layout = useMemo(
    () => ({
      font: { size: 11, color: "#d1d5db", family: "Inter, system-ui, sans-serif" },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 60, r: 20, t: title ? 30 : 10, b: 40 },
      autosize: true,
      title: title
        ? { text: title, font: { size: 13, color: "#e5e7eb" }, x: 0.01 }
        : undefined,
      xaxis: {
        gridcolor: "rgba(255,255,255,0.06)",
        tickfont: { color: "#9ca3af" },
        dtick: 1,
      },
      yaxis: {
        gridcolor: "rgba(255,255,255,0.06)",
        tickfont: { color: "#9ca3af" },
        tickprefix: "$",
      },
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
      if (point && point.x) {
        dispatch({ type: "SET_YEAR", payload: point.x });
      }
    },
    [dispatch]
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[200px]">
        <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full min-h-[200px]">
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }

  if (!plotData) {
    return (
      <div className="flex items-center justify-center h-full min-h-[200px]">
        <p className="text-sm text-gray-500">No timeseries data available.</p>
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
