import { useState, useEffect, useRef } from "react";
import { fetchCountryProfile } from "../api/countries";

export default function useCountryProfile(iso3, year, commodity) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const controllerRef = useRef(null);

  useEffect(() => {
    if (!iso3) {
      setProfile(null);
      setLoading(false);
      setError(null);
      return;
    }

    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);
    setError(null);

    fetchCountryProfile(iso3, year, commodity, controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) {
          setProfile(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!controller.signal.aborted) {
          setError(err.message || "Failed to load country profile");
          setLoading(false);
        }
      });

    return () => {
      controller.abort();
    };
  }, [iso3, year, commodity]);

  return { profile, loading, error };
}
