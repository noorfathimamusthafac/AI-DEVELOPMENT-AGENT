export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: 'developer' | 'admin';
}

export interface WorkPackage {
  id: string;
  subject: string;
  type: 'Bug' | 'Feature';
  status: string;
  priority: string;
  description: string;
  lock_version?: number;
  comments?: Array<{ author: string; comment: string }>;
}

export interface AgentLog {
  id: number;
  step: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  message: string;
  details?: string;
  timestamp?: string;
}

export interface AgentRun {
  id: number;
  ticket_id: string;
  ticket_title: string;
  ticket_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  branch_name?: string;
  commit_hash?: string;
  summary?: string;
  test_output?: string;
  created_at?: string;
  finished_at?: string;
  logs?: AgentLog[];
}

const API_BASE = 'http://localhost:8000/api';

function getHeaders(): HeadersInit {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  // Auth
  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  async register(email: string, password: string, full_name: string, role: string) {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name, role }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to get current user');
    return res.json();
  },

  // OpenProject
  async getWorkPackages(): Promise<WorkPackage[]> {
    const res = await fetch(`${API_BASE}/openproject/work_packages`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch work packages');
    return res.json();
  },

  async getWorkPackage(ticketId: string): Promise<WorkPackage> {
    const res = await fetch(`${API_BASE}/openproject/work_packages/${ticketId}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to fetch work package ${ticketId}`);
    return res.json();
  },

  // Agent
  async runAgent(ticketId: string): Promise<{ success: boolean; run_id: number; ticket_id: string; status: string }> {
    const res = await fetch(`${API_BASE}/agent/run/${ticketId}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to trigger agent');
    return res.json();
  },

  async getRuns(): Promise<AgentRun[]> {
    const res = await fetch(`${API_BASE}/agent/runs`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch agent runs');
    return res.json();
  },

  async getRun(runId: number): Promise<AgentRun> {
    const res = await fetch(`${API_BASE}/agent/runs/${runId}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to fetch run ${runId}`);
    return res.json();
  },

  async getGitDiff(): Promise<{ success: boolean; diff?: string; error?: string }> {
    const res = await fetch(`${API_BASE}/agent/diff`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch git diff');
    return res.json();
  },

  async resetDemo(): Promise<{ success: boolean; message?: string }> {
    const res = await fetch(`${API_BASE}/agent/reset_demo`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to reset demo');
    return res.json();
  },
};
