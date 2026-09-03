import type { Metadata } from "next";
import "./globals.css";
import ThemeToggle from "../components/ThemeToggle";

export const metadata: Metadata = {
  title: "rictrlab",
  description: "rictrlab",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('theme');var d=t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme: dark)').matches);if(d)document.documentElement.classList.add('dark')}catch(e){}})();`,
          }}
        />
      </head>
      <body className="h-screen overflow-hidden flex flex-col bg-[#fafafa] text-zinc-900 antialiased" style={{ fontFamily: "'Manrope', sans-serif" }}>
        <header className="sticky top-0 z-40 w-full bg-transparent">
          <div className="mx-auto flex h-12 max-w-[1600px] items-center justify-between px-4 sm:px-6 lg:px-8">
            <a href="/" className="flex items-center gap-2.5">
              <span className="text-lg tracking-tight text-black">
                <span className="font-extrabold">rictr</span>
                <span className="font-light">lab</span>
              </span>
            </a>
            <ThemeToggle />
          </div>
        </header>
        <main className="mx-auto max-w-[1600px] w-full flex-1 px-4 sm:px-6 lg:px-8 py-4 overflow-hidden flex flex-col">
          {children}
        </main>
        <footer className="mt-auto bg-transparent border-none">
          <div className="mx-auto max-w-[1600px] px-4 sm:px-6 lg:px-8 py-6 flex items-center justify-center text-xs text-zinc-500">
            <span>© 2026 rictrlab</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
