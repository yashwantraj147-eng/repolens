import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { RepoInput } from './components/RepoInput';
import { ReportPage } from './components/ReportPage';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorAlert } from './components/ErrorAlert';
import { useAnalyze } from './hooks/useAnalyze';
import {
  GitFork,
  Sparkles,
  GitGraph,
  ShieldCheck,
  BookOpen,
  ArrowUpRight,
  Terminal,
} from 'lucide-react';

export function App() {
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('repolens_theme');
      if (saved) return saved === 'dark';
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  const { report, loading, error, analyze, loadReport, reset } = useAnalyze();

  // Sync dark class on document root
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('repolens_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('repolens_theme', 'light');
    }
  }, [darkMode]);

  // Load report from URL query parameter if present
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const reportId = params.get('report_id');
      if (reportId && !report) {
        loadReport(reportId).catch(() => {
          // If loading fails, clear param and return to input
          window.history.replaceState({}, '', window.location.pathname);
        });
      }
    }
  }, [loadReport]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 selection:bg-indigo-500 selection:text-white">
      <Header darkMode={darkMode} setDarkMode={setDarkMode} onReset={reset} />

      <main className="flex-1 pb-16">
        {loading && <LoadingSpinner />}

        {error && !loading && (
          <div className="max-w-3xl mx-auto px-4 mt-8">
            <ErrorAlert message={error} onRetry={() => reset()} />
          </div>
        )}

        {!loading && report ? (
          <ReportPage report={report} onReset={reset} darkMode={darkMode} />
        ) : !loading && !error ? (
          /* Landing / Hero State */
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 sm:pt-24 text-center">
            {/* Pill */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-indigo-200 dark:border-indigo-800/80 bg-indigo-50/70 dark:bg-indigo-950/50 text-xs font-semibold text-indigo-700 dark:text-indigo-300 mb-8 backdrop-blur-sm shadow-xs animate-bounce">
              <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
              <span>Full-Stack Repository Intelligence</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-slate-950 dark:text-white max-w-4xl mx-auto leading-[1.15]">
              Instant architecture diagrams & health scores for{' '}
              <span className="bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-500 bg-clip-text text-transparent">
                any GitHub repository
              </span>
            </h1>

            <p className="mt-6 text-base sm:text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
              Drop any public repository link to generate a plain-English explanation, interactive Mermaid system diagram, step-by-step onboarding guide, and a 0–100 health audit.
            </p>

            {/* Input Bar */}
            <div className="mt-10 mb-16">
              <RepoInput onAnalyze={analyze} loading={loading} />
            </div>

            {/* Feature Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 text-left pt-6">
              <div className="p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/60 backdrop-blur-sm shadow-xs hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors">
                <div className="w-10 h-10 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4">
                  <GitGraph className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-1.5">
                  Mermaid Diagrams
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Automatic component, service, and routing graph rendered right in the browser.
                </p>
              </div>

              <div className="p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/60 backdrop-blur-sm shadow-xs hover:border-emerald-300 dark:hover:border-emerald-700 transition-colors">
                <div className="w-10 h-10 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-4">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-1.5">
                  7-Point Health Score
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Weighted evaluation of tests, README quality, issue response, license, and CI/CD.
                </p>
              </div>

              <div className="p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/60 backdrop-blur-sm shadow-xs hover:border-violet-300 dark:hover:border-violet-700 transition-colors">
                <div className="w-10 h-10 rounded-2xl bg-violet-50 dark:bg-violet-950/60 text-violet-600 dark:text-violet-400 flex items-center justify-center mb-4">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-1.5">
                  Plain-English Summary
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Understand unfamiliar codebases in seconds without digging through hundreds of files.
                </p>
              </div>

              <div className="p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/60 backdrop-blur-sm shadow-xs hover:border-amber-300 dark:hover:border-amber-700 transition-colors">
                <div className="w-10 h-10 rounded-2xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-4">
                  <BookOpen className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-1.5">
                  Onboarding Guides
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Exact terminal commands to clone, install dependencies, run test suites, and open PRs.
                </p>
              </div>
            </div>
          </div>
        ) : null}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200/80 dark:border-slate-800/80 py-8 bg-white/50 dark:bg-slate-950/50 backdrop-blur-xs transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-800 dark:text-slate-200">RepoLens</span>
            <span>—</span>
            <span>Open-source GitHub repository analyzer</span>
          </div>
          <div className="flex items-center gap-4">
            <span>FastAPI + React + Tailwind + Mermaid</span>
            <span className="text-slate-300 dark:text-slate-700">|</span>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-indigo-600 dark:hover:text-indigo-400 inline-flex items-center gap-1 transition-colors"
            >
              <span>GitHub</span>
              <ArrowUpRight className="w-3 h-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
export default App;

