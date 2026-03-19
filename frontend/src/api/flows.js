import api from "./client";

export async function fetchTopFlows(commodity, year, limit = 200, signal) {
  const { data } = await api.get("/flows/top", {
    params: { commodity, year, limit },
    signal,
  });
  return data;
}

export async function fetchSankeyData(commodity, year, flowType, limit = 50, signal) {
  const { data } = await api.get("/flows/sankey", {
    params: { commodity, year, flow_type: flowType, limit },
    signal,
  });
  return data;
}

export async function fetchTimeseries(reporter, partner, commodity, signal) {
  const { data } = await api.get("/flows/timeseries", {
    params: { reporter, partner, commodity },
    signal,
  });
  return data;
}
