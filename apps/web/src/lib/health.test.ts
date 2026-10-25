import { describe, expect, it } from "vitest";

import { summarizeHealth } from "./health";

describe("summarizeHealth", () => {
  it("reports operational when every check is ok", () => {
    const summary = summarizeHealth({
      status: "ok",
      checks: { database: "ok", redis: "ok" },
    });

    expect(summary).toEqual({ tone: "ok", label: "All systems operational", failing: [] });
  });

  it("lists failing checks when degraded", () => {
    const summary = summarizeHealth({
      status: "degraded",
      checks: { database: "ok", redis: "unavailable" },
    });

    expect(summary.tone).toBe("degraded");
    expect(summary.failing).toEqual(["redis"]);
  });

  it("reports the API as down when there is no payload", () => {
    expect(summarizeHealth(null).tone).toBe("down");
  });
});
