import React, { useState } from 'react';
import {
  Trophy,
  Scale,
  Star,
  GitFork,
  AlertCircle,
  ExternalLink,
  Share2,
  Check,
  RotateCcw,
  ArrowRight,
  ShieldCheck,
  FileText,
  Clock,
  TestTube2,
  GitCommit,
  BookOpen,
  CheckCircle,
  HelpCircle,
  Sparkles,
} from 'lucide-react';

const CATEGORY_META = {
  readme_quality: { title: 'README Quality', icon: FileText, color: 'text-blue-500' },
  test_presence: { title: 'Test Presence', icon: TestTube2, color: 'text-emerald-500' },
  security_posture: { title: 'Security & Supply Chain', icon: ShieldCheck, color: 'text-rose-500' },
  commit_activity: { title: 'Commit Velocity', icon: GitCommit, color: 'text-purple-500' },
  documentation: { title: 'Documentation & Community', icon: BookOpen, color: 'text-sky-500' },
  ci_setup: { title: 'CI / CD Pipeline', icon: CheckCircle, color: 'text-teal-500' },
  issue_response_time: { title: 'Issue Resolution Speed', icon: Clock, color: 'text-amber-500' },
  license: { title: 'Open-Source License', icon: Scale, color: 'text-indigo-500' },
};

export function ComparePage({ compareData, onReset, onSelectReport }) {
  const [copiedShare, setCopiedShare] = useState(false);

  if (!compareData) return null;

  const { repo_a, repo_b, comparison } = compareData;
  const nameA = `${repo_a.repo.owner}/${repo_a.repo.name}`;
  const nameB = `${repo_b.repo.owner}/${repo_b.repo.name}`;

  const handleShare = () => {
    if (typeof window !== 'undefined') {
      const shareUrl = `${window.location.origin}${window.location.pathname}?compare=${encodeURIComponent(`${nameA},${nameB}`)}`;
      navigator.clipboard.writeText(shareUrl);
      setCopiedShare(true);
      setTimeout(() => setCopiedShare(false), 2500);
    }
  };

  const getWinnerBadge = () => {
    if (comparison.overall_winner === 'repo_a') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black bg-emerald-50 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border border-emerald-200/60 dark:border-emerald-800/60">
          <Trophy className="w-3.5 h-3.5 text-amber-500" />
          <span>{nameA} Leads (+{Math.abs(comparison.score_diff)} pts)</span>
        </span>
      );
    }
    if (comparison.overall_winner === 'repo_b') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black bg-purple-50 dark:bg-purple-950/80 text-purple-700 dark:text-purple-300 border border-purple-200/60 dark:border-purple-800/60">
          <Trophy className="w-3.5 h-3.5 text-amber-500" />
          <span>{nameB} Leads (+{Math.abs(comparison.score_diff)} pts)</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
        <Scale className="w-3.5 h-3.5 text-indigo-500" />
        <span>Evenly Matched (Tie)</span>
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fadeIn">
      {/* Top Comparison Header */}
      <div className="rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-6 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-black text-slate-950 dark:text-white">
                Head-to-Head Comparison
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Comparing architecture health, code quality, and maintainability metrics
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={handleShare}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/80 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-colors shadow-xs"
            >
              {copiedShare ? (
                <>
                  <Check className="w-4 h-4 text-emerald-500" />
                  <span className="text-emerald-600 dark:text-emerald-400">Link Copied!</span>
                </>
              ) : (
                <>
                  <Share2 className="w-4 h-4" />
                  <span>Share Matchup</span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-md shadow-indigo-500/20 transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              <span>New Matchup</span>
            </button>
          </div>
        </div>

        {/* Dual Repo Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
          {/* Repo A Card */}
          <div className={`p-6 rounded-2xl border transition-all ${
            comparison.overall_winner === 'repo_a'
              ? 'border-indigo-400 dark:border-indigo-600 bg-indigo-50/30 dark:bg-indigo-950/20 shadow-md shadow-indigo-500/5'
              : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40'
          }`}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <span className="text-[10px] font-black uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
                  REPOSITORY A
                </span>
                <h2 className="text-lg sm:text-xl font-black text-slate-900 dark:text-white mt-1">
                  <a
                    href={repo_a.repo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-indigo-600 dark:hover:text-indigo-400 inline-flex items-center gap-1.5"
                  >
                    <span>{nameA}</span>
                    <ExternalLink className="w-4 h-4 text-slate-400" />
                  </a>
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                  {repo_a.repo.description || 'No description provided.'}
                </p>
              </div>

              <div className="text-right shrink-0">
                <div className="text-3xl font-black text-slate-900 dark:text-white">
                  {repo_a.health_score.overall}
                </div>
                <span className="px-2 py-0.5 rounded-md text-xs font-black bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300">
                  Grade {repo_a.health_score.grade}
                </span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-200/60 dark:border-slate-800/60 flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
              <span className="font-semibold">{repo_a.repo.language || 'Multi-language'}</span>
              <button
                type="button"
                onClick={() => onSelectReport(repo_a.report_id)}
                className="inline-flex items-center gap-1 text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
              >
                <span>View Full Audit</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Repo B Card */}
          <div className={`p-6 rounded-2xl border transition-all ${
            comparison.overall_winner === 'repo_b'
              ? 'border-purple-400 dark:border-purple-600 bg-purple-50/30 dark:bg-purple-950/20 shadow-md shadow-purple-500/5'
              : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40'
          }`}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <span className="text-[10px] font-black uppercase tracking-wider text-purple-600 dark:text-purple-400">
                  REPOSITORY B
                </span>
                <h2 className="text-lg sm:text-xl font-black text-slate-900 dark:text-white mt-1">
                  <a
                    href={repo_b.repo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-purple-600 dark:hover:text-purple-400 inline-flex items-center gap-1.5"
                  >
                    <span>{nameB}</span>
                    <ExternalLink className="w-4 h-4 text-slate-400" />
                  </a>
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                  {repo_b.repo.description || 'No description provided.'}
                </p>
              </div>

              <div className="text-right shrink-0">
                <div className="text-3xl font-black text-slate-900 dark:text-white">
                  {repo_b.health_score.overall}
                </div>
                <span className="px-2 py-0.5 rounded-md text-xs font-black bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300">
                  Grade {repo_b.health_score.grade}
                </span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-200/60 dark:border-slate-800/60 flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
              <span className="font-semibold">{repo_b.repo.language || 'Multi-language'}</span>
              <button
                type="button"
                onClick={() => onSelectReport(repo_b.report_id)}
                className="inline-flex items-center gap-1 text-purple-600 dark:text-purple-400 font-semibold hover:underline"
              >
                <span>View Full Audit</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Winner Announcement Banner */}
        <div className="mt-6 p-4 rounded-2xl bg-slate-50 dark:bg-slate-950/70 border border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            {getWinnerBadge()}
            <span className="text-xs text-slate-600 dark:text-slate-300">
              {comparison.verdict_summary}
            </span>
          </div>
        </div>
      </div>

      {/* Community & Activity Head-to-Head */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {/* Stars */}
        <div className="p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 shadow-2xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
              <span>GitHub Stars</span>
            </span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
              Δ {Math.abs(comparison.metrics.stars_diff).toLocaleString()}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-center pt-1">
            <div className={`p-2.5 rounded-xl ${comparison.metrics.stars_winner === 'repo_a' ? 'bg-indigo-50 dark:bg-indigo-950/70 font-bold' : 'bg-slate-50 dark:bg-slate-950/50'}`}>
              <div className="text-xs text-slate-400 truncate">{repo_a.repo.name}</div>
              <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">{repo_a.repo.stars.toLocaleString()}</div>
            </div>
            <div className={`p-2.5 rounded-xl ${comparison.metrics.stars_winner === 'repo_b' ? 'bg-purple-50 dark:bg-purple-950/70 font-bold' : 'bg-slate-50 dark:bg-slate-950/50'}`}>
              <div className="text-xs text-slate-400 truncate">{repo_b.repo.name}</div>
              <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">{repo_b.repo.stars.toLocaleString()}</div>
            </div>
          </div>
        </div>

        {/* Forks */}
        <div className="p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 shadow-2xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <GitFork className="w-4 h-4 text-blue-500" />
              <span>Forks</span>
            </span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
              Δ {Math.abs(comparison.metrics.forks_diff).toLocaleString()}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-center pt-1">
            <div className={`p-2.5 rounded-xl ${comparison.metrics.forks_winner === 'repo_a' ? 'bg-indigo-50 dark:bg-indigo-950/70 font-bold' : 'bg-slate-50 dark:bg-slate-950/50'}`}>
              <div className="text-xs text-slate-400 truncate">{repo_a.repo.name}</div>
              <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">{repo_a.repo.forks.toLocaleString()}</div>
            </div>
            <div className={`p-2.5 rounded-xl ${comparison.metrics.forks_winner === 'repo_b' ? 'bg-purple-50 dark:bg-purple-950/70 font-bold' : 'bg-slate-50 dark:bg-slate-950/50'}`}>
              <div className="text-xs text-slate-400 truncate">{repo_b.repo.name}</div>
              <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">{repo_b.repo.forks.toLocaleString()}</div>
            </div>
          </div>
        </div>

        {/* Open Issues */}
        <div className="p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 shadow-2xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-rose-500" />
              <span>Open Issues</span>
            </span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
              Δ {Math.abs(comparison.metrics.open_issues_diff).toLocaleString()}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-center pt-1">
            <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/50">
              <div className="text-xs text-slate-400 truncate">{repo_a.repo.name}</div>
              <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">{repo_a.repo.open_issues.toLocaleString()}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/50">
              <div className="text-xs text-slate-400 truncate">{repo_b.repo.name}</div>
              <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">{repo_b.repo.open_issues.toLocaleString()}</div>
            </div>
          </div>
        </div>
      </div>

      {/* 8-Category Health Score Breakdown Matrix */}
      <div className="rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 sm:p-8 shadow-sm space-y-6">
        <div>
          <h2 className="text-lg font-black text-slate-950 dark:text-white">
            8-Category Health Score Matrix
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Side-by-side metric comparison across all evaluated categories
          </p>
        </div>

        <div className="space-y-4">
          {comparison.categories.map((cat) => {
            const meta = CATEGORY_META[cat.category] || {
              title: cat.name,
              icon: HelpCircle,
              color: 'text-slate-500',
            };
            const Icon = meta.icon;

            return (
              <div
                key={cat.category}
                className="p-4 sm:p-5 rounded-2xl border border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/40 hover:bg-slate-50 dark:hover:bg-slate-950/80 transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className={`p-1.5 rounded-lg bg-white dark:bg-slate-800 ${meta.color} shadow-xs`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="text-sm font-bold text-slate-900 dark:text-white">
                        {meta.title}
                      </span>
                    </div>
                  </div>

                  {/* Winner Pill */}
                  <div className="shrink-0">
                    {cat.winner === 'repo_a' && (
                      <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-50 dark:bg-indigo-950/70 text-indigo-700 dark:text-indigo-300 border border-indigo-200/60 dark:border-indigo-800/60">
                        {repo_a.repo.name} (+{cat.diff})
                      </span>
                    )}
                    {cat.winner === 'repo_b' && (
                      <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-purple-50 dark:bg-purple-950/70 text-purple-700 dark:text-purple-300 border border-purple-200/60 dark:border-purple-800/60">
                        {repo_b.repo.name} (+{Math.abs(cat.diff)})
                      </span>
                    )}
                    {cat.winner === 'tie' && (
                      <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        Tied ({cat.score_a}/100)
                      </span>
                    )}
                  </div>
                </div>

                {/* Score Comparison Bars */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1 text-xs">
                  {/* Repo A Bar */}
                  <div>
                    <div className="flex items-center justify-between mb-1 text-slate-600 dark:text-slate-400 font-medium">
                      <span>{repo_a.repo.name}</span>
                      <span className="font-bold text-slate-900 dark:text-white">{cat.score_a}/100</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                        style={{ width: `${cat.score_a}%` }}
                      />
                    </div>
                    <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1 truncate">
                      {cat.details_a}
                    </p>
                  </div>

                  {/* Repo B Bar */}
                  <div>
                    <div className="flex items-center justify-between mb-1 text-slate-600 dark:text-slate-400 font-medium">
                      <span>{repo_b.repo.name}</span>
                      <span className="font-bold text-slate-900 dark:text-white">{cat.score_b}/100</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-purple-500 transition-all duration-500"
                        style={{ width: `${cat.score_b}%` }}
                      />
                    </div>
                    <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1 truncate">
                      {cat.details_b}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
