import { useExplorerDispatch } from "../../context/ExplorerContext";
import { formatUSD, formatChangePct } from "../../utils/formatters";
import { shiftBgClass } from "../../utils/colorScales";

function ShiftBadge({ type }) {
  const label =
    type === "surge"
      ? "Surge"
      : type === "collapse"
        ? "Collapse"
        : type === "new"
          ? "New Flow"
          : type === "abandoned"
            ? "Abandoned"
            : type;

  return (
    <span
      className={`inline-block px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded border ${shiftBgClass(type)}`}
    >
      {label}
    </span>
  );
}

function ShiftCard({ shift, onClick }) {
  const isPositive =
    shift.shift_type === "surge" || shift.shift_type === "new";

  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full text-left p-3 rounded-lg bg-gray-800/60 hover:bg-gray-800/80 border border-gray-700/40 hover:border-gray-600/60 transition-all cursor-pointer group"
    >
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <p className="text-sm text-gray-200 font-medium leading-tight">
          {shift.reporter_name || shift.reporter_iso3}
          <span className="text-gray-500 mx-1.5">&rarr;</span>
          {shift.partner_name || shift.partner_iso3}
        </p>
        <ShiftBadge type={shift.shift_type} />
      </div>
      <div className="flex items-center gap-3 text-xs">
        <span className={isPositive ? "text-green-400" : "text-red-400"}>
          {formatChangePct(shift.change_pct)}
        </span>
        <span className="text-gray-500">
          {formatUSD(shift.value_from)} &rarr; {formatUSD(shift.value_to)}
        </span>
      </div>
      {shift.change_abs != null && (
        <p className="text-xs text-gray-500 mt-1">
          {shift.change_abs >= 0 ? "+" : ""}
          {formatUSD(shift.change_abs)} absolute
        </p>
      )}
    </button>
  );
}

export default function ShiftAlerts({ shifts = [], loading = false }) {
  const dispatch = useExplorerDispatch();

  const handleShiftClick = (shift) => {
    dispatch({
      type: "SET_VIEW_STATE",
      payload: {
        longitude: 0,
        latitude: 20,
        zoom: 2.5,
        pitch: 30,
        bearing: 0,
        transitionDuration: 800,
      },
    });
    dispatch({
      type: "HIGHLIGHT_ARC",
      payload: {
        reporter: shift.reporter_iso3,
        partner: shift.partner_iso3,
      },
    });
  };

  if (loading) {
    return (
      <div className="space-y-3 p-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="animate-pulse h-20 bg-gray-800/60 rounded-lg"
          />
        ))}
      </div>
    );
  }

  if (!shifts || shifts.length === 0) {
    return (
      <div className="flex items-center justify-center h-full min-h-[200px]">
        <p className="text-sm text-gray-500">No significant trade shifts detected.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 p-1 overflow-y-auto">
      <p className="text-xs text-gray-500 px-1 mb-2">
        {shifts.length} shift{shifts.length !== 1 ? "s" : ""} detected
      </p>
      {shifts.map((shift, idx) => (
        <ShiftCard
          key={`${shift.reporter_iso3}-${shift.partner_iso3}-${idx}`}
          shift={shift}
          onClick={() => handleShiftClick(shift)}
        />
      ))}
    </div>
  );
}
