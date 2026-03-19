import { describe, it, expect } from "vitest";
import { render, screen, act } from "@testing-library/react";
import {
  ExplorerProvider,
  useExplorer,
  useExplorerDispatch,
} from "../ExplorerContext";

function TestConsumer() {
  const state = useExplorer();
  const dispatch = useExplorerDispatch();
  return (
    <div>
      <span data-testid="commodity">{state.commodity}</span>
      <span data-testid="year">{state.year}</span>
      <span data-testid="flowType">{state.flowType}</span>
      <span data-testid="selectedCountry">{state.selectedCountry || "none"}</span>
      <span data-testid="minValue">{state.minValue}</span>
      <span data-testid="isPlaying">{String(state.isPlaying)}</span>
      <button
        data-testid="set-commodity"
        onClick={() => dispatch({ type: "SET_COMMODITY", payload: "cobalt" })}
      />
      <button
        data-testid="set-year"
        onClick={() => dispatch({ type: "SET_YEAR", payload: 2020 })}
      />
      <button
        data-testid="set-flow-type"
        onClick={() => dispatch({ type: "SET_FLOW_TYPE", payload: "import" })}
      />
      <button
        data-testid="select-country"
        onClick={() => dispatch({ type: "SELECT_COUNTRY", payload: "USA" })}
      />
      <button
        data-testid="set-min-value"
        onClick={() => dispatch({ type: "SET_MIN_VALUE", payload: 1000000 })}
      />
      <button
        data-testid="set-playing"
        onClick={() => dispatch({ type: "SET_PLAYING", payload: true })}
      />
      <button
        data-testid="reset"
        onClick={() => dispatch({ type: "RESET" })}
      />
    </div>
  );
}

describe("ExplorerContext", () => {
  it("provides initial state", () => {
    render(
      <ExplorerProvider>
        <TestConsumer />
      </ExplorerProvider>,
    );

    expect(screen.getByTestId("commodity").textContent).toBe("lithium");
    expect(screen.getByTestId("year").textContent).toBe("2023");
    expect(screen.getByTestId("flowType").textContent).toBe("export");
    expect(screen.getByTestId("selectedCountry").textContent).toBe("none");
    expect(screen.getByTestId("minValue").textContent).toBe("0");
    expect(screen.getByTestId("isPlaying").textContent).toBe("false");
  });

  it("dispatches SET_COMMODITY", () => {
    render(
      <ExplorerProvider>
        <TestConsumer />
      </ExplorerProvider>,
    );

    act(() => screen.getByTestId("set-commodity").click());
    expect(screen.getByTestId("commodity").textContent).toBe("cobalt");
  });

  it("dispatches SET_YEAR", () => {
    render(
      <ExplorerProvider>
        <TestConsumer />
      </ExplorerProvider>,
    );

    act(() => screen.getByTestId("set-year").click());
    expect(screen.getByTestId("year").textContent).toBe("2020");
  });

  it("dispatches SET_FLOW_TYPE", () => {
    render(
      <ExplorerProvider>
        <TestConsumer />
      </ExplorerProvider>,
    );

    act(() => screen.getByTestId("set-flow-type").click());
    expect(screen.getByTestId("flowType").textContent).toBe("import");
  });

  it("dispatches SELECT_COUNTRY", () => {
    render(
      <ExplorerProvider>
        <TestConsumer />
      </ExplorerProvider>,
    );

    act(() => screen.getByTestId("select-country").click());
    expect(screen.getByTestId("selectedCountry").textContent).toBe("USA");
  });

  it("dispatches SET_MIN_VALUE", () => {
    render(
      <ExplorerProvider>
        <TestConsumer />
      </ExplorerProvider>,
    );

    act(() => screen.getByTestId("set-min-value").click());
    expect(screen.getByTestId("minValue").textContent).toBe("1000000");
  });

  it("dispatches SET_PLAYING", () => {
    render(
      <ExplorerProvider>
        <TestConsumer />
      </ExplorerProvider>,
    );

    act(() => screen.getByTestId("set-playing").click());
    expect(screen.getByTestId("isPlaying").textContent).toBe("true");
  });

  it("dispatches RESET to return to initial state", () => {
    render(
      <ExplorerProvider>
        <TestConsumer />
      </ExplorerProvider>,
    );

    act(() => screen.getByTestId("set-commodity").click());
    act(() => screen.getByTestId("set-year").click());
    expect(screen.getByTestId("commodity").textContent).toBe("cobalt");
    expect(screen.getByTestId("year").textContent).toBe("2020");

    act(() => screen.getByTestId("reset").click());
    expect(screen.getByTestId("commodity").textContent).toBe("lithium");
    expect(screen.getByTestId("year").textContent).toBe("2023");
  });

  it("renders children within provider", () => {
    render(
      <ExplorerProvider>
        <div data-testid="child">Hello</div>
      </ExplorerProvider>,
    );

    expect(screen.getByTestId("child").textContent).toBe("Hello");
  });

  it("throws when useExplorer is used outside provider", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<TestConsumer />)).toThrow(
      "useExplorer must be used within ExplorerProvider",
    );
    spy.mockRestore();
  });
});
