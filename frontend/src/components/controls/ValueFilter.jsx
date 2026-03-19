import { useExplorer, useExplorerDispatch } from "../../context/ExplorerContext";
import { formatUSD } from "../../utils/format";

const MIN = 0;
const MAX = 1e10; // $10B
const STEP = 1e6; // $1M increments

/**
 * Range slider for filtering flows by minimum trade value.
 */
export default function ValueFilter() {
  const { minValue } = useExplorer();
  const dispatch = useExplorerDispatch();

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label
          htmlFor="value-filter"
          className="text-xs font-semibold uppercase tracking-wider text-gray-400"
        >
          Min Value
        </label>
        <span className="text-xs font-medium text-cyan-400">
          {formatUSD(minValue)}
        </span>
      </div>
      <input
        id="value-filter"
        type="range"
        min={MIN}
        max={MAX}
        step={STEP}
        value={minValue}
        onChange={(e) =>
          dispatch({ type: "SET_MIN_VALUE", payload: Number(e.target.value) })
        }
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-gray-700 accent-cyan-400"
      />
      <div className="flex justify-between text-[10px] text-gray-500">
        <span>$0</span>
        <span>$10B</span>
      </div>
    </div>
  );
}
