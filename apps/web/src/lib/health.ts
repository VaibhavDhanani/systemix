export type HealthPayload = {
  status: "ok" | "degraded";
  checks: Record<string, "ok" | "unavailable">;
};

export type HealthSummary = {
  tone: "ok" | "degraded" | "down";
  label: string;
  failing: string[];
};

/** Turns a /api/health result (or a failed request) into something the UI can show. */
export function summarizeHealth(payload: HealthPayload | null): HealthSummary {
  if (payload === null) {
    return { tone: "down", label: "API unreachable", failing: [] };
  }
  const failing = Object.entries(payload.checks)
    .filter(([, status]) => status !== "ok")
    .map(([name]) => name);
  if (payload.status === "ok" && failing.length === 0) {
    return { tone: "ok", label: "All systems operational", failing };
  }
  return { tone: "degraded", label: "Degraded", failing };
}
