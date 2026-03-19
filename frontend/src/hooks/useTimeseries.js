import { useState, useEffect, useRef } from "react";
import { fetchTimeseries } from "../api/flows";

export default function useTimeseries(reporter, partner, commodity) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const controllerRef = useRef(null);

  useEffect(() => {
    if (!reporter || !partner || !commodity) {
      setData([]);
      return;
    }

    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);
    setError(null);

    fetchTimeseries(reporter, partner, commodity, controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!controller.signal.aborted) {
          setError(err.message || "Failed to load timeseries");
          setLoading(false);
        }
      });

    return () => {
      controller.abort();
    };
  }, [reporter, partner, commodity]);

  return { data, loading, error };
}
