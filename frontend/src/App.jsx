import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { RepoInput } from './components/RepoInput';
import { ReportPage } from './components/ReportPage';
import { CompareInput } from './components/CompareInput';
import { ComparePage } from './components/ComparePage';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorAlert } from './components/ErrorAlert';
import { useAnalyze } from './hooks/useAnalyze';
import { getRecentReports, compareRepositories } from './utils/api';
import {
  GitFork,
  Sparkles,
  GitGraph,
  ShieldCheck,
  BookOpen,
  ArrowUpRight,
  Terminal,
  History,
  Star,
  Scale,
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

  const [mode, setMode] = useState('single'); // 'single' | 'compare'
  const [compareData, setCompareData] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState(null);

  const { report, loading, error, analyze, loadReport, reset } = useAnalyze();
  const [recentReports, setRecentReports] = useState([]);

  // Fetch recent reports on mount and when returning to landing
  useEffect(() => {
    if (!report && !compareData && !loading && !compareLoading) {
      getRecentReports(4)
        .then((items) => setRecentReports(items || []))
        .catch(() => setRecentReports([]));
    }
  }, [report, compareData, loading, compareLoading]);

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

  const handleCompare = async (repoA, repoB, forceRefresh = false) => {
    setCompareLoading(true);
    setCompareError(null);
    try {
      const data = await compareRepositories(repoA, repoB, forceRefresh);
      setCompareData(data);
      if (typeof window !== 'undefined' && window.history) {
        const url = new URL(window.location.href);
        url.searchParams.set('compare', `${repoA},${repoB}`);
        window.history.pushState({}, '', url.toString());
      }
    } catch (err) {
      setCompareError(err.message || 'Failed to compare repositories.');
    } finally {
      setCompareLoading(false);
    }
  };

  const handleResetCompare = () => {
    setCompareData(null);
    setCompareError(null);
    if (typeof window !== 'undefined' && window.history) {
      window.history.pushState({}, '', window.location.pathname);
    }
  };

  const handleSelectReportFromCompare = async (reportId) => {
    setCompareData(null);
    setMode('single');
    await loadReport(reportId);
  };

  // Load report or comparison from URL query parameters on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const reportId = params.get('report_id');
      const repoParam = params.get('repo') || params.get('url');
      const compareParam = params.get('compare');

      if (compareParam && !compareData && !compareLoading) {
        setMode('compare');
        const parts = compareParam.split(',');
        if (parts.length === 2) {
          handleCompare(parts[0], parts[1]);
        }
      } else if (reportId && !report) {
        loadReport(reportId).catch(() => {
          window.history.replaceState({}, '', window.location.pathname);
        });
      } else if (repoParam && !report && !loading) {
        const fullUrl = repoParam.startsWith('http')
          ? repoParam
          : `https://github.com/${repoParam}`;
        analyze(fullUrl).catch(() => {
          window.history.replaceState({}, '', window.location.pathname);
        });
      }
    }
  }, []);

  const handleGlobalReset = () => {
    reset();
    handleResetCompare();
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 selection:bg-indigo-500 selection:text-white">
      <Header darkMode={darkMode} setDarkMode={setDarkMode} onReset={handleGlobalReset} />

      <main className="flex-1 pb-16">
        {(loading || compareLoading) && <LoadingSpinner />}

        {(error || compareError) && !loading && !compareLoading && (
          <div className="max-w-3xl mx-auto px-4 mt-8">
            <ErrorAlert
              message={error || compareError}
              onRetry={() => {
                if (error) reset();
                if (compareError) handleResetCompare();
              }}
            />
          </div>
        )}

        {/* View 1: Single Report View */}
        {!loading && !compareLoading && report ? (
          <ReportPage report={report} onReset={reset} darkMode={darkMode} />
        ) : null}

        {/* View 2: Comparison Report View */}
        {!loading && !compareLoading && !report && compareData ? (
          <ComparePage
            compareData={compareData}
            onReset={handleResetCompare}
            onSelectReport={handleSelectReportFromCompare}
          />
        ) : null}

        {/* View 3: Landing / Search State */}
        {!loading && !compareLoading && !report && !compareData ? (
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 sm:pt-20 text-center">
            {/* Pill */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-indigo-200 dark:border-indigo-800/80 bg-indigo-50/70 dark:bg-indigo-950/50 text-xs font-semibold text-indigo-700 dark:text-indigo-300 mb-6 backdrop-blur-sm shadow-xs animate-bounce">
              <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
              <span>Full-Stack Repository Intelligence</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-slate-950 dark:text-white max-w-4xl mx-auto leading-[1.15]">
              Instant architecture diagrams, health audits &{' '}
              <span className="bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-500 bg-clip-text text-transparent">
                head-to-head comparisons
              </span>
            </h1>

            <p className="mt-5 text-base sm:text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
              Drop any public repository link or compare two repositories side-by-side to analyze architecture, supply chain security, test coverage, and onboarding guides.
            </p>

            {/* Mode Switcher Toggle */}
            <div className="flex items-center justify-center mt-8 mb-6">
              <div className="inline-flex p-1 rounded-2xl bg-slate-200/70 dark:bg-slate-900 border border-slate-300/80 dark:border-slate-800 shadow-inner">
                <button
                  type="button"
                  onClick={() => setMode('single')}
                  className={`px-5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    mode === 'single'
                      ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  Single Repository
                </button>
                <button
                  type="button"
                  onClick={() => setMode('compare')}
                  className={`px-5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                    mode === 'compare'
                      ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <Scale className="w-3.5 h-3.5" />
                  <span>Compare Repos</span>
                </button>
              </div>
            </div>

            {/* Input Bar according to active mode */}
            <div className="mb-12">
              {mode === 'single' ? (
                <RepoInput onAnalyze={analyze} loading={loading} />
              ) : (
                <CompareInput onCompare={handleCompare} loading={compareLoading} />
              )}
            </div>

            {/* Recently Analyzed Shelf (Single mode only) */}
            {mode === 'single' && recentReports && recentReports.length > 0 && (
              <div className="mb-14 text-left max-w-3xl mx-auto">
                <div className="flex items-center gap-2 mb-3 px-1 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  <History className="w-3.5 h-3.5 text-indigo-500" />
                  <span>Recently Analyzed Repositories</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {recentReports.map((item) => (
                    <button
                      key={item.report_id}
                      type="button"
                      onClick={() => loadReport(item.report_id)}
                      className="p-3.5 rounded-2xl border border-slate-200/90 dark:border-slate-800/90 bg-white/80 dark:bg-slate-900/80 hover:bg-slate-50 dark:hover:bg-slate-800/80 hover:border-indigo-400 dark:hover:border-indigo-600 transition-all text-left flex items-center justify-between group shadow-2xs cursor-pointer"
                    >
                      <div className="min-w-0 pr-3">
                        <div className="text-xs font-bold text-slate-900 dark:text-white truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                          {item.owner} / {item.name}
                        </div>
                        <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                          {item.language && <span>{item.language}</span>}
                          {item.language && <span>•</span>}
                          <span className="inline-flex items-center gap-1">
                            <Star className="w-3 h-3 text-amber-500 fill-amber-500" />
                            {item.stars.toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className="px-2 py-0.5 rounded-lg text-xs font-black bg-indigo-50 dark:bg-indigo-950/70 text-indigo-700 dark:text-indigo-300 border border-indigo-200/60 dark:border-indigo-800/60">
                          {item.overall_score} ({item.grade})
                        </span>
                        <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

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
                  8-Point Health Score
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Weighted evaluation of tests, security posture, README quality, issue response, license, and CI/CD.
                </p>
              </div>

              <div className="p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/60 backdrop-blur-sm shadow-xs hover:border-violet-300 dark:hover:border-violet-700 transition-colors">
                <div className="w-10 h-10 rounded-2xl bg-violet-50 dark:bg-violet-950/60 text-violet-600 dark:text-violet-400 flex items-center justify-center mb-4">
                  <Scale className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-1.5">
                  RepoLens Compare
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Compare two libraries or tools head-to-head with delta matrices and tradeoff summaries.
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
            <span>Open-source GitHub repository analyzer & comparison engine</span>
          </div>
          <div className="flex items-center gap-4">
            <span>FastAPI + React + Tailwind + Mermaid</span>
            <span className="text-slate-300 dark:text-slate-700">|</span>
            <a
              href="https://github.com/yashwantraj147-eng/repolens"
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
