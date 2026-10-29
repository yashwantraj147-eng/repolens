import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Copy, Check, GitGraph, Maximize2 } from 'lucide-react';

export function MermaidDiagram({ chart, darkMode }) {
  const containerRef = useRef(null);
  const [copied, setCopied] = useState(false);
  const [renderError, setRenderError] = useState(null);
  const [svgContent, setSvgContent] = useState('');

  useEffect(() => {
    let isMounted = true;

    async function renderChart() {
      if (!chart || !containerRef.current) return;

      try {
        setRenderError(null);
        mermaid.initialize({
          startOnLoad: false,
          suppressErrorRendering: true,
          theme: darkMode ? 'dark' : 'neutral',
          themeVariables: darkMode
            ? {
                primaryColor: '#4F46E5',
                primaryTextColor: '#FFFFFF',
                primaryBorderColor: '#6366F1',
                lineColor: '#818CF8',
                secondaryColor: '#1E1B4B',
                tertiaryColor: '#0F172A',
                background: '#0B0F19',
              }
            : {
                primaryColor: '#EEF2FF',
                primaryTextColor: '#1E1B4B',
                primaryBorderColor: '#6366F1',
                lineColor: '#6366F1',
                secondaryColor: '#F8FAFC',
                tertiaryColor: '#FFFFFF',
              },
          securityLevel: 'loose',
          fontFamily: 'Inter, system-ui, sans-serif',
        });

        // Clean up any stray error elements Mermaid may have injected into document.body
        document.querySelectorAll('[id^="dmermaid"], [id^="mermaid-"]').forEach((el) => {
          if (el.parentElement === document.body) el.remove();
        });

        const id = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
        const { svg } = await mermaid.render(id, chart);

        if (isMounted) {
          setSvgContent(svg);
        }
      } catch (err) {
        console.error('Mermaid render error:', err);
        // Clean up any error SVGs Mermaid injected into document.body
        document.querySelectorAll('[id^="dmermaid"], [id^="mermaid-"]').forEach((el) => {
          if (el.parentElement === document.body) el.remove();
        });
        if (isMounted) {
          setRenderError('Could not render architecture diagram graphically. Raw markup displayed below.');
        }
      }
    }

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chart, darkMode]);

  const handleCopy = () => {
    if (!chart) return;
    navigator.clipboard.writeText(chart);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-8 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <GitGraph className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Architecture & Module Flow
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Auto-generated component hierarchy and system interaction graph
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/50 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-medium text-slate-700 dark:text-slate-300 transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-500" />
              <span className="text-emerald-600 dark:text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy Mermaid</span>
            </>
          )}
        </button>
      </div>

      {renderError ? (
        <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 text-xs text-amber-700 dark:text-amber-300">
          <p className="mb-2 font-medium">{renderError}</p>
          <pre className="p-4 rounded-xl bg-slate-900 text-slate-100 font-mono text-[11px] overflow-x-auto">
            {chart}
          </pre>
        </div>
      ) : (
        <div
          ref={containerRef}
          className="overflow-x-auto py-6 px-4 rounded-2xl bg-slate-50/60 dark:bg-slate-950/60 border border-slate-100 dark:border-slate-800/60 flex items-center justify-center min-h-[260px]"
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      )}
    </div>
  );
}

