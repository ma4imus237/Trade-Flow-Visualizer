import { useEffect } from "react";
import { useExplorer, useExplorerDispatch } from "../../context/ExplorerContext";

const YEAR_MIN = 2010;
const YEAR_MAX = 2023;
const INTERVAL_MS = 1500;

/**
 * Year scrubber with play/pause auto-advance.
 * When playing, auto-advances year every 1.5 seconds, wrapping to YEAR_MIN after YEAR_MAX.
 */
export default function TimeSlider() {
  const { year, isPlaying } = useExplorer();
  const dispatch = useExplorerDispatch();

  useEffect(() => {
    if (!isPlaying) return;

    const id = setTimeout(() => {
      const nextYear = year >= YEAR_MAX ? YEAR_MIN : year + 1;
      dispatch({ type: "SET_YEAR", payload: nextYear });
    }, INTERVAL_MS);

    return () => clearTimeout(id);
  }, [isPlaying, year, dispatch]);

  const togglePlay = () => {
    dispatch({ type: "SET_PLAYING", payload: !isPlaying });
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold uppercase tracking-wider text-gray-400">
          Timeline
        </label>
        <span className="text-lg font-bold tabular-nums text-white">
          {year}
        </span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={togglePlay}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/10 text-white transition-colors hover:bg-white/10"
          aria-label={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="h-4 w-4"
            >
              <path d="M5.75 3a.75.75 0 0 0-.75.75v12.5c0 .414.336.75.75.75h1.5a.75.75 0 0 0 .75-.75V3.75A.75.75 0 0 0 7.25 3h-1.5ZM12.75 3a.75.75 0 0 0-.75.75v12.5c0 .414.336.75.75.75h1.5a.75.75 0 0 0 .75-.75V3.75a.75.75 0 0 0-.75-.75h-1.5Z" />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="h-4 w-4"
            >
              <path d="M6.3 2.84A1.5 1.5 0 0 0 4 4.11v11.78a1.5 1.5 0 0 0 2.3 1.27l9.344-5.891a1.5 1.5 0 0 0 0-2.538L6.3 2.841Z" />
            </svg>
          )}
        </button>

        <input
          type="range"
          min={YEAR_MIN}
          max={YEAR_MAX}
          step={1}
          value={year}
          onChange={(e) =>
            dispatch({ type: "SET_YEAR", payload: Number(e.target.value) })
          }
          className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-gray-700 accent-cyan-400"
        />
      </div>

      <div className="flex justify-between text-[10px] text-gray-500">
        <span>{YEAR_MIN}</span>
        <span>{YEAR_MAX}</span>
      </div>
    </div>
  );
}
