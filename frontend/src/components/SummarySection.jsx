import React from 'react';
import { Sparkles, Tag, Code2, Layers } from 'lucide-react';

export function SummarySection({ summary, repo }) {
  if (!summary) return null;

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-8 shadow-sm">
      <div className="flex items-center gap-2.5 mb-5">
        <div className="p-2 rounded-xl bg-violet-50 dark:bg-violet-950/60 text-violet-600 dark:text-violet-400">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Repository Intelligence Summary
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Synthesized overview of functionality, stack, and purpose
          </p>
        </div>
      </div>

      <div className="prose dark:prose-invert max-w-none text-slate-700 dark:text-slate-300 text-sm leading-relaxed space-y-3">
        {summary.split('\n\n').map((paragraph, idx) => (
          <p key={idx} className="leading-relaxed">
            {paragraph}
          </p>
        ))}
      </div>

      {repo?.topics && repo.topics.length > 0 && (
        <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-800/80">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400 mb-3">
            <Tag className="w-3.5 h-3.5" />
            <span>Repository Topics</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {repo.topics.map((topic) => (
              <span
                key={topic}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              >
                #{topic}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

