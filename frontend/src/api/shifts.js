import api from "./client";

export async function fetchShifts(commodity, yearFrom, yearTo, minValue = 1000000, signal) {
  const { data } = await api.get("/shifts", {
    params: {
      commodity,
      year_from: yearFrom,
      year_to: yearTo,
      min_value: minValue,
    },
    signal,
  });
  return data;
}

export async function fetchShiftsSummary(commodity, yearFrom, yearTo, signal) {
  const { data } = await api.get("/shifts/summary", {
    params: {
      commodity,
      year_from: yearFrom,
      year_to: yearTo,
    },
    signal,
  });
  return data;
}
