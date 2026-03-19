import { useExplorer, useExplorerDispatch } from "../../context/ExplorerContext";
import { COMMODITY_LIST } from "../../utils/commodities";

/**
 * Button group for selecting one of the 7 commodities.
 */
export default function CommoditySelector() {
  const { commodity } = useExplorer();
  const dispatch = useExplorerDispatch();

  return (
    <div className="space-y-2">
      <label className="text-xs font-semibold uppercase tracking-wider text-gray-400">
        Commodity
      </label>
      <div className="flex flex-wrap gap-1.5">
        {COMMODITY_LIST.map((item) => {
          const active = item.code === commodity;
          return (
            <button
              key={item.code}
              onClick={() =>
                dispatch({ type: "SET_COMMODITY", payload: item.code })
              }
              className={`flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors ${
                active
                  ? "bg-white/15 text-white ring-1 ring-white/20"
                  : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
              }`}
            >
              <span
                className="inline-block h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              {item.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}
