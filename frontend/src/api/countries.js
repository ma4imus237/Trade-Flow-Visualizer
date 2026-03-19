import api from "./client";

export async function fetchCountryProfile(iso3, year, commodity, signal) {
  const { data } = await api.get(`/countries/${iso3}/profile`, {
    params: { year, commodity },
    signal,
  });
  return data;
}

export async function fetchCountryPartners(iso3, year, commodity, flowType, signal) {
  const { data } = await api.get(`/countries/${iso3}/partners`, {
    params: { year, commodity, flow_type: flowType },
    signal,
  });
  return data;
}
