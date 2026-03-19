import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import SankeyDiagram from "../SankeyDiagram";

// Mock react-plotly.js to avoid requiring actual Plotly in tests
vi.mock("react-plotly.js", () => ({
  default: ({ data, layout, onClick }) => (
    <div data-testid="plotly-chart" data-traces={data?.length ?? 0}>
      Plotly Chart
    </div>
  ),
}));

// Mock the hooks and context
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

const sampleData = {
  nodes: [
    { id: "AUS", name: "Australia" },
    { id: "CHN", name: "China" },
  ],
  links: [{ source: 0, target: 1, value: 5000000 }],
};

vi.mock("../../../hooks/useSankey", () => ({
  default: vi.fn(),
}));

import useSankey from "../../../hooks/useSankey";

describe("SankeyDiagram", () => {
  it("renders loading state", () => {
    useSankey.mockReturnValue({ data: null, loading: true, error: null });
    render(<SankeyDiagram />);
    expect(screen.getByText(/loading sankey/i)).toBeInTheDocument();
  });

  it("renders empty state when no data", () => {
    useSankey.mockReturnValue({ data: null, loading: false, error: null });
    render(<SankeyDiagram />);
    expect(screen.getByText(/no trade flow data/i)).toBeInTheDocument();
  });

  it("renders empty state for empty nodes/links", () => {
    useSankey.mockReturnValue({
      data: { nodes: [], links: [] },
      loading: false,
      error: null,
    });
    render(<SankeyDiagram />);
    expect(screen.getByText(/no trade flow data/i)).toBeInTheDocument();
  });

  it("renders error state", () => {
    useSankey.mockReturnValue({
      data: null,
      loading: false,
      error: "Network error",
    });
    render(<SankeyDiagram />);
    expect(screen.getByText(/network error/i)).toBeInTheDocument();
  });

  it("renders Plotly chart with sample data", () => {
    useSankey.mockReturnValue({
      data: sampleData,
      loading: false,
      error: null,
    });
    render(<SankeyDiagram />);
    expect(screen.getByTestId("plotly-chart")).toBeInTheDocument();
  });
});
