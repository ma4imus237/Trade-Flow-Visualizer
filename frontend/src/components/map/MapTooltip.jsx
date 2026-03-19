import { formatUSD, formatWeight } from "../../utils/formatters";

/**
 * Floating tooltip that renders on arc or country hover.
 * Receives hoverInfo from deck.gl picking.
 */
export default function MapTooltip({ hoverInfo }) {
  if (!hoverInfo || !hoverInfo.object) return null;

  const { x, y, object, layer } = hoverInfo;
  const isArc = layer?.id === "trade-arcs";

  return (
    <div
      className="pointer-events-none absolute z-50 rounded-lg bg-gray-900/95 px-3 py-2 text-sm text-white shadow-xl backdrop-blur-sm"
      style={{
        left: x + 12,
        top: y - 12,
        maxWidth: 280,
      }}
    >
      {isArc ? (
        <ArcTooltipContent flow={object} />
      ) : (
        <CountryTooltipContent country={object} />
      )}
    </div>
  );
}

function ArcTooltipContent({ flow }) {
  return (
    <div className="space-y-1">
      <p className="font-semibold">
        {flow.reporter_name}
        <span className="mx-1 text-gray-400">&rarr;</span>
        {flow.partner_name}
      </p>
      <div className="flex items-center gap-3 text-xs text-gray-300">
        <span>{formatUSD(flow.value_usd)}</span>
        <span className="text-gray-500">|</span>
        <span>{formatWeight(flow.weight_kg)}</span>
      </div>
    </div>
  );
}

function CountryTooltipContent({ country }) {
  return (
    <div className="space-y-1">
      <p className="font-semibold">{country.name}</p>
      <div className="flex flex-col gap-0.5 text-xs text-gray-300">
        <span>Exports: {formatUSD(country.totalExport)}</span>
        <span>Imports: {formatUSD(country.totalImport)}</span>
      </div>
    </div>
  );
}
