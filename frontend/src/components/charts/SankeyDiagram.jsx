import { useMemo, useCallback } from "react";
import Plot from "react-plotly.js";
import { useExplorer, useExplorerDispatch } from "../../context/ExplorerContext";
import useSankey from "../../hooks/useSankey";
import { getCommodityColor } from "../../utils/commodities";
import {
  SANKEY_LINK_OPACITY,
  SANKEY_NODE_PAD,
  SANKEY_NODE_THICKNESS,
} from "../../utils/constants";

function LoadingSkeleton() {
  return (
    <div className="flex items-center justify-center h-full min-h-[300px]">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-gray-400">Loading Sankey diagram...</span>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex items-center justify-center h-full min-h-[300px]">
      <p className="text-sm text-gray-500">
        No trade flow data available for the current selection.
      </p>
    </div>
  );
}

export default function SankeyDiagram() {
  const { commodity, year, flowType } = useExplorer();
  const dispatch = useExplorerDispatch();
  const { data, loading, error } = useSankey(commodity, year, flowType);

  const commodityColor = getCommodityColor(commodity);

  const plotData = useMemo(() => {
    if (!data || !data.nodes || !data.links) return null;
    if (data.nodes.length === 0 || data.links.length === 0) return null;

    const nodeColors = data.nodes.map(() => commodityColor);
    const linkColors = data.links.map(
      () => `rgba(${hexToRgbStr(commodityColor)}, ${SANKEY_LINK_OPACITY})`
    );

    return [
      {
        type: "sankey",
        orientation: "h",
        node: {
          pad: SANKEY_NODE_PAD,
          thickness: SANKEY_NODE_THICKNESS,
          line: { color: "rgba(255,255,255,0.2)", width: 0.5 },
          label: data.nodes.map((n) => n.name),
          color: nodeColors,
          hovertemplate: "%{label}<extra></extra>",
        },
        link: {
          source: data.links.map((l) => l.source),
          target: data.links.map((l) => l.target),
          value: data.links.map((l) => l.value),
          color: linkColors,
          hovertemplate:
            "%{source.label} → %{target.label}<br>$%{value:,.0f}<extra></extra>",
        },
      },
    ];
  }, [data, commodityColor]);

  const layout = useMemo(
    () => ({
      font: { size: 11, color: "#d1d5db", family: "Inter, system-ui, sans-serif" },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 10, r: 10, t: 10, b: 10 },
      autosize: true,
    }),
    []
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
      if (!data || !data.nodes) return;
      const point = event.points?.[0];
      if (!point) return;

      if (point.pointNumber !== undefined && point.hasOwnProperty("sourceLinks")) {
        const node = data.nodes[point.pointNumber];
        if (node && node.id) {
          dispatch({ type: "SELECT_COUNTRY", payload: node.id });
        }
      }
    },
    [data, dispatch]
  );

  if (loading) return <LoadingSkeleton />;
  if (error) {
    return (
      <div className="flex items-center justify-center h-full min-h-[300px]">
        <p className="text-sm text-red-400">Error: {error}</p>
      </div>
    );
  }
  if (!plotData) return <EmptyState />;

  return (
    <div className="w-full h-full min-h-[300px]">
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

function hexToRgbStr(hex) {
  const h = hex.replace("#", "");
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  return `${r}, ${g}, ${b}`;
}
