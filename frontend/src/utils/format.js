/**
 * Format a USD value into a human-readable string.
 * e.g., 1_500_000_000 -> "$1.5B", 23_000_000 -> "$23M", 750_000 -> "$750K"
 */
export function formatUSD(value) {
  if (value == null || isNaN(value)) return "$0";
  const abs = Math.abs(value);
  if (abs >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
  if (abs >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (abs >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  if (abs >= 1e3) return `$${(value / 1e3).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
}

/**
 * Format weight in kg to human-readable tonnes.
 * e.g., 45_000_000 -> "45,000 t"
 */
export function formatWeight(kg) {
  if (kg == null || isNaN(kg)) return "0 t";
  const tonnes = kg / 1000;
  return `${tonnes.toLocaleString("en-US", { maximumFractionDigits: 0 })} t`;
}

/**
 * Parse a hex color string to an RGBA array.
 * e.g., "#06b6d4" -> [6, 182, 212, 255]
 */
export function hexToRgba(hex, alpha = 255) {
  const h = hex.replace("#", "");
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  return [r, g, b, alpha];
}
