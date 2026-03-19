export function hexToRgba(hex, alpha = 255) {
  const h = hex.replace("#", "");
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  return [r, g, b, alpha];
}

export function formatUSD(value) {
  if (value == null || isNaN(value)) return "$0";
  const abs = Math.abs(value);
  const sign = value < 0 ? "-" : "";
  if (abs >= 1e12) return `${sign}$${(abs / 1e12).toFixed(1)}T`;
  if (abs >= 1e9) return `${sign}$${(abs / 1e9).toFixed(1)}B`;
  if (abs >= 1e6) return `${sign}$${(abs / 1e6).toFixed(1)}M`;
  if (abs >= 1e3) return `${sign}$${(abs / 1e3).toFixed(1)}K`;
  return `${sign}$${abs.toFixed(0)}`;
}

export function formatWeight(kg) {
  if (kg == null || isNaN(kg)) return "0 tonnes";
  const tonnes = kg / 1000;
  if (tonnes >= 1e6) return `${(tonnes / 1e6).toFixed(1)}M tonnes`;
  if (tonnes >= 1e3) return `${(tonnes / 1e3).toFixed(1)}K tonnes`;
  return `${tonnes.toFixed(0)} tonnes`;
}

export function formatChangePct(pct) {
  if (pct == null || isNaN(pct)) return "0.0%";
  const sign = pct >= 0 ? "+" : "";
  return `${sign}${pct.toFixed(1)}%`;
}

export function formatNumber(value) {
  if (value == null || isNaN(value)) return "0";
  return value.toLocaleString("en-US");
}
