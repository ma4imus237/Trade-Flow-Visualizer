import { ScatterplotLayer } from "@deck.gl/layers";

/**
 * Extracts unique countries from flows and aggregates total trade value.
 */
function extractCountries(flows) {
  const map = new Map();

  for (const f of flows) {
    // Reporter side
    if (!map.has(f.reporter_iso3)) {
      map.set(f.reporter_iso3, {
        iso3: f.reporter_iso3,
        name: f.reporter_name,
        lon: f.reporter_lon,
        lat: f.reporter_lat,
        totalExport: 0,
        totalImport: 0,
      });
    }
    const reporter = map.get(f.reporter_iso3);
    if (f.flow_type === "export") {
      reporter.totalExport += f.value_usd;
    } else {
      reporter.totalImport += f.value_usd;
    }

    // Partner side
    if (!map.has(f.partner_iso3)) {
      map.set(f.partner_iso3, {
        iso3: f.partner_iso3,
        name: f.partner_name,
        lon: f.partner_lon,
        lat: f.partner_lat,
        totalExport: 0,
        totalImport: 0,
      });
    }
    const partner = map.get(f.partner_iso3);
    if (f.flow_type === "export") {
      partner.totalImport += f.value_usd;
    } else {
      partner.totalExport += f.value_usd;
    }
  }

  return Array.from(map.values());
}

/**
 * Creates a deck.gl ScatterplotLayer for country markers.
 */
export function createCountryLayer(flows, selectedCountry) {
  const countries = extractCountries(flows);

  return new ScatterplotLayer({
    id: "country-dots",
    data: countries,
    getPosition: (d) => [d.lon, d.lat],
    getRadius: (d) => {
      const total = d.totalExport + d.totalImport;
      return Math.max(20000, Math.sqrt(total / 1e6) * 5000);
    },
    getFillColor: (d) => {
      if (selectedCountry && d.iso3 === selectedCountry) {
        return [255, 255, 255, 220];
      }
      return [200, 200, 200, 140];
    },
    getLineColor: [255, 255, 255, 80],
    lineWidthMinPixels: 1,
    stroked: true,
    pickable: true,
    radiusMinPixels: 3,
    radiusMaxPixels: 30,
    updateTriggers: {
      getFillColor: [selectedCountry],
    },
  });
}

export { extractCountries };
