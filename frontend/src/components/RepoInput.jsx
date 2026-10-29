import React, { useState } from 'react';
import { Search, ArrowRight, Sparkles, X, Github } from 'lucide-react';

const SAMPLE_REPOS = [
  { label: 'FastAPI', url: 'https://github.com/fastapi/fastapi', desc: 'Python API framework' },
  { label: 'Express', url: 'https://github.com/expressjs/express', desc: 'Node.js web framework' },
  { label: 'Flask', url: 'https://github.com/pallets/flask', desc: 'Python micro-framework' },
  { label: 'React', url: 'https://github.com/facebook/react', desc: 'UI library' },
];

export function RepoInput({ onAnalyze, loading }) {
  const [url, setUrl] = useState('');
  const [validationError, setValidationError] = useState('');

  const validateUrl = (value) => {
    if (!value.trim()) {
      return 'Please enter a GitHub repository URL.';
    }
    const githubRegex = /^(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9\-_.]+)\/([a-zA-Z0-9\-_.]+?)(?:\.git)?(?:\/.*)?$/;
    if (!githubRegex.test(value.trim())) {
      return 'Please enter a valid GitHub URL, e.g. https://github.com/owner/repo';
    }
    return '';
  };

  const handleSubmit = (e) => {
    e?.preventDefault();
    const error = validateUrl(url);
    if (error) {
      setValidationError(error);
      return;
    }
    setValidationError('');
    onAnalyze(url.trim());
  };

  const handleSelectSample = (sampleUrl) => {
    setUrl(sampleUrl);
    setValidationError('');
    onAnalyze(sampleUrl);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative group">
        <div className="relative flex items-center rounded-2xl border-2 border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-lg shadow-indigo-500/5 group-focus-within:border-indigo-500 dark:group-focus-within:border-indigo-500 transition-all duration-200">
          <div className="pl-4 pr-2 text-slate-400 dark:text-slate-500 flex items-center">
            <Github className="w-5 h-5" />
          </div>
          <input
            type="text"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (validationError) setValidationError('');
            }}
            placeholder="Paste public GitHub URL (e.g., https://github.com/fastapi/fastapi)"
            disabled={loading}
            aria-label="GitHub Repository URL"
            className="w-full py-4 px-2 text-sm sm:text-base bg-transparent text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none disabled:opacity-50"
          />
          {url && !loading && (
            <button
              type="button"
              onClick={() => {
                setUrl('');
                setValidationError('');
              }}
              aria-label="Clear input"
              className="p-1.5 mr-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <div className="pr-2.5">
            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm text-white bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-indigo-500/25 transition-all duration-150"
            >
              <span>{loading ? 'Analyzing...' : 'Analyze'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {validationError && (
          <p className="mt-2 text-xs font-medium text-rose-500 dark:text-rose-400 pl-4">
            {validationError}
          </p>
        )}
      </form>

      {/* Quick sample pills */}
      <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs">
        <span className="text-slate-500 dark:text-slate-400 flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
          Try sample:
        </span>
        {SAMPLE_REPOS.map((sample) => (
          <button
            key={sample.label}
            type="button"
            disabled={loading}
            onClick={() => handleSelectSample(sample.url)}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/70 text-slate-700 dark:text-slate-300 hover:border-indigo-400 dark:hover:border-indigo-600 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all duration-150 disabled:opacity-50 shadow-sm"
          >
            <span className="font-medium">{sample.label}</span>
            <span className="ml-1.5 text-slate-400 dark:text-slate-500 hidden sm:inline">
              · {sample.desc}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

