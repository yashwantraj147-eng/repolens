import React from 'react';
import { Award, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';

export function ScoreCard({ healthScore }) {
  if (!healthScore) return null;

  const { overall, grade } = healthScore;

  // Grade color schemes
  const getGradeTheme = (g) => {
    if (g.startsWith('A')) {
      return {
        stroke: '#10B981', // Emerald
        bg: 'from-emerald-500/10 to-teal-500/5',
        badge: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800',
        label: 'Excellent Quality',
        icon: CheckCircle2,
      };
    } else if (g.startsWith('B')) {
      return {
        stroke: '#3B82F6', // Blue
        bg: 'from-blue-500/10 to-indigo-500/5',
        badge: 'bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 border-blue-300 dark:border-blue-800',
        label: 'Healthy & Maintained',
        icon: TrendingUp,
      };
    } else if (g.startsWith('C')) {
      return {
        stroke: '#F59E0B', // Amber
        bg: 'from-amber-500/10 to-orange-500/5',
        badge: 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-300 dark:border-amber-800',
        label: 'Needs Attention',
        icon: AlertTriangle,
      };
    } else {
      return {
        stroke: '#EF4444', // Red
        bg: 'from-rose-500/10 to-red-500/5',
        badge: 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border-rose-300 dark:border-rose-800',
        label: 'Critical Gaps',
        icon: AlertTriangle,
      };
    }
  };

  const theme = getGradeTheme(grade);
  const StatusIcon = theme.icon;

  // Circle dimensions
  const size = 180;
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (overall / 100) * circumference;

  return (
    <div className={`relative overflow-hidden rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-gradient-to-br ${theme.bg} bg-white dark:bg-slate-900/90 p-8 shadow-sm flex flex-col items-center text-center`}>
      <div className="flex items-center gap-2 mb-6">
        <Award className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Repository Health Score
        </h3>
      </div>

      {/* Radial Gauge */}
      <div className="relative flex items-center justify-center my-2">
        <svg width={size} height={size} className="rotate-[-90deg]">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-slate-100 dark:text-slate-800"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={theme.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center score label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-black tracking-tight text-slate-900 dark:text-white">
            {overall}
          </span>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            Out of 100
          </span>
        </div>
      </div>

      {/* Grade and Status Pill */}
      <div className="mt-6 flex flex-col items-center gap-2">
        <div className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border text-xs font-bold ${theme.badge}`}>
          <StatusIcon className="w-3.5 h-3.5" />
          <span>Grade {grade} · {theme.label}</span>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs mt-1">
          Weighted evaluation across 7 key signals: documentation, tests, commit rhythm, and CI setup.
        </p>
      </div>
    </div>
  );
}

