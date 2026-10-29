import { useState, useCallback } from 'react';
import { analyzeRepository, getReportById } from '../utils/api';

/**
 * Custom React hook for orchestrating repository analysis.
 */
export function useAnalyze() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyze = useCallback(async (repoUrl) => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeRepository(repoUrl);
      setReport(data);
      // Update browser URL query param without full reload
      if (typeof window !== 'undefined' && window.history) {
        const url = new URL(window.location.href);
        url.searchParams.set('report_id', data.report_id);
        window.history.pushState({}, '', url.toString());
      }
      return data;
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const loadReport = useCallback(async (reportId) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getReportById(reportId);
      setReport(data);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to load report.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setReport(null);
    setError(null);
    if (typeof window !== 'undefined' && window.history) {
      const url = new URL(window.location.href);
      url.searchParams.delete('report_id');
      window.history.pushState({}, '', url.pathname);
    }
  }, []);

  return {
    report,
    loading,
    error,
    analyze,
    loadReport,
    reset,
  };
}

