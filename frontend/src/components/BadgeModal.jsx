import React, { useState } from 'react';
import { X, Check, Copy, Shield, ExternalLink, Code2 } from 'lucide-react';

export function BadgeModal({ repo, report, isOpen, onClose }) {
  const [style, setStyle] = useState('flat');
  const [copiedType, setCopiedType] = useState(null);

  if (!isOpen || !repo) return null;

  const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:5173';
  const apiBase = origin.includes(':5173') ? origin : origin; // works through vite proxy or direct host
  
  const badgeUrl = `${apiBase}/api/badge/${repo.owner}/${repo.name}.svg?style=${style}`;
  const reportUrl = `${origin}/?repo=${encodeURIComponent(`${repo.owner}/${repo.name}`)}`;

  const markdownSnippet = `[![RepoLens Health](${badgeUrl})](${reportUrl})`;
  const htmlSnippet = `<a href="${reportUrl}"><img src="${badgeUrl}" alt="RepoLens Health" /></a>`;
  const urlSnippet = badgeUrl;

  const handleCopy = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopiedType(type);
    setTimeout(() => setCopiedType(null), 2000);
  };

  const styleOptions = [
    { id: 'flat', label: 'Flat (Default)' },
    { id: 'flat-square', label: 'Flat Square' },
    { id: 'for-the-badge', label: 'For The Badge' },
  ];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fadeIn"
      onClick={onClose}
    >
      <div
        className="w-full max-w-xl rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl p-6 sm:p-8 space-y-6 text-slate-900 dark:text-slate-100 animate-scaleUp"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-950 dark:text-white">
                Embed Health Badge
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Display live RepoLens audit grade directly on your README
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Live Badge Preview Box */}
        <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/80 flex flex-col items-center justify-center gap-3">
          <span className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
            Live Preview
          </span>
          <div className="py-2 px-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/60 shadow-xs flex items-center justify-center min-h-[44px]">
            <img
              src={badgeUrl}
              alt="RepoLens Health Badge"
              className="h-6 sm:h-7"
              key={`${style}-${repo.owner}-${repo.name}`}
            />
          </div>
          <span className="text-[11px] text-slate-500 dark:text-slate-400">
            Vector SVG updates automatically as your repository metrics evolve
          </span>
        </div>

        {/* Style Selector */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
            Badge Style
          </label>
          <div className="grid grid-cols-3 gap-2">
            {styleOptions.map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setStyle(opt.id)}
                className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                  style === opt.id
                    ? 'border-indigo-600 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 shadow-xs'
                    : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Snippets */}
        <div className="space-y-3">
          {/* Markdown */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                Markdown (README.md)
              </span>
              <button
                type="button"
                onClick={() => handleCopy(markdownSnippet, 'markdown')}
                className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                {copiedType === 'markdown' ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-500" />
                    <span className="text-emerald-600 dark:text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            <pre className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-[11px] font-mono text-slate-800 dark:text-slate-200 overflow-x-auto whitespace-pre">
              {markdownSnippet}
            </pre>
          </div>

          {/* HTML */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                HTML
              </span>
              <button
                type="button"
                onClick={() => handleCopy(htmlSnippet, 'html')}
                className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                {copiedType === 'html' ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-500" />
                    <span className="text-emerald-600 dark:text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            <pre className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-[11px] font-mono text-slate-800 dark:text-slate-200 overflow-x-auto whitespace-pre">
              {htmlSnippet}
            </pre>
          </div>

          {/* Direct Image URL */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                Raw Badge URL
              </span>
              <button
                type="button"
                onClick={() => handleCopy(urlSnippet, 'url')}
                className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                {copiedType === 'url' ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-500" />
                    <span className="text-emerald-600 dark:text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            <pre className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-[11px] font-mono text-slate-800 dark:text-slate-200 overflow-x-auto whitespace-pre">
              {urlSnippet}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-2 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-900 dark:bg-slate-100 hover:bg-slate-800 dark:hover:bg-white text-white dark:text-slate-900 text-xs font-semibold shadow-xs transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

