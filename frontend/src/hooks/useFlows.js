import { useState, useEffect, useRef, useMemo } from "react";
import { useExplorer } from "../context/ExplorerContext";
import { fetchTopFlows } from "../api/flows";

/**
 * Custom hook that fetches trade flows reactively when
 * commodity, year, or flowType change.
 * Filters by minValue client-side.
 * Uses AbortController for cancellation on re-fetch.
 */
export function useFlows() {
  const { commodity, year, flowType, minValue } = useExplorer();
  const [rawFlows, setRawFlows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  useEffect(() => {
    // Abort any in-flight request
    if (abortRef.current) {
      abortRef.current.abort();
    }

    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);

    fetchTopFlows(commodity, year, 200, controller.signal)
      .then((data) => {
        setRawFlows(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name === "CanceledError" || err.name === "AbortError") {
          return; // Ignore aborted requests
        }
        setError(err.message || "Failed to fetch flows");
        setLoading(false);
      });

    return () => {
      controller.abort();
    };
  }, [commodity, year]);

  // Filter by flowType and minValue client-side
  const flows = useMemo(() => {
    let filtered = rawFlows;

    if (flowType !== "both") {
      filtered = filtered.filter((f) => f.flow_type === flowType);
    }

    if (minValue > 0) {
      filtered = filtered.filter((f) => f.value_usd >= minValue);
    }

    return filtered;
  }, [rawFlows, flowType, minValue]);

  return { flows, loading, error };
}
