export { COMMODITY_COLORS, getCommodityColor } from "./commodities";

export function shiftColor(shiftType) {
  switch (shiftType) {
    case "surge":
      return "#22c55e";
    case "collapse":
      return "#ef4444";
    case "new":
      return "#06b6d4";
    case "abandoned":
      return "#f59e0b";
    default:
      return "#6b7280";
  }
}

export function shiftBgClass(shiftType) {
  switch (shiftType) {
    case "surge":
      return "bg-green-500/20 text-green-400 border-green-500/30";
    case "collapse":
      return "bg-red-500/20 text-red-400 border-red-500/30";
    case "new":
      return "bg-cyan-500/20 text-cyan-400 border-cyan-500/30";
    case "abandoned":
      return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    default:
      return "bg-gray-500/20 text-gray-400 border-gray-500/30";
  }
}
