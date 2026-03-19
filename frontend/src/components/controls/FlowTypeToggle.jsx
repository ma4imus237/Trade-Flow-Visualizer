import { useExplorer, useExplorerDispatch } from "../../context/ExplorerContext";

const FLOW_OPTIONS = [
  { value: "export", label: "Export" },
  { value: "import", label: "Import" },
  { value: "both", label: "Both" },
];

/**
 * Toggle between Import / Export / Both flow types.
 */
export default function FlowTypeToggle() {
  const { flowType } = useExplorer();
  const dispatch = useExplorerDispatch();

  return (
    <div className="space-y-2">
      <label className="text-xs font-semibold uppercase tracking-wider text-gray-400">
        Flow Type
      </label>
      <div className="flex rounded-md border border-white/10">
        {FLOW_OPTIONS.map((opt) => {
          const active = opt.value === flowType;
          return (
            <button
              key={opt.value}
              onClick={() =>
                dispatch({ type: "SET_FLOW_TYPE", payload: opt.value })
              }
              className={`flex-1 px-3 py-1.5 text-xs font-medium transition-colors first:rounded-l-md last:rounded-r-md ${
                active
                  ? "bg-white/15 text-white"
                  : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
              }`}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
