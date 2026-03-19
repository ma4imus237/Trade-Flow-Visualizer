import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { ExplorerProvider } from "../../context/ExplorerContext";

// Mock the API module
vi.mock("../../api/flows", () => ({
  fetchTopFlows: vi.fn(),
}));

import { fetchTopFlows } from "../../api/flows";
import { useFlows } from "../useFlows";

const MOCK_FLOWS = [
  {
    reporter_iso3: "AUS",
    reporter_name: "Australia",
    reporter_lat: -25.0,
    reporter_lon: 134.0,
    partner_iso3: "CHN",
    partner_name: "China",
    partner_lat: 35.0,
    partner_lon: 105.0,
    commodity: "lithium",
    year: 2023,
    flow_type: "export",
    value_usd: 5_000_000_000,
    weight_kg: 50_000_000,
  },
  {
    reporter_iso3: "CHL",
    reporter_name: "Chile",
    reporter_lat: -33.0,
    reporter_lon: -71.0,
    partner_iso3: "KOR",
    partner_name: "South Korea",
    partner_lat: 37.0,
    partner_lon: 127.0,
    commodity: "lithium",
    year: 2023,
    flow_type: "export",
    value_usd: 2_000_000_000,
    weight_kg: 20_000_000,
  },
];

function wrapper({ children }) {
  return createElement(ExplorerProvider, null, children);
}

describe("useFlows", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns flows after successful fetch", async () => {
    fetchTopFlows.mockResolvedValueOnce(MOCK_FLOWS);

    const { result } = renderHook(() => useFlows(), { wrapper });

    // Initially loading
    expect(result.current.loading).toBe(true);
    expect(result.current.flows).toEqual([]);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.flows).toHaveLength(2);
    expect(result.current.error).toBeNull();
    expect(fetchTopFlows).toHaveBeenCalledWith("lithium", 2023, 200, expect.any(Object));
  });

  it("returns error on fetch failure", async () => {
    fetchTopFlows.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useFlows(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe("Network error");
    expect(result.current.flows).toEqual([]);
  });

  it("aborts request on unmount", async () => {
    let capturedSignal = null;

    fetchTopFlows.mockImplementation((commodity, year, limit, signal) => {
      capturedSignal = signal;
      // Return a promise that never resolves (simulating slow request)
      return new Promise(() => {});
    });

    const { unmount } = renderHook(() => useFlows(), { wrapper });

    // The signal should exist and not be aborted yet
    expect(capturedSignal).not.toBeNull();
    expect(capturedSignal.aborted).toBe(false);

    // Unmounting should abort the in-flight request
    unmount();
    expect(capturedSignal.aborted).toBe(true);
  });
});
