import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-1 flex-col justify-center">
      <section className="flex flex-1 flex-col items-center justify-center text-center py-8 sm:py-12 min-h-[calc(100vh-10rem)]">
        <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight text-black leading-[1.05]">
          Master PyTorch
          <br />
          without bounds
        </h1>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/problems"
            className="inline-flex items-center gap-2 rounded-full bg-black px-6 py-3 text-sm font-semibold text-white hover:bg-zinc-800 transition"
          >
            Explore Problems
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14" />
              <path d="M12 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </section>
    </div>
  );
}
