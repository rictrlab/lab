"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

type EditorProps = {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  height?: string;
};

function Fallback({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="h-[500px] w-full resize-none border border-zinc-200 bg-white p-4 font-mono text-sm text-zinc-900 outline-none focus:border-black dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700"
      spellCheck={false}
    />
  );
}

const MonacoEditor = dynamic(() => import("@monaco-editor/react").then((mod) => mod.default), {
  ssr: false,
  loading: () => (
    <div className="h-[500px] w-full animate-pulse bg-zinc-50 border border-zinc-200" />
  ),
});

export default function Editor({ value, onChange, language = "python", height = "500px" }: EditorProps) {
  const [theme, setTheme] = useState("vs");

  useEffect(() => {
    const check = () => {
      const isDark = document.documentElement.classList.contains("dark");
      setTheme(isDark ? "vs-dark" : "vs");
    };
    check();
    const observer = new MutationObserver(check);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    window.addEventListener("storage", check);
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    media.addEventListener("change", check);
    return () => {
      observer.disconnect();
      window.removeEventListener("storage", check);
      media.removeEventListener("change", check);
    };
  }, []);

  return (
    <div className="overflow-hidden border border-zinc-200 bg-white dark:border-zinc-700 dark:bg-zinc-900">
      <MonacoEditor
        height={height}
        language={language}
        value={value}
        onChange={(v: string | undefined) => onChange(v ?? "")}
        theme={theme}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "JetBrains Mono, Menlo, Monaco, Consolas, monospace",
          scrollBeyondLastLine: false,
          wordWrap: "on",
          padding: { top: 12, bottom: 12 },
          automaticLayout: true,
          tabSize: 4,
          lineNumbers: "on",
          glyphMargin: false,
          folding: true,
          bracketPairColorization: { enabled: true },
        }}
        loading={<Fallback value={value} onChange={onChange} />}
      />
    </div>
  );
}
