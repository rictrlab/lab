"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import Editor from "../../../components/Editor";
import { fetchProblem, submitCode, ProblemDetail, SubmitResult } from "../../../lib/api";
import Link from "next/link";

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  return (
    <span className="text-xs font-medium text-zinc-500 capitalize">
      {difficulty || "Unknown"}
    </span>
  );
}

export default function ProblemPage() {
  const params = useParams<{ slug: string }>();
  const slug = Array.isArray(params.slug) ? params.slug[0] : params.slug;
  const router = useRouter();

  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [code, setCode] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<SubmitResult | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Lock outer scroll on problem page — only inner panes scroll
  useEffect(() => {
    const prevHtmlOverflow = document.documentElement.style.overflow;
    const prevBodyOverflow = document.body.style.overflow;
    document.documentElement.style.overflow = "hidden";
    document.body.style.overflow = "hidden";
    return () => {
      document.documentElement.style.overflow = prevHtmlOverflow;
      document.body.style.overflow = prevBodyOverflow;
    };
  }, []);

  useEffect(() => {
    if (!slug) return;
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchProblem(slug);
        if (cancelled) return;
        setProblem(data);
        const starter =
          (data as any).starter_code ??
          (data as any).starterCode ??
          (data as any).code ??
          "";
        setCode(starter);
      } catch (e: any) {
        if (cancelled) return;
        setError(e?.message || "Failed to load problem");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [slug]);

  const handleSubmit = async () => {
    if (!slug || !code) return;
    setSubmitting(true);
    setSubmitError(null);
    setResult(null);
    try {
      const res = await submitCode(slug, code);
      setResult(res);
    } catch (e: any) {
      setSubmitError(e?.message || "Submit failed");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    if (problem) {
      const starter =
        (problem as any).starter_code ??
        (problem as any).starterCode ??
        (problem as any).code ??
        "";
      setCode(starter);
      setResult(null);
      setSubmitError(null);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 w-1/3 bg-zinc-200 rounded" />
        <div className="grid lg:grid-cols-[45%_55%] gap-6">
          <div className="space-y-4">
            <div className="h-64 bg-zinc-100 border border-zinc-200" />
          </div>
          <div className="h-[500px] bg-zinc-100 border border-zinc-200" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Link href="/problems" className="inline-flex items-center gap-1.5 text-sm text-zinc-500 hover:text-black">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
          Back to problems
        </Link>
        <div className="border border-red-200 bg-red-50/60 p-8 text-center">
          <h3 className="text-sm font-semibold text-red-700">Failed to load problem</h3>
          <p className="mt-2 text-sm text-zinc-600">
            Slug: <code className="text-black">{slug}</code>
          </p>
          <p className="mt-1 text-xs font-mono text-zinc-500 break-all">{error}</p>
          <p className="mt-2 text-xs text-zinc-500">Is backend running at http://localhost:8000 ?</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 inline-flex rounded-none bg-black px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!problem) return null;

  const promptMd = (problem as any).prompt_md ?? (problem as any).prompt ?? (problem as any).description ?? "";

  // Parse examples from promptMd: look for ```python blocks with >>> solve(...)
  function parseExamples(md: string) {
    const blocks: { input: string; output: string }[] = [];
    const codeBlockRe = /```(?:python)?\s*\n([\s\S]*?)```/g;
    let m;
    while ((m = codeBlockRe.exec(md)) !== null) {
      const body = m[1];
      if (!body.includes(">>>")) continue;
      const lines = body.split("\n");
      let currentInput = "";
      let currentOutput = "";
      for (const line of lines) {
        const trimmed = line.replace(/^>>> /, "").trim();
        if (!trimmed || trimmed.startsWith("#")) continue;
        if (trimmed === "import torch" || trimmed.startsWith("import ") || trimmed.startsWith("from ")) continue;
        if (line.startsWith(">>> ")) {
          if (currentOutput) {
            blocks.push({ input: currentInput, output: currentOutput });
            currentInput = "";
            currentOutput = "";
          }
          currentInput = currentInput ? currentInput + "\n" + trimmed : trimmed;
        } else {
          currentOutput = currentOutput ? currentOutput + "\n" + line.trim() : line.trim();
        }
      }
      if (currentInput && currentOutput) {
        blocks.push({ input: currentInput, output: currentOutput });
      }
    }
    return blocks;
  }
  function parseConstraints(md: string): string[] {
    const m = md.match(/##\s*Constraints\s*\n([\s\S]*?)(?=\n##\s|\n*$)/i);
    if (!m) return [];
    return m[1]
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.startsWith("-"))
      .map((l) => l.replace(/^-\s*/, "").trim())
      .filter(Boolean);
  }
  function parseNotes(md: string): string[] {
    const notes: string[] = [];
    const pushSection = (heading: string) => {
      const re = new RegExp(`##\\s*${heading}\\s*\\n([\\s\\S]*?)(?=\\n##\\s|\\n*$)`, "i");
      const mm = md.match(re);
      if (!mm) return;
      mm[1]
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean)
        .forEach((l) => {
          if (l.startsWith("-")) notes.push(l.replace(/^-\s*/, "").trim());
          else if (!l.startsWith("```") && !l.startsWith(">>>")) notes.push(l);
        });
    };
    pushSection("Note");
    pushSection("Hints");
    return notes;
  }
  function getCleanDescription(md: string): string {
    let cleaned = md;
    cleaned = cleaned.replace(/```[\s\S]*?```/g, "");
    cleaned = cleaned.replace(/##\s*Constraints[\s\S]*?(?=\n##\s|\n*$)/gi, "");
    cleaned = cleaned.replace(/##\s*Hints[\s\S]*?(?=\n##\s|\n*$)/gi, "");
    cleaned = cleaned.replace(/##\s*Note[\s\S]*?(?=\n##\s|\n*$)/gi, "");
    // Remove Input/Output bullet blocks (in case markdown not yet cleaned)
    cleaned = cleaned.replace(/^- \*\*Input\*\*.*$/gm, "");
    cleaned = cleaned.replace(/^- \*\*Output\*\*.*$/gm, "");
    cleaned = cleaned.replace(/^\s{2,}- `.*$/gm, "");
    cleaned = cleaned.replace(/\n{3,}/g, "\n\n").trim();
    return cleaned;
  }
  const parsedExamples = parseExamples(promptMd);
  const parsedConstraints = parseConstraints(promptMd);
  const parsedNotes = parseNotes(promptMd);
  const cleanDescription = getCleanDescription(promptMd);

  return (
    <div className="flex flex-col w-full lg:h-[calc(100vh-8rem)] gap-4 lg:overflow-hidden">
      {/* Top bar */}
      <div className="flex flex-col gap-3 shrink-0">
        <Link href="/problems" className="inline-flex items-center gap-1.5 text-sm text-zinc-500 hover:text-black w-fit">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
          All problems
        </Link>

        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-black">{problem.title}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
              <DifficultyBadge difficulty={problem.difficulty} />
              <span className="text-xs text-zinc-500">{problem.category || "General"}</span>
              <span className="font-mono text-zinc-400">/{problem.slug}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReset}
              className="rounded-none border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100"
            >
              Reset
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="inline-flex items-center gap-2 rounded-none bg-black px-4 py-1.5 text-sm font-semibold text-white hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {submitting && (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {submitting ? "Submitting..." : "Submit"}
            </button>
          </div>
        </div>
      </div>

      {/* Main split — expanded full page */}
      <div className="grid gap-4 lg:grid-cols-[46%_54%] flex-1 min-h-0 items-stretch lg:overflow-hidden">
        {/* Left: description — spacious, scrollable, full height */}
        <div className="flex flex-col border border-zinc-200 bg-white p-6 sm:p-8 lg:overflow-auto lg:min-h-0 space-y-5 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
          {cleanDescription ? (
            <div className="prose prose-zinc prose-base max-w-none prose-p:leading-relaxed prose-headings:font-bold prose-headings:tracking-tight
              prose-pre:!bg-transparent prose-pre:!p-0 prose-pre:!m-0 prose-pre:!border-0
              prose-code:before:content-none prose-code:after:content-none
              [&_.katex-display]:!bg-white [&_.katex-display]:!border [&_.katex-display]:!border-zinc-200 [&_.katex-display]:!p-4 [&_.katex-display]:!my-4
              [&>p:first-of-type]:font-bold [&>p:first-of-type]:italic [&>p:first-of-type]:text-black">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
                components={{
                  pre: () => null,
                  code: ({ inline, className, children, ...props }: any) => {
                    if (inline) {
                      return (
                        <code className="bg-zinc-100 border border-zinc-200 px-1 py-0.5 text-xs font-mono" {...props}>
                          {children}
                        </code>
                      );
                    }
                    return null;
                  },
                  h2: ({ children }: any) => {
                    const t = String(children).toLowerCase();
                    if (t.includes("constraint") || t.includes("hint") || t.includes("note")) return null;
                    return <h2 className="text-base font-bold text-black mt-6 mb-2">{children}</h2>;
                  },
                  h3: ({ children }: any) => {
                    const t = String(children).toLowerCase();
                    if (t.includes("constraint") || t.includes("hint") || t.includes("note")) return null;
                    return <h3 className="text-sm font-bold text-black mt-4 mb-1">{children}</h3>;
                  },
                  p: ({ children }: any) => <p className="text-sm leading-relaxed text-zinc-700 my-2">{children}</p>,
                  ul: ({ children }: any) => <ul className="list-disc list-inside text-sm text-zinc-600 space-y-1.5 my-3">{children}</ul>,
                  ol: ({ children }: any) => <ol className="list-decimal list-inside text-sm text-zinc-600 space-y-1.5 my-3">{children}</ol>,
                  li: ({ children }: any) => <li className="text-sm text-zinc-600">{children}</li>,
                  strong: ({ children }: any) => <strong className="font-bold text-black">{children}</strong>,
                  em: ({ children }: any) => <em className="italic">{children}</em>,
                }}
              >
                {cleanDescription}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="text-sm text-zinc-500">No description available.</p>
          )}

          {parsedExamples.length > 0 && (
            <div className="space-y-3">
              {parsedExamples.map((ex, i) => (
                <div key={i} className="border border-zinc-200 bg-white">
                  <div className="px-4 py-2 border-b border-zinc-100 bg-zinc-50">
                    <span className="text-[10px] font-bold tracking-widest text-zinc-400 uppercase">Example {i + 1}</span>
                  </div>
                  <div className="divide-y divide-zinc-100">
                    <div className="px-4 py-3">
                      <div className="text-[10px] font-bold tracking-widest text-zinc-400 uppercase mb-1">Input</div>
                      <pre className="text-sm font-mono text-zinc-700 whitespace-pre-wrap break-all">{ex.input}</pre>
                    </div>
                    <div className="px-4 py-3">
                      <div className="text-[10px] font-bold tracking-widest text-zinc-400 uppercase mb-1">Output</div>
                      <pre className="text-sm font-mono text-emerald-700 whitespace-pre-wrap break-all">{ex.output}</pre>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {parsedNotes.length > 0 && (
            <div className="pt-4">
              <h4 className="text-sm font-bold text-black mb-2">Note</h4>
              <ul className="list-disc list-inside text-sm text-zinc-500 space-y-1.5">
                {parsedNotes.map((n, idx) => (
                  <li key={idx}>{n}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="pt-5 border-t border-zinc-200 mt-auto">
            <h4 className="text-sm font-bold text-black mb-2">Constraints</h4>
            <ul className="list-disc list-inside text-sm text-zinc-500 space-y-1.5">
              {parsedConstraints.length > 0 ? (
                parsedConstraints.map((c, idx) => <li key={idx}>{c}</li>)
              ) : (
                <li>Function signature must match exactly</li>
              )}
            </ul>
          </div>
        </div>

        {/* Right: editor — big sandbox, full height */}
        <div className="flex flex-col min-h-0 gap-4 lg:overflow-auto [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
          <div className="flex flex-col flex-1 border border-zinc-200 bg-white p-3 min-h-[680px]">
            <Editor value={code} onChange={setCode} language="python" height="680px" />
            <div className="flex flex-wrap items-center gap-2 pt-3 px-1 shrink-0">
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="inline-flex items-center gap-2 rounded-none bg-black px-5 py-2 text-sm font-semibold text-white hover:bg-zinc-800 disabled:opacity-50 transition"
              >
                {submitting ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Running...
                  </>
                ) : (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M5 3l14 9-14 9V3z" />
                    </svg>
                    Run
                  </>
                )}
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="inline-flex items-center gap-2 rounded-none bg-white border border-zinc-200 px-5 py-2 text-sm font-semibold text-black hover:bg-zinc-100 disabled:opacity-50 transition"
              >
                Submit
              </button>
            </div>
          </div>

          {/* Results */}
          {(result || submitError || submitting) && (
            <div className="border border-zinc-200 bg-white p-4 sm:p-5">
              <h3 className="text-sm font-bold text-black mb-3 flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-black" />
                Results
              </h3>

              {submitting && (
                <div className="flex items-center gap-3 text-sm text-zinc-500 py-6 justify-center">
                  <svg className="animate-spin h-5 w-5 text-black" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Judging your solution...
                </div>
              )}

              {submitError && !submitting && (
                <div className="border border-red-200 bg-red-50/60 p-4">
                  <p className="text-sm font-medium text-red-700">Submission failed</p>
                  <p className="mt-1 text-xs font-mono text-zinc-600 break-all">{submitError}</p>
                  <p className="mt-2 text-xs text-zinc-500">Check backend at http://localhost:8000/api/submit</p>
                </div>
              )}

              {result && !submitting && (
                <div className="space-y-4">
                  {/* Summary */}
                  <div className="flex flex-wrap items-center gap-3">
                    <span
                      className={`inline-flex items-center px-3 py-1 text-xs font-bold border ${
                        result.passed === result.total
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : "bg-red-50 text-red-700 border-red-200"
                      }`}
                    >
                      {result.passed}/{result.total} passed
                    </span>
                    {typeof result.latency_ms === "number" && (
                      <span className="text-xs text-zinc-500 font-mono">{result.latency_ms}ms</span>
                    )}
                    {result.status && (
                      <span className="text-xs text-zinc-500 capitalize">{result.status}</span>
                    )}
                  </div>

                  {(result.stdout || result.error) && (
                    <div className="grid gap-2">
                      {result.stdout && (
                        <div className="rounded-none border border-zinc-200 bg-zinc-50 p-3">
                          <div className="text-[11px] font-bold tracking-widest text-zinc-400 uppercase mb-1">Stdout</div>
                          <pre className="text-xs font-mono text-zinc-700 whitespace-pre-wrap break-all">{result.stdout}</pre>
                        </div>
                      )}
                      {result.error && (
                        <div className="rounded-none border border-red-200 bg-red-50/60 p-3">
                          <div className="text-[11px] font-bold tracking-widest text-red-500 uppercase mb-1">Error</div>
                          <pre className="text-xs font-mono text-red-700 whitespace-pre-wrap break-all">{result.error}</pre>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Per test */}
                  {Array.isArray(result.results) && result.results.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Test Cases</div>
                      {result.results.map((t: any, i: number) => (
                        <div
                          key={i}
                          className={`rounded-none border p-3 flex flex-col gap-1 ${
                            t.passed
                              ? "border-emerald-200 bg-emerald-50/50"
                              : "border-red-200 bg-red-50/50"
                          }`}
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${t.passed ? "text-emerald-700" : "text-red-700"}`}>
                              <span className={`h-2 w-2 rounded-full ${t.passed ? "bg-emerald-500" : "bg-red-500"}`} />
                              {t.name || `Test ${i + 1}`} — {t.passed ? "Passed" : "Failed"}
                            </span>
                            {typeof t.latency_ms === "number" && (
                              <span className="text-[11px] font-mono text-zinc-400">{t.latency_ms}ms</span>
                            )}
                          </div>
                          {(t.input || t.expected || t.actual) && (
                            <div className="mt-1 grid gap-1 text-xs font-mono">
                              {t.input && <div className="text-zinc-500"><span className="text-zinc-400">input:</span> <span className="text-zinc-700 break-all">{String(t.input)}</span></div>}
                              {t.expected !== undefined && <div className="text-zinc-500"><span className="text-zinc-400">expected:</span> <span className="text-emerald-700 break-all">{String(t.expected)}</span></div>}
                              {t.actual !== undefined && <div className="text-zinc-500"><span className="text-zinc-400">actual:</span> <span className={t.passed ? "text-emerald-700" : "text-red-700"}>{String(t.actual)}</span></div>}
                            </div>
                          )}
                          {t.error && <pre className="mt-1 text-xs font-mono text-red-700 whitespace-pre-wrap break-all">{t.error}</pre>}
                          {t.stdout && <pre className="mt-1 text-xs font-mono text-zinc-500 whitespace-pre-wrap break-all">{t.stdout}</pre>}
                        </div>
                      ))}
                    </div>
                  )}

                  {result.message && <p className="text-xs text-zinc-500">{result.message}</p>}
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
