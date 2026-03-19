import { ArcLayer } from "@deck.gl/layers";
import { hexToRgba } from "../utils/formatters";

/**
 * Creates a deck.gl ArcLayer for trade flow arcs.
 */
export function createArcLayer(flows, highlightedArc, commodityColor) {
  const color = hexToRgba(commodityColor, 200);
  const colorDim = hexToRgba(commodityColor, 60);

  return new ArcLayer({
    id: "trade-arcs",
    data: flows,
    getSourcePosition: (d) => [d.reporter_lon, d.reporter_lat],
    getTargetPosition: (d) => [d.partner_lon, d.partner_lat],
    getSourceColor: (d) => {
      if (!highlightedArc) return color;
      const isHighlighted =
        d.reporter_iso3 === highlightedArc.reporter_iso3 &&
        d.partner_iso3 === highlightedArc.partner_iso3;
      return isHighlighted ? hexToRgba(commodityColor, 255) : colorDim;
    },
    getTargetColor: (d) => {
      if (!highlightedArc) return color;
      const isHighlighted =
        d.reporter_iso3 === highlightedArc.reporter_iso3 &&
        d.partner_iso3 === highlightedArc.partner_iso3;
      return isHighlighted ? hexToRgba(commodityColor, 255) : colorDim;
    },
    getWidth: (d) => Math.max(1, Math.log(d.value_usd / 1e6) * 2),
    getTilt: 15,
    pickable: true,
    autoHighlight: true,
    highlightColor: hexToRgba(commodityColor, 255),
    updateTriggers: {
      getSourceColor: [highlightedArc, commodityColor],
      getTargetColor: [highlightedArc, commodityColor],
    },
  });
}
