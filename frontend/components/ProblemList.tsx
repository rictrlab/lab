"use client";

import Link from "next/link";
import { ProblemSummary } from "../lib/api";

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const d = (difficulty || "").toLowerCase();
  let classes = "bg-zinc-800 text-zinc-300 border-zinc-700";
  if (d === "easy") classes = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
  else if (d === "medium") classes = "bg-amber-500/10 text-amber-400 border-amber-500/20";
  else if (d === "hard") classes = "bg-red-500/10 text-red-400 border-red-500/20";
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize ${classes}`}>
      {difficulty}
    </span>
  );
}

export default function ProblemList({ problems }: { problems: ProblemSummary[] }) {
  if (!problems.length) {
    return (
      <div className="rounded-2xl border border-zinc-800 bg-[#18181b] p-10 text-center">
        <p className="text-zinc-400 text-sm">No problems found.</p>
      </div>
    );
  }
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {problems.map((p) => (
        <Link
          key={p.slug}
          href={`/problems/${encodeURIComponent(p.slug)}`}
          className="group relative flex flex-col rounded-2xl border border-zinc-800 bg-[#18181b] p-5 hover:border-zinc-700 hover:bg-[#1e1e21] transition-colors"
        >
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-orange-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
          <div className="relative">
            <div className="flex items-start justify-between gap-3 mb-3">
              <h3 className="font-semibold text-white leading-tight line-clamp-2 group-hover:text-orange-100 transition-colors">
                {p.title}
              </h3>
              <DifficultyBadge difficulty={p.difficulty} />
            </div>
            <div className="flex items-center gap-2 text-xs text-zinc-500 mb-4">
              <span className="inline-flex items-center rounded-full bg-zinc-900 border border-zinc-800 px-2 py-0.5">
                {p.category || "General"}
              </span>
              <span className="truncate font-mono text-[11px] text-zinc-600">{p.slug}</span>
            </div>
            <div className="flex items-center justify-between mt-auto pt-2 border-t border-zinc-800/60">
              <span className="text-xs font-medium text-zinc-400 group-hover:text-zinc-200 flex items-center gap-1">
                Solve
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="group-hover:translate-x-0.5 transition-transform">
                  <path d="M5 12h14" />
                  <path d="M12 5l7 7-7 7" />
                </svg>
              </span>
              <span className="text-[11px] text-zinc-600">PyTorch · CPU</span>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
