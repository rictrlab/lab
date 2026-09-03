"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchProblems, ProblemSummary } from "../../lib/api";

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  return (
    <span className="text-xs font-medium text-zinc-500 capitalize">
      {difficulty || "Unknown"}
    </span>
  );
}

function SkeletonCard() {
  return (
    <div className="animate-pulse border border-zinc-200 bg-white px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3 flex-1">
        <div className="h-4 w-32 bg-zinc-200" />
        <div className="h-4 w-20 bg-zinc-100 border border-zinc-200" />
      </div>
      <div className="h-3 w-12 bg-zinc-200" />
    </div>
  );
}

export default function ProblemsPage() {
  const [problems, setProblems] = useState<ProblemSummary[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProblems();
      setProblems(data);
    } catch (e: any) {
      setError(e?.message || "Failed to fetch problems");
      setProblems(null);
    } finally {
      setLoading(false);
    }
  };

  const tags = Array.from(new Set((problems || []).map((p) => p.category || "General"))).sort();
  const filtered = selectedTag ? (problems || []).filter((p) => (p.category || "General") === selectedTag) : problems;

  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [retryCount]);

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] gap-4">
      <div className="flex flex-wrap items-center justify-between gap-4 shrink-0">
        <h1 className="text-sm font-normal text-zinc-400">
          {problems ? `${problems.length} challenge${problems.length !== 1 ? "s" : ""}` : ""}
        </h1>
      </div>

      {loading && !problems && (
        <div className="border border-zinc-200 bg-white p-4 flex-1 min-h-0">
          <div className="flex flex-col gap-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        </div>
      )}

      {error && !loading && (
        <div className="border border-red-200 bg-red-50/60 p-6 text-center">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-red-100 border-red-200 mb-3">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="1.8">
              <path d="M12 9v4" />
              <path d="M12 17h.01" />
              <path d="M10.3 3.3 3.1 15a2 2 0 0 0 1.7 3h14.4a2 2 0 0 0 1.7-3L13.7 3.3a2 2 0 0 0-3.4 0z" />
            </svg>
          </div>
          <h3 className="text-sm font-semibold text-red-700">Backend offline</h3>
          <p className="mt-1 text-sm text-zinc-600 max-w-md mx-auto">
            Could not reach backend. Please try again.
          </p>
          <p className="mt-2 text-xs text-zinc-500 font-mono break-all">{error}</p>
          <button
            onClick={() => setRetryCount((c) => c + 1)}
            className="mt-4 inline-flex items-center justify-center rounded-none bg-black px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800 transition"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && problems && problems.length === 0 && (
        <div className="border border-zinc-200 bg-white p-10 text-center">
          <p className="text-zinc-500 text-sm">No problems found. Check back soon.</p>
        </div>
      )}

      {!loading && problems && problems.length > 0 && (
        <>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedTag(null)}
              className={`rounded-none border px-3 py-1.5 text-xs font-medium transition ${!selectedTag ? "bg-black text-white border-black" : "bg-white text-zinc-600 border-zinc-200 hover:border-black hover:bg-zinc-50"}`}
            >
              All
            </button>
            {tags.map((tag) => (
              <button
                key={tag}
                onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
                className={`rounded-none border px-3 py-1.5 text-xs font-medium transition ${selectedTag === tag ? "bg-black text-white border-black" : "bg-white text-zinc-600 border-zinc-200 hover:border-black hover:bg-zinc-50"}`}
              >
                {tag}
              </button>
            ))}
          </div>

          <div className="border border-zinc-200 bg-white p-4 flex-1 min-h-0 flex flex-col">
            <div className="flex-1 overflow-y-auto pr-1 -mr-1 flex flex-col gap-2 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
              {filtered && filtered.length > 0 ? (
                filtered.map((p) => (
                  <Link
                    key={p.slug}
                    href={`/problems/${encodeURIComponent(p.slug)}`}
                    className="group flex items-center justify-between border border-zinc-200 bg-white px-4 py-3 hover:border-black hover:shadow-sm transition-all"
                  >
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <h3 className="font-semibold text-sm text-black truncate">
                        {p.title}
                      </h3>
                      <span className="hidden sm:inline-flex items-center border border-zinc-200 bg-zinc-50 px-2 py-0.5 text-[11px] font-medium text-zinc-600 shrink-0">
                        {p.category || "General"}
                      </span>
                    </div>
                    <span className="text-xs font-semibold text-zinc-500 group-hover:text-black flex items-center gap-1.5 shrink-0 ml-4">
                      Solve
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="group-hover:translate-x-0.5 transition-transform">
                        <path d="M5 12h14" />
                        <path d="M12 5l7 7-7 7" />
                      </svg>
                    </span>
                  </Link>
                ))
              ) : (
                <p className="text-sm text-zinc-500 text-center py-8">No problems for this tag.</p>
              )}
            </div>
          </div>
        </>
      )}


    </div>
  );
}
