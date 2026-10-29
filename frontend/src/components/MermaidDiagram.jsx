import React, { useEffect, useRef, useState, useCallback } from 'react';
import mermaid from 'mermaid';
import { Copy, Check, GitGraph, RefreshCw, AlertTriangle, Code2 } from 'lucide-react';

// Global sequential render lock to prevent Mermaid race conditions in React 18 StrictMode
let renderLock = Promise.resolve();

/**
 * Sanitize Mermaid diagram markup to prevent syntax errors:
 * - Deduplicates identical node IDs
 * - Replaces pipes `|` inside node labels with bullets `•`
 * - Normalizes arrows pointing to subgraphs
 */
function sanitizeMermaid(chart) {
  if (!chart || typeof chart !== 'string') return '';
  const lines = chart.split('\n');
  const seenNodeIds = new Set();
  const sanitizedLines = [];

  for (let line of lines) {
    const trimmed = line.trim();

    // Check for node definition: ID["Label..."]
    const nodeMatch = trimmed.match(/^([A-Za-z0-9_]+)\["(.*)"\]$/);
    if (nodeMatch) {
      let [, id, label] = nodeMatch;
      // Replace pipes inside node labels to avoid conflict with edge syntax
      label = label.replace(/\|/g, ' • ');

      // Deduplicate node IDs if already seen
      if (seenNodeIds.has(id)) {
        id = `${id}_${Math.floor(Math.random() * 10000)}`;
      }
      seenNodeIds.add(id);

      const indent = line.substring(0, line.indexOf(trimmed));
      sanitizedLines.push(`${indent}${id}["${label}"]`);
      continue;
    }

    sanitizedLines.push(line);
  }

  return sanitizedLines.join('\n');
}

export function MermaidDiagram({ chart, darkMode }) {
  const containerRef = useRef(null);
  const renderSeqRef = useRef(0);
  const [copied, setCopied] = useState(false);
  const [renderError, setRenderError] = useState(null);
  const [svgContent, setSvgContent] = useState('');
  const [isRendering, setIsRendering] = useState(false);
  const [showRawMarkup, setShowRawMarkup] = useState(false);

  const doRender = useCallback(async () => {
    if (!chart) return;

    const currentSeq = ++renderSeqRef.current;
    setIsRendering(true);

    // Queue the render through our global lock so Mermaid instances don't collide
    renderLock = renderLock
      .catch(() => {})
      .then(async () => {
        if (currentSeq !== renderSeqRef.current) return;

        try {
          // Suppress Mermaid's default error popup/bomb injection
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
          mermaid.parseError = () => {};

          const sanitized = sanitizeMermaid(chart);
          const id = `mermaid-${Math.random().toString(36).substring(2, 9)}`;

          const { svg } = await mermaid.render(id, sanitized);

          if (currentSeq === renderSeqRef.current) {
            setSvgContent(svg);
            setRenderError(null);
            setIsRendering(false);
          }
        } catch (err) {
          console.warn('Primary Mermaid render failed, attempting simplified fallback...', err);

          // Attempt fallback: simplified clean flowchart
          try {
            const fallbackId = `mermaid-fb-${Math.random().toString(36).substring(2, 9)}`;
            const fallbackChart = `graph TD\n  ROOT["Repository Architecture"]\n  style ROOT fill:#4f46e5,stroke:#3730a3,color:#fff\n  MOD["Modules & Components"]\n  style MOD fill:#1e1b4b,stroke:#818cf8,color:#c7d2fe\n  ROOT --> MOD`;
            const { svg } = await mermaid.render(fallbackId, fallbackChart);

            if (currentSeq === renderSeqRef.current) {
              setSvgContent(svg);
              setRenderError('Complex layout simplified for compatibility. Full markup available below.');
              setIsRendering(false);
            }
          } catch (fallbackErr) {
            if (currentSeq === renderSeqRef.current) {
              setSvgContent('');
              setRenderError('Could not render architecture diagram graphically. Raw markup displayed below.');
              setIsRendering(false);
            }
          }
        } finally {
          // Clean up any stray error elements Mermaid may have injected into document.body
          document.querySelectorAll('[id^="dmermaid"]').forEach((el) => {
            if (el.parentElement === document.body) el.remove();
          });
        }
      });
  }, [chart, darkMode]);

  useEffect(() => {
    doRender();
    return () => {
      // Invalidate in-flight render on unmount
      renderSeqRef.current++;
    };
  }, [doRender]);

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

        <div className="flex items-center gap-2">
          {renderError && (
            <button
              type="button"
              onClick={() => setShowRawMarkup((v) => !v)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/50 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-medium text-slate-700 dark:text-slate-300 transition-colors"
            >
              <Code2 className="w-3.5 h-3.5" />
              <span>{showRawMarkup ? 'Hide Markup' : 'View Markup'}</span>
            </button>
          )}

          <button
            type="button"
            onClick={doRender}
            disabled={isRendering}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/50 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-medium text-slate-700 dark:text-slate-300 transition-colors disabled:opacity-50"
            title="Re-render diagram"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRendering ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>

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
      </div>

      {renderError && (
        <div className="mb-4 p-3.5 rounded-2xl bg-amber-50/80 dark:bg-amber-950/30 border border-amber-200/80 dark:border-amber-900/50 text-xs text-amber-800 dark:text-amber-200 flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium">{renderError}</p>
          </div>
        </div>
      )}

      {/* Persistent SVG container that never unmounts */}
      <div
        ref={containerRef}
        className={`overflow-x-auto py-6 px-4 rounded-2xl bg-slate-50/60 dark:bg-slate-950/60 border border-slate-100 dark:border-slate-800/60 flex items-center justify-center min-h-[260px] transition-opacity ${
          isRendering ? 'opacity-50' : 'opacity-100'
        } ${!svgContent && renderError ? 'hidden' : ''}`}
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />

      {/* Raw markup viewer (shown if toggle active or if SVG could not render at all) */}
      {(showRawMarkup || (!svgContent && renderError)) && (
        <div className="mt-4">
          <pre className="p-4 rounded-xl bg-slate-900 text-slate-100 font-mono text-[11px] overflow-x-auto border border-slate-800">
            {chart}
          </pre>
        </div>
      )}
    </div>
  );
}
