const BASE = '/api';

async function request(path, options = {}) {
  const token = localStorage.getItem('cs_token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Auth
  login: (username, password) => request('/auth/login', {
    method: 'POST', body: JSON.stringify({ username, password })
  }),
  register: (username, password, role = 'user') => request('/auth/register', {
    method: 'POST', body: JSON.stringify({ username, password, role })
  }),
  getMe: () => request('/auth/me'),

  // Core
  analyze: (input, sourceIp = '127.0.0.1', userId = 'dashboard_user') => request('/analyze', {
    method: 'POST',
    body: JSON.stringify({ input, source_ip: sourceIp, user_id: userId })
  }),
  getDashboard: () => request('/dashboard'),
  getAgents: () => request('/agents'),
  getAgent: (name) => request(`/agents/${name}`),
  getThreats: () => request('/threats'),
  getStats: () => request('/stats'),

  // Red Team
  runSimulation: (type = 'full') => request('/redteam/simulate', {
    method: 'POST', body: JSON.stringify({ simulation_type: type })
  }),
  getRedTeamHistory: () => request('/redteam/history'),
};
