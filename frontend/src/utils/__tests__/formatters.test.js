import { describe, it, expect } from "vitest";
import { formatUSD, formatWeight, formatChangePct } from "../formatters";

describe("formatUSD", () => {
  it("formats trillions", () => {
    expect(formatUSD(1.5e12)).toBe("$1.5T");
  });

  it("formats billions", () => {
    expect(formatUSD(2.3e9)).toBe("$2.3B");
    expect(formatUSD(1e9)).toBe("$1.0B");
  });

  it("formats millions", () => {
    expect(formatUSD(340e6)).toBe("$340.0M");
    expect(formatUSD(1.2e6)).toBe("$1.2M");
  });

  it("formats thousands", () => {
    expect(formatUSD(5600)).toBe("$5.6K");
    expect(formatUSD(1000)).toBe("$1.0K");
  });

  it("formats small values", () => {
    expect(formatUSD(500)).toBe("$500");
    expect(formatUSD(0)).toBe("$0");
  });

  it("handles null and NaN", () => {
    expect(formatUSD(null)).toBe("$0");
    expect(formatUSD(undefined)).toBe("$0");
    expect(formatUSD(NaN)).toBe("$0");
  });

  it("handles negative values", () => {
    expect(formatUSD(-2.3e9)).toBe("-$2.3B");
    expect(formatUSD(-5e6)).toBe("-$5.0M");
  });
});

describe("formatWeight", () => {
  it("formats millions of tonnes", () => {
    expect(formatWeight(1.5e9)).toBe("1.5M tonnes");
  });

  it("formats thousands of tonnes", () => {
    expect(formatWeight(5e6)).toBe("5.0K tonnes");
    expect(formatWeight(1.2e6)).toBe("1.2K tonnes");
  });

  it("formats small tonnage", () => {
    expect(formatWeight(5000)).toBe("5 tonnes");
    expect(formatWeight(500)).toBe("1 tonnes");
  });

  it("handles null and NaN", () => {
    expect(formatWeight(null)).toBe("0 tonnes");
    expect(formatWeight(undefined)).toBe("0 tonnes");
    expect(formatWeight(NaN)).toBe("0 tonnes");
  });
});

describe("formatChangePct", () => {
  it("formats positive percentages with plus sign", () => {
    expect(formatChangePct(25.3)).toBe("+25.3%");
    expect(formatChangePct(0)).toBe("+0.0%");
  });

  it("formats negative percentages", () => {
    expect(formatChangePct(-15.7)).toBe("-15.7%");
  });

  it("formats large percentages", () => {
    expect(formatChangePct(1500.5)).toBe("+1500.5%");
  });

  it("handles null and NaN", () => {
    expect(formatChangePct(null)).toBe("0.0%");
    expect(formatChangePct(NaN)).toBe("0.0%");
  });
});
