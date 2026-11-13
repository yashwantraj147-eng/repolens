/**
 * API client for interacting with the RepoLens backend.
 */

const API_BASE = import.meta.env.VITE_API_BASE || '';

export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Trigger analysis of a GitHub repository.
 * @param {string} repoUrl
 * @param {boolean} forceRefresh - Bypass server cache and force fresh analysis
 * @returns {Promise<object>} AnalysisReport
 */
export async function analyzeRepository(repoUrl, forceRefresh = false) {
  try {
    const response = await fetch(`${API_BASE}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ repo_url: repoUrl, force_refresh: forceRefresh }),
    });

    const data = await response.json();

    if (!response.ok) {
      let message = data.detail || 'Failed to analyze repository';
      if (Array.isArray(data.detail)) {
        message = data.detail.map((err) => err.msg || JSON.stringify(err)).join(', ');
      }
      throw new ApiError(message, response.status, data);
    }

    return data;
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      err.message === 'Failed to fetch'
        ? 'Cannot connect to backend server. Make sure it is running on port 8000.'
        : err.message,
      0
    );
  }
}

/**
 * Fetch recently analyzed repositories for the landing page showcase.
 * @param {number} limit
 * @returns {Promise<Array>}
 */
export async function getRecentReports(limit = 6) {
  try {
    const response = await fetch(`${API_BASE}/api/reports/recent?limit=${limit}`);
    if (!response.ok) return [];
    return await response.json();
  } catch {
    return [];
  }
}

/**
 * Fetch a previously cached report by ID.
 * @param {string} reportId
 * @returns {Promise<object>}
 */
export async function getReportById(reportId) {
  try {
    const response = await fetch(`${API_BASE}/api/reports/${encodeURIComponent(reportId)}`);
    const data = await response.json();

    if (!response.ok) {
      throw new ApiError(data.detail || 'Report not found', response.status, data);
    }

    return data;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(err.message, 0);
  }
}

/**
 * Check backend health status.
 */
export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}

