import { useState, useCallback } from "react";
import DeckGL from "@deck.gl/react";
import { Map } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import { useExplorer, useExplorerDispatch } from "../../context/ExplorerContext";
import { getCommodityColor } from "../../utils/commodities";
import { createArcLayer } from "../../layers/arcLayer";
import { createCountryLayer } from "../../layers/countryLayer";
import MapTooltip from "./MapTooltip";
import MapLegend from "./MapLegend";

const MAP_STYLE =
  "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

/**
 * Main map component using deck.gl + react-map-gl (maplibre).
 * Renders trade flow arcs and country scatter dots.
 */
export default function FlowMap({ flows }) {
  const { viewState, commodity, highlightedArc, selectedCountry } =
    useExplorer();
  const dispatch = useExplorerDispatch();
  const [hoverInfo, setHoverInfo] = useState(null);

  const commodityColor = getCommodityColor(commodity);

  const layers = [
    createCountryLayer(flows, selectedCountry),
    createArcLayer(flows, highlightedArc, commodityColor),
  ];

  const onViewStateChange = useCallback(
    ({ viewState: vs }) => {
      dispatch({ type: "SET_VIEW_STATE", payload: vs });
    },
    [dispatch],
  );

  const onHover = useCallback(
    (info) => {
      setHoverInfo(info);
      if (info.layer?.id === "trade-arcs") {
        dispatch({ type: "HIGHLIGHT_ARC", payload: info.object || null });
      }
    },
    [dispatch],
  );

  const onClick = useCallback(
    (info) => {
      if (info.layer?.id === "country-dots" && info.object) {
        dispatch({ type: "SELECT_COUNTRY", payload: info.object.iso3 });
      } else {
        dispatch({ type: "SELECT_COUNTRY", payload: null });
      }
    },
    [dispatch],
  );

  return (
    <div className="relative h-full w-full">
      <DeckGL
        viewState={viewState}
        onViewStateChange={onViewStateChange}
        controller={true}
        layers={layers}
        onHover={onHover}
        onClick={onClick}
        getCursor={({ isHovering }) => (isHovering ? "pointer" : "grab")}
      >
        <Map mapStyle={MAP_STYLE} />
      </DeckGL>
      <MapTooltip hoverInfo={hoverInfo} />
      <MapLegend commodity={commodity} />
    </div>
  );
}
