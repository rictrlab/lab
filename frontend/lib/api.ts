export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export type ProblemSummary = {
  slug: string;
  title: string;
  difficulty: string;
  category: string;
  // optional fields if backend returns them
  tags?: string[];
};

export type ProblemDetail = {
  slug: string;
  title: string;
  difficulty: string;
  category: string;
  prompt_md: string;
  starter_code: string;
  function_signature?: string;
  examples?: Array<{ input: string; output: string; explanation?: string } | string>;
  // fallback raw
  description?: string;
  signature?: string;
};

export type SubmitResult = {
  passed: number;
  total: number;
  results: Array<{
    name?: string;
    passed: boolean;
    input?: string;
    expected?: string;
    actual?: string;
    error?: string | null;
    stdout?: string | null;
    latency_ms?: number;
  }>;
  stdout?: string | null;
  error?: string | null;
  latency_ms?: number;
  // alternative shapes
  status?: string;
  message?: string;
};

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Request failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export async function fetchProblems(): Promise<ProblemSummary[]> {
  const res = await fetch(`${API_BASE}/api/problems`, {
    cache: "no-store",
  });
  const data = await handleResponse<any>(res);
  // Normalize: backend may return array or {problems: []}
  if (Array.isArray(data)) return data as ProblemSummary[];
  if (Array.isArray(data.problems)) return data.problems as ProblemSummary[];
  if (Array.isArray(data.data)) return data.data as ProblemSummary[];
  return [];
}

export async function fetchProblem(slug: string): Promise<ProblemDetail> {
  const res = await fetch(`${API_BASE}/api/problems/${encodeURIComponent(slug)}`, {
    cache: "no-store",
  });
  return handleResponse<ProblemDetail>(res);
}

export async function submitCode(
  slug: string,
  code: string
): Promise<SubmitResult> {
  const res = await fetch(`${API_BASE}/api/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ slug, code }),
  });
  return handleResponse<SubmitResult>(res);
}

// client-side helper with timeout
export async function fetchWithTimeout(
  input: RequestInfo | URL,
  init?: RequestInit,
  timeoutMs = 6000
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(input, { ...init, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(id);
  }
}
