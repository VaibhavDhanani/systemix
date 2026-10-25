"use client";

import { useEffect, useState } from "react";

import { type HealthPayload, summarizeHealth } from "@/lib/health";

const toneStyles = {
  ok: "bg-success-soft text-success",
  degraded: "bg-warning-soft text-warning",
  down: "bg-danger-soft text-danger",
} as const;

export function ApiStatus() {
  const [payload, setPayload] = useState<HealthPayload | null | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/health", { cache: "no-store" })
      .then((res) => res.json() as Promise<HealthPayload>)
      .catch(() => null)
      .then((data) => {
        if (!cancelled) setPayload(data);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (payload === undefined) {
    return <p className="text-muted">Checking the API…</p>;
  }

  const summary = summarizeHealth(payload);
  return (
    <div className="flex flex-col gap-4">
      <span
        className={`self-start rounded-full px-3 py-1 text-sm font-semibold ${toneStyles[summary.tone]}`}
      >
        {summary.label}
      </span>
      {payload && (
        <ul className="flex flex-col gap-2">
          {Object.entries(payload.checks).map(([name, status]) => (
            <li
              key={name}
              className="flex justify-between rounded-control border border-line px-4 py-3"
            >
              <span className="font-medium capitalize">{name}</span>
              <span className="font-mono text-sm text-muted">{status}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
