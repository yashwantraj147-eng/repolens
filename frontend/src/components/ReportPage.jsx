import React, { useState, useRef, useEffect } from 'react';
import {
  Star,
  GitFork,
  AlertCircle,
  ExternalLink,
  Share2,
  Check,
  Calendar,
  Code,
  Shield,
  RotateCcw,
  Download,
  Printer,
  FileText,
  ChevronDown,
} from 'lucide-react';
import { ScoreCard } from './ScoreCard';
import { ScoreBreakdown } from './ScoreBreakdown';
import { MermaidDiagram } from './MermaidDiagram';
import { SummarySection } from './SummarySection';
import { OnboardingGuide } from './OnboardingGuide';
import { BadgeModal } from './BadgeModal';
import {
  generateMarkdownReport,
  generateContributingGuide,
  downloadTextFile,
} from '../utils/exportHelpers';

export function ReportPage({ report, onReset, darkMode }) {
  const [copiedShare, setCopiedShare] = useState(false);
  const [badgeModalOpen, setBadgeModalOpen] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const exportMenuRef = useRef(null);

  // Close export dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target)) {
        setExportOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!report) return null;

  const { repo, health_score, summary, architecture_diagram, onboarding_guide } = report;

  const handleShare = () => {
    if (typeof window !== 'undefined') {
      const shareUrl = `${window.location.origin}${window.location.pathname}?repo=${encodeURIComponent(`${repo.owner}/${repo.name}`)}`;
      navigator.clipboard.writeText(shareUrl);
      setCopiedShare(true);
      setTimeout(() => setCopiedShare(false), 2500);
    }
  };

  const handleDownloadMarkdown = () => {
    const md = generateMarkdownReport(report);
    downloadTextFile(`RepoLens-Audit-${repo.owner}-${repo.name}.md`, md);
    setExportOpen(false);
  };

  const handleDownloadContributing = () => {
    const md = generateContributingGuide(report);
    downloadTextFile('CONTRIBUTING.md', md);
    setExportOpen(false);
  };

  const handlePrint = () => {
    setExportOpen(false);
    if (typeof window !== 'undefined') {
      window.print();
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return 'N/A';
    try {
      return new Date(isoString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fadeIn">
      {/* Top Banner & Metadata */}
      <div className="rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                <a
                  href={repo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-indigo-600 dark:hover:text-indigo-400 inline-flex items-center gap-2 group transition-colors"
                >
                  <span>{repo.owner} / {repo.name}</span>
                  <ExternalLink className="w-5 h-5 text-slate-400 group-hover:text-indigo-500 transition-colors" />
                </a>
              </h1>
              {repo.license_name && (
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200/60 dark:border-indigo-800/60">
                  <Shield className="w-3.5 h-3.5" />
                  {repo.license_name}
                </span>
              )}
            </div>

            <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 max-w-3xl leading-relaxed">
              {repo.description || 'No description provided for this repository.'}
            </p>

            {/* Quick stats pills */}
            <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-500 dark:text-slate-400 pt-1">
              {repo.language && (
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                  <span>{repo.language}</span>
                </div>
              )}
              <div className="flex items-center gap-1.5">
                <Star className="w-4 h-4 text-amber-500" />
                <span>{repo.stars?.toLocaleString() || 0} stars</span>
              </div>
              <div className="flex items-center gap-1.5">
                <GitFork className="w-4 h-4 text-blue-500" />
                <span>{repo.forks?.toLocaleString() || 0} forks</span>
              </div>
              <div className="flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 text-rose-500" />
                <span>{repo.open_issues?.toLocaleString() || 0} open issues</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-slate-400" />
                <span>Updated {formatDate(repo.updated_at)}</span>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap items-center gap-2.5 shrink-0 no-print">
            {/* Embed Badge Button */}
            <button
              type="button"
              onClick={() => setBadgeModalOpen(true)}
              className="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl border border-indigo-200 dark:border-indigo-900 bg-indigo-50/70 dark:bg-indigo-950/50 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-xs font-semibold text-indigo-700 dark:text-indigo-300 transition-colors shadow-xs"
              title="Get vector SVG badge for README"
            >
              <Shield className="w-4 h-4 text-indigo-500" />
              <span>Embed Badge</span>
            </button>

            {/* Export Dropdown */}
            <div className="relative" ref={exportMenuRef}>
              <button
                type="button"
                onClick={() => setExportOpen((prev) => !prev)}
                className="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/80 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-colors shadow-xs"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {exportOpen && (
                <div className="absolute right-0 mt-2 w-56 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl py-2 z-30 text-xs animate-fadeIn">
                  <button
                    type="button"
                    onClick={handleDownloadMarkdown}
                    className="w-full px-4 py-2 text-left flex items-center gap-2.5 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors"
                  >
                    <FileText className="w-4 h-4 text-indigo-500" />
                    <div>
                      <div className="font-semibold">Download Audit (.md)</div>
                      <div className="text-[10px] text-slate-400">Full analysis & diagram</div>
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={handleDownloadContributing}
                    className="w-full px-4 py-2 text-left flex items-center gap-2.5 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors"
                  >
                    <Code className="w-4 h-4 text-emerald-500" />
                    <div>
                      <div className="font-semibold">CONTRIBUTING.md</div>
                      <div className="text-[10px] text-slate-400">Ready for repo root</div>
                    </div>
                  </button>
                  <div className="my-1 border-t border-slate-100 dark:border-slate-800" />
                  <button
                    type="button"
                    onClick={handlePrint}
                    className="w-full px-4 py-2 text-left flex items-center gap-2.5 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors"
                  >
                    <Printer className="w-4 h-4 text-slate-400" />
                    <div>
                      <div className="font-semibold">Print / Save as PDF</div>
                      <div className="text-[10px] text-slate-400">Print-optimized layout</div>
                    </div>
                  </button>
                </div>
              )}
            </div>

            {/* Share Button */}
            <button
              type="button"
              onClick={handleShare}
              className="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/80 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-colors shadow-xs"
            >
              {copiedShare ? (
                <>
                  <Check className="w-4 h-4 text-emerald-500" />
                  <span className="text-emerald-600 dark:text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Share2 className="w-4 h-4" />
                  <span>Share</span>
                </>
              )}
            </button>

            {/* New Analysis Button */}
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-md shadow-indigo-500/20 transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              <span>New Analysis</span>
            </button>
          </div>
        </div>
      </div>

      {/* Grid: Health Score + Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <ScoreCard healthScore={health_score} />
        </div>
        <div className="lg:col-span-2">
          <ScoreBreakdown breakdown={health_score?.breakdown} />
        </div>
      </div>

      {/* Repository Intelligence Summary */}
      <SummarySection summary={summary} repo={repo} />

      {/* Architecture & Module Flow Diagram */}
      <MermaidDiagram chart={architecture_diagram} darkMode={darkMode} />

      {/* Contributor Onboarding Guide */}
      <OnboardingGuide guide={onboarding_guide} repoName={repo.name} />

      {/* Badge Embed Modal */}
      <BadgeModal
        isOpen={badgeModalOpen}
        onClose={() => setBadgeModalOpen(false)}
        repo={repo}
        report={report}
      />
    </div>
  );
}
