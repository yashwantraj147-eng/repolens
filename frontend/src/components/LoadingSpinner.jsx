import React from 'react';
import { Loader2, Sparkles, GitBranch, ShieldCheck } from 'lucide-react';

export function LoadingSpinner({ stage = 'Analyzing repository...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 dark:bg-indigo-500/20 flex items-center justify-center animate-pulse">
          <Loader2 className="w-8 h-8 text-indigo-600 dark:text-indigo-400 animate-spin" />
        </div>
        <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center">
          <Sparkles className="w-3.5 h-3.5 animate-bounce" />
        </div>
      </div>
      <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-2">
        {stage}
      </h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm">
        Fetching file tree, calculating health metrics, generating Mermaid architecture diagram, and drafting contributor guide...
      </p>

      <div className="mt-8 grid grid-cols-3 gap-4 text-xs text-slate-500 dark:text-slate-400 max-w-md w-full">
        <div className="flex items-center gap-1.5 justify-center py-2 px-3 rounded-lg bg-slate-100 dark:bg-slate-900">
          <GitBranch className="w-3.5 h-3.5 text-indigo-500" />
          <span>Structure Map</span>
        </div>
        <div className="flex items-center gap-1.5 justify-center py-2 px-3 rounded-lg bg-slate-100 dark:bg-slate-900">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
          <span>7-Point Health</span>
        </div>
        <div className="flex items-center gap-1.5 justify-center py-2 px-3 rounded-lg bg-slate-100 dark:bg-slate-900">
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          <span>AI Summary</span>
        </div>
      </div>
    </div>
  );
}

