export const COMMODITY_COLORS = {
  lithium: "#06b6d4",
  cobalt: "#8b5cf6",
  rare_earths: "#f59e0b",
  copper: "#ef4444",
  uranium: "#22c55e",
  nickel: "#ec4899",
  graphite: "#6b7280",
};

export const COMMODITY_LIST = [
  { code: "lithium", name: "Lithium", color: "#06b6d4" },
  { code: "cobalt", name: "Cobalt", color: "#8b5cf6" },
  { code: "rare_earths", name: "Rare Earths", color: "#f59e0b" },
  { code: "copper", name: "Copper", color: "#ef4444" },
  { code: "uranium", name: "Uranium", color: "#22c55e" },
  { code: "nickel", name: "Nickel", color: "#ec4899" },
  { code: "graphite", name: "Graphite", color: "#6b7280" },
];

export function getCommodityColor(commodity) {
  return COMMODITY_COLORS[commodity] || "#6b7280";
}
