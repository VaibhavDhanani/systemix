import type { Metadata } from "next";

import { ApiStatus } from "./api-status";

export const metadata: Metadata = { title: "Status · Systemix" };

export default function StatusPage() {
  return (
    <main className="mx-auto flex w-full max-w-xl flex-col gap-6 px-6 py-16">
      <h1 className="text-3xl font-bold tracking-tight">System status</h1>
      <p className="text-muted">
        Live result of <code className="font-mono text-sm">GET /api/health</code>, proxied from
        Next.js to the FastAPI backend.
      </p>
      <ApiStatus />
    </main>
  );
}
