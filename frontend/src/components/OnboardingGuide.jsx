import React, { useState } from 'react';
import { BookOpen, Copy, Check, Terminal, GitPullRequest } from 'lucide-react';

export function OnboardingGuide({ guide, repoName }) {
  const [copiedCode, setCopiedCode] = useState(null);

  if (!guide) return null;

  const handleCopyCode = (code, index) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(index);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  // Helper to parse simple markdown blocks
  const renderGuideContent = (content) => {
    const lines = content.split('\n');
    const elements = [];
    let currentCodeBlock = null;
    let codeIndex = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      if (line.startsWith('```')) {
        if (currentCodeBlock === null) {
          currentCodeBlock = { lang: line.replace('```', '').trim(), lines: [] };
        } else {
          const codeText = currentCodeBlock.lines.join('\n');
          const blockIdx = codeIndex++;
          elements.push(
            <div key={`code-${blockIdx}`} className="relative my-3 rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-md">
              <div className="flex items-center justify-between px-4 py-2 bg-slate-900/90 border-b border-slate-800 text-[11px] text-slate-400 font-mono">
                <span className="flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-indigo-400" />
                  {currentCodeBlock.lang || 'bash'}
                </span>
                <button
                  type="button"
                  onClick={() => handleCopyCode(codeText, blockIdx)}
                  className="flex items-center gap-1 hover:text-white transition-colors"
                >
                  {copiedCode === blockIdx ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
              <pre className="p-4 text-xs font-mono text-slate-200 overflow-x-auto leading-relaxed">
                <code>{codeText}</code>
              </pre>
            </div>
          );
          currentCodeBlock = null;
        }
        continue;
      }

      if (currentCodeBlock !== null) {
        currentCodeBlock.lines.push(line);
        continue;
      }

      if (line.startsWith('## ')) {
        elements.push(
          <h2 key={i} className="text-xl font-extrabold text-slate-900 dark:text-white mt-6 mb-3">
            {line.replace('## ', '')}
          </h2>
        );
      } else if (line.startsWith('### ')) {
        elements.push(
          <h3 key={i} className="text-base font-bold text-slate-800 dark:text-slate-100 mt-5 mb-2">
            {line.replace('### ', '')}
          </h3>
        );
      } else if (line.startsWith('- ')) {
        elements.push(
          <li key={i} className="text-sm text-slate-700 dark:text-slate-300 ml-4 list-disc mb-1">
            {line.replace('- ', '')}
          </li>
        );
      } else if (/^\d+\.\s/.test(line)) {
        elements.push(
          <p key={i} className="text-sm text-slate-700 dark:text-slate-300 font-medium my-1.5">
            {line}
          </p>
        );
      } else if (line.trim()) {
        elements.push(
          <p key={i} className="text-sm text-slate-600 dark:text-slate-400 my-2 leading-relaxed">
            {line}
          </p>
        );
      }
    }

    return elements;
  };

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-8 shadow-sm">
      <div className="flex items-center gap-2.5 mb-6">
        <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
          <BookOpen className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Contributor Onboarding Guide
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Step-by-step developer setup, testing commands, and contribution workflow
          </p>
        </div>
      </div>

      <div className="space-y-2">
        {renderGuideContent(guide)}
      </div>
    </div>
  );
}

