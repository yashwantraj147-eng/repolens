import React, { useState } from 'react';
import { ArrowRightLeft, Sparkles, Scale, Search, Loader2 } from 'lucide-react';

const PRESETS = [
  { label: 'FastAPI vs Flask', a: 'fastapi/fastapi', b: 'pallets/flask' },
  { label: 'Express vs Fastify', a: 'expressjs/express', b: 'fastify/fastify' },
  { label: 'Vite vs Webpack', a: 'vitejs/vite', b: 'webpack/webpack' },
  { label: 'Next.js vs Remix', a: 'vercel/next.js', b: 'remix-run/remix' },
];

export function CompareInput({ onCompare, loading }) {
  const [repoA, setRepoA] = useState('');
  const [repoB, setRepoB] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!repoA.trim() || !repoB.trim()) {
      setError('Please provide two repositories to compare.');
      return;
    }
    setError('');
    onCompare(repoA.trim(), repoB.trim());
  };

  const handleSwap = () => {
    const temp = repoA;
    setRepoA(repoB);
    setRepoB(temp);
  };

  const handleSelectPreset = (preset) => {
    setRepoA(preset.a);
    setRepoB(preset.b);
    setError('');
    onCompare(preset.a, preset.b);
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      <form
        onSubmit={handleSubmit}
        className="rounded-3xl border border-slate-200/90 dark:border-slate-800/90 bg-white dark:bg-slate-900/90 p-4 sm:p-5 shadow-lg shadow-indigo-500/5 backdrop-blur-md"
      >
        <div className="flex flex-col md:flex-row items-center gap-3">
          {/* Repo A Input */}
          <div className="relative flex-1 w-full">
            <input
              type="text"
              value={repoA}
              onChange={(e) => {
                setRepoA(e.target.value);
                if (error) setError('');
              }}
              placeholder="e.g. fastapi/fastapi"
              disabled={loading}
              className="w-full py-3.5 pl-4 pr-4 rounded-2xl bg-slate-50 dark:bg-slate-950/70 border border-slate-200 dark:border-slate-800 text-sm font-medium text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
            />
            <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 border border-indigo-200/60 dark:border-indigo-800/60">
              REPO A
            </span>
          </div>

          {/* Swap Button */}
          <button
            type="button"
            onClick={handleSwap}
            disabled={loading}
            className="p-2.5 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-50 dark:hover:bg-slate-800/80 transition-colors shadow-2xs shrink-0"
            title="Swap repositories"
          >
            <ArrowRightLeft className="w-4 h-4" />
          </button>

          {/* Repo B Input */}
          <div className="relative flex-1 w-full">
            <input
              type="text"
              value={repoB}
              onChange={(e) => {
                setRepoB(e.target.value);
                if (error) setError('');
              }}
              placeholder="e.g. pallets/flask"
              disabled={loading}
              className="w-full py-3.5 pl-4 pr-4 rounded-2xl bg-slate-50 dark:bg-slate-950/70 border border-slate-200 dark:border-slate-800 text-sm font-medium text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
            />
            <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-50 dark:bg-purple-950/80 text-purple-600 dark:text-purple-400 border border-purple-200/60 dark:border-purple-800/60">
              REPO B
            </span>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full md:w-auto px-6 py-3.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold shadow-md shadow-indigo-500/25 transition-all flex items-center justify-center gap-2 shrink-0 cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Comparing...</span>
              </>
            ) : (
              <>
                <Scale className="w-4 h-4" />
                <span>Compare</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <p className="text-xs text-rose-500 dark:text-rose-400 mt-3 text-left pl-1">
            {error}
          </p>
        )}
      </form>

      {/* Preset Comparison Quick-Picks */}
      <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
        <span className="text-xs font-semibold text-slate-400 dark:text-slate-500 mr-1 flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
          <span>Popular Matchups:</span>
        </span>
        {PRESETS.map((p) => (
          <button
            key={p.label}
            type="button"
            onClick={() => handleSelectPreset(p)}
            disabled={loading}
            className="px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 hover:bg-indigo-50 dark:hover:bg-slate-800 hover:border-indigo-300 dark:hover:border-indigo-700 text-xs font-semibold text-slate-700 dark:text-slate-300 transition-all shadow-2xs cursor-pointer"
          >
            {p.label}
          </button>
        ))}
      </div>
    </div>
  );
}
