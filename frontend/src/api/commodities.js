import api from "./client";

export async function fetchCommodities(signal) {
  const { data } = await api.get("/commodities", { signal });
  return data;
}

export async function fetchYears(signal) {
  const { data } = await api.get("/years", { signal });
  return data;
}
