import { getCommodityColor, COMMODITY_LIST } from "../../utils/commodities";
import { formatUSD } from "../../utils/format";

/**
 * Map legend showing commodity color and width scale.
 * Positioned bottom-right of the map container.
 */
export default function MapLegend({ commodity }) {
  const color = getCommodityColor(commodity);
  const item = COMMODITY_LIST.find((c) => c.code === commodity);
  const label = item ? item.name : commodity;

  const widthSteps = [
    { value: 1e6, label: "$1M" },
    { value: 1e8, label: "$100M" },
    { value: 1e10, label: "$10B" },
  ];

  return (
    <div className="absolute bottom-4 right-4 z-40 rounded-lg bg-gray-900/90 px-4 py-3 text-xs text-gray-200 shadow-lg backdrop-blur-sm">
      <div className="mb-2 flex items-center gap-2">
        <span
          className="inline-block h-3 w-3 rounded-full"
          style={{ backgroundColor: color }}
        />
        <span className="font-medium">{label}</span>
      </div>

      <div className="space-y-1">
        <p className="text-[10px] uppercase tracking-wider text-gray-400">
          Arc width
        </p>
        {widthSteps.map((step) => {
          const width = Math.max(1, Math.log(step.value / 1e6) * 2);
          return (
            <div key={step.label} className="flex items-center gap-2">
              <div
                className="rounded-sm"
                style={{
                  width: 24,
                  height: Math.max(2, width),
                  backgroundColor: color,
                }}
              />
              <span>{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
