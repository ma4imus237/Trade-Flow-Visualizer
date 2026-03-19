import { useState, useEffect, useRef } from "react";
import { fetchShifts, fetchShiftsSummary } from "../api/shifts";

export default function useShifts(commodity, yearFrom, yearTo, minValue = 1000000) {
  const [shifts, setShifts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const controllerRef = useRef(null);

  useEffect(() => {
    if (!commodity || !yearFrom || !yearTo) return;

    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);
    setError(null);

    Promise.all([
      fetchShifts(commodity, yearFrom, yearTo, minValue, controller.signal),
      fetchShiftsSummary(commodity, yearFrom, yearTo, controller.signal),
    ])
      .then(([shiftsResult, summaryResult]) => {
        if (!controller.signal.aborted) {
          setShifts(shiftsResult);
          setSummary(summaryResult);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!controller.signal.aborted) {
          setError(err.message || "Failed to load shift data");
          setLoading(false);
        }
      });

    return () => {
      controller.abort();
    };
  }, [commodity, yearFrom, yearTo, minValue]);

  return { shifts, summary, loading, error };
}
