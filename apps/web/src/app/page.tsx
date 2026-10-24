import Link from "next/link";

// Placeholder until Phase 1 builds the real landing page.
export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center gap-6 px-6 py-24">
      <span className="self-start rounded-full bg-brand-soft px-3 py-1 text-sm font-semibold text-brand-strong">
        Phase 0 · Foundation
      </span>
      <h1 className="text-5xl font-extrabold tracking-tight">Systemix</h1>
      <p className="max-w-xl text-lg leading-relaxed text-muted">
        Learn system design the way interviewers think. The landing page arrives in Phase 1.
      </p>
      <Link
        href="/status"
        className="self-start rounded-control bg-brand px-5 py-3 font-semibold text-white hover:bg-brand-strong"
      >
        Check system status
      </Link>
    </main>
  );
}
