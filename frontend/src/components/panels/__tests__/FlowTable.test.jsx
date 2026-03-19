import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import FlowTable from "../FlowTable";

const mockState = {
  commodity: "lithium",
  year: 2023,
  flowType: "export",
  selectedCountry: null,
  highlightedArc: null,
  minValue: 0,
  isPlaying: false,
  viewState: { longitude: 0, latitude: 20, zoom: 1.5, pitch: 30, bearing: 0 },
};
const mockDispatch = vi.fn();

vi.mock("../../../context/ExplorerContext", () => ({
  useExplorer: () => mockState,
  useExplorerDispatch: () => mockDispatch,
}));

const sampleFlows = [
  {
    reporter_iso3: "AUS",
    reporter_name: "Australia",
    partner_iso3: "CHN",
    partner_name: "China",
    value_usd: 5000000,
    weight_kg: 1500000,
    change_pct: 12.5,
  },
  {
    reporter_iso3: "CHL",
    reporter_name: "Chile",
    partner_iso3: "KOR",
    partner_name: "South Korea",
    value_usd: 3000000,
    weight_kg: 900000,
    change_pct: -8.3,
  },
  {
    reporter_iso3: "ARG",
    reporter_name: "Argentina",
    partner_iso3: "USA",
    partner_name: "United States",
    value_usd: 7000000,
    weight_kg: 2000000,
    change_pct: 45.0,
  },
];

describe("FlowTable", () => {
  it("renders empty state when no flows", () => {
    render(<FlowTable flows={[]} />);
    expect(screen.getByText(/no flow data/i)).toBeInTheDocument();
  });

  it("renders table with sample data", () => {
    render(<FlowTable flows={sampleFlows} />);
    expect(screen.getByText("Australia")).toBeInTheDocument();
    expect(screen.getByText("China")).toBeInTheDocument();
    expect(screen.getByText("Chile")).toBeInTheDocument();
    expect(screen.getByText("South Korea")).toBeInTheDocument();
  });

  it("renders all column headers", () => {
    render(<FlowTable flows={sampleFlows} />);
    expect(screen.getByText("Reporter")).toBeInTheDocument();
    expect(screen.getByText("Partner")).toBeInTheDocument();
    expect(screen.getByText("Value (USD)")).toBeInTheDocument();
    expect(screen.getByText("Weight")).toBeInTheDocument();
    expect(screen.getByText("Change %")).toBeInTheDocument();
  });

  it("sorts by clicking column header", () => {
    render(<FlowTable flows={sampleFlows} />);

    // Default sort is by value_usd desc, so Argentina (7M) should be first
    const rows = screen.getAllByRole("row");
    // Row 0 is header, row 1 is first data row
    expect(rows[1]).toHaveTextContent("Argentina");

    // Click on Reporter header to sort by name
    fireEvent.click(screen.getByText("Reporter"));

    const rowsAfterSort = screen.getAllByRole("row");
    // Descending alphabetical: Chile first
    expect(rowsAfterSort[1]).toHaveTextContent("Chile");
  });

  it("dispatches HIGHLIGHT_ARC on row click", () => {
    render(<FlowTable flows={sampleFlows} />);
    const rows = screen.getAllByRole("row");
    fireEvent.click(rows[1]); // click first data row
    expect(mockDispatch).toHaveBeenCalledWith({
      type: "HIGHLIGHT_ARC",
      payload: expect.objectContaining({
        reporter: expect.any(String),
        partner: expect.any(String),
      }),
    });
  });
});
