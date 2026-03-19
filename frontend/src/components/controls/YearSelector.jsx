import { useExplorer, useExplorerDispatch } from "../../context/ExplorerContext";

const YEARS = Array.from({ length: 14 }, (_, i) => 2010 + i);

/**
 * Dropdown selector for the year.
 */
export default function YearSelector() {
  const { year } = useExplorer();
  const dispatch = useExplorerDispatch();

  return (
    <div className="space-y-2">
      <label
        htmlFor="year-select"
        className="text-xs font-semibold uppercase tracking-wider text-gray-400"
      >
        Year
      </label>
      <select
        id="year-select"
        value={year}
        onChange={(e) =>
          dispatch({ type: "SET_YEAR", payload: Number(e.target.value) })
        }
        className="w-full rounded-md border border-white/10 bg-gray-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-cyan-400"
      >
        {YEARS.map((y) => (
          <option key={y} value={y}>
            {y}
          </option>
        ))}
      </select>
    </div>
  );
}
