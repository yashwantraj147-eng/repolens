import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export function ErrorAlert({ message, onRetry }) {
  return (
    <div className="rounded-2xl border border-rose-200 dark:border-rose-900/50 bg-rose-50/80 dark:bg-rose-950/30 p-6 my-6 shadow-sm backdrop-blur-sm">
      <div className="flex items-start gap-4">
        <div className="p-2.5 rounded-xl bg-rose-100 dark:bg-rose-900/50 text-rose-600 dark:text-rose-400 shrink-0">
          <AlertCircle className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h4 className="text-base font-semibold text-rose-900 dark:text-rose-200 mb-1">
            Analysis Failed
          </h4>
          <p className="text-sm text-rose-700 dark:text-rose-300/90 leading-relaxed">
            {message}
          </p>
          <div className="mt-4 flex items-center gap-3">
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium bg-rose-600 hover:bg-rose-700 text-white shadow-sm transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Try Again
              </button>
            )}
            <span className="text-xs text-rose-500 dark:text-rose-400">
              Check that the repository is public and the URL is formatted as <code className="font-mono">https://github.com/owner/repo</code>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

