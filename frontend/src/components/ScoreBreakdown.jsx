import React from 'react';
import {
  FileText,
  GitCommit,
  Clock,
  TestTube2,
  Scale,
  BookOpen,
  CheckCircle,
  HelpCircle,
} from 'lucide-react';

const CATEGORY_META = {
  readme_quality: {
    title: 'README Quality',
    icon: FileText,
    color: 'text-blue-500',
    barColor: 'bg-blue-500',
  },
  commit_activity: {
    title: 'Commit Activity',
    icon: GitCommit,
    color: 'text-purple-500',
    barColor: 'bg-purple-500',
  },
  issue_response_time: {
    title: 'Issue Response Time',
    icon: Clock,
    color: 'text-amber-500',
    barColor: 'bg-amber-500',
  },
  test_presence: {
    title: 'Test Presence',
    icon: TestTube2,
    color: 'text-emerald-500',
    barColor: 'bg-emerald-500',
  },
  license: {
    title: 'License',
    icon: Scale,
    color: 'text-indigo-500',
    barColor: 'bg-indigo-500',
  },
  documentation: {
    title: 'Documentation',
    icon: BookOpen,
    color: 'text-sky-500',
    barColor: 'bg-sky-500',
  },
  ci_setup: {
    title: 'CI / CD Setup',
    icon: CheckCircle,
    color: 'text-teal-500',
    barColor: 'bg-teal-500',
  },
};

export function ScoreBreakdown({ breakdown }) {
  if (!breakdown) return null;

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-8 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Score Breakdown
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Individual category metrics, weights, and findings
          </p>
        </div>
      </div>

      <div className="space-y-5">
        {Object.entries(breakdown).map(([key, data]) => {
          const meta = CATEGORY_META[key] || {
            title: key.replace(/_/g, ' '),
            icon: HelpCircle,
            color: 'text-slate-500',
            barColor: 'bg-slate-500',
          };
          const Icon = meta.icon;
          const weightPercent = Math.round((data.weight || 0) * 100);

          return (
            <div
              key={key}
              className="p-4 rounded-2xl border border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-950/40 hover:bg-slate-50 dark:hover:bg-slate-950/80 transition-colors"
            >
              <div className="flex items-center justify-between gap-4 mb-2">
                <div className="flex items-center gap-2.5">
                  <div className={`p-1.5 rounded-lg bg-white dark:bg-slate-800 ${meta.color} shadow-xs`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                    {meta.title}
                  </span>
                  <span className="text-[11px] font-medium text-slate-400 dark:text-slate-500">
                    ({weightPercent}% weight)
                  </span>
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-base font-bold text-slate-900 dark:text-white">
                    {data.score}
                  </span>
                  <span className="text-xs text-slate-400">/100</span>
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full h-2 rounded-full bg-slate-200/80 dark:bg-slate-800 overflow-hidden my-2">
                <div
                  className={`h-full rounded-full ${meta.barColor} transition-all duration-700 ease-out`}
                  style={{ width: `${Math.min(100, Math.max(0, data.score))}%` }}
                />
              </div>

              {/* Detailed insights */}
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                {data.details}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

