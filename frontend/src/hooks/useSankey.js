import { useState, useEffect, useRef } from "react";
import { fetchSankeyData } from "../api/flows";

export default function useSankey(commodity, year, flowType) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const controllerRef = useRef(null);

  useEffect(() => {
    if (!commodity || !year) return;

    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);
    setError(null);

    fetchSankeyData(commodity, year, flowType, 30, controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!controller.signal.aborted) {
          setError(err.message || "Failed to load Sankey data");
          setLoading(false);
        }
      });

    return () => {
      controller.abort();
    };
  }, [commodity, year, flowType]);

  return { data, loading, error };
}
