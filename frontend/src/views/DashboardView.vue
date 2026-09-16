<template>
  <div class="dashboard-page">
    <Navbar :currentUser="currentUser" />

    <main class="dashboard-main">
      <!-- Hero Command Banner -->
      <section class="hero-banner glass-panel fade-in">
        <div class="hero-content">
          <div class="hero-badge">
            <span class="sparkle-icon">✦</span>
            <span>Autonomous Software Engineering Assistant</span>
          </div>
          <h1 class="hero-title">OpenProject Work Board &bull; AI Dev Agent</h1>
          <p class="hero-desc">
            Picks up OpenProject tickets, inspects codebase, writes code patches, executes unit tests, commits to Git, and transitions ticket status automatically.
          </p>

          <!-- Quick KPI summary -->
          <div class="kpi-row">
            <div class="kpi-item">
              <span class="kpi-num">{{ workPackages.length }}</span>
              <span class="kpi-lbl">Work Packages</span>
            </div>
            <div class="kpi-divider"></div>
            <div class="kpi-item">
              <span class="kpi-num">{{ bugCount }}</span>
              <span class="kpi-lbl">Open Bugs</span>
            </div>
            <div class="kpi-divider"></div>
            <div class="kpi-item">
              <span class="kpi-num">{{ resolvedCount }}</span>
              <span class="kpi-lbl">Resolved</span>
            </div>
            <div class="kpi-divider"></div>
            <div class="kpi-item">
              <span class="kpi-num accent-text">100%</span>
              <span class="kpi-lbl">Pytest Pass Rate</span>
            </div>
          </div>
        </div>

        <!-- Quick Demo Trigger Actions -->
        <div class="hero-actions">
          <button
            id="btn-quick-demo"
            class="btn btn-primary demo-launch-btn"
            :disabled="runningTicketId !== null"
            @click="triggerQuickDemo"
            title="Launch live agent demonstration on BUG-101"
          >
            <span v-if="runningTicketId" class="spinner"></span>
            <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            <span>{{ runningTicketId ? 'Agent Running...' : '⚡ Quick Demo: Auto-Run BUG-101' }}</span>
          </button>

          <div class="action-subgroup">
            <button
              id="btn-inspect-diff"
              class="btn btn-secondary"
              @click="openDiffModal"
              title="Inspect recent Git diff"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="18" cy="18" r="3"></circle>
                <circle cx="6" cy="6" r="3"></circle>
                <path d="M13 6h3a2 2 0 0 1 2 2v7"></path>
                <line x1="6" y1="9" x2="6" y2="21"></line>
              </svg>
              <span>Inspect Git Diff</span>
            </button>

            <button
              id="btn-reset-demo"
              class="btn btn-secondary"
              :disabled="resettingDemo"
              @click="handleResetDemo"
              title="Revert test repository to buggy state"
            >
              <span v-if="resettingDemo" class="spinner"></span>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
                <path d="M21 3v5h-5"></path>
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
                <path d="M3 21v-5h5"></path>
              </svg>
              <span>Reset Demo State</span>
            </button>
          </div>
        </div>
      </section>

      <!-- Work Board Filter & Search Bar -->
      <section class="board-controls">
        <div class="filter-pills">
          <button
            class="pill-btn"
            :class="{ active: filterType === 'all' }"
            @click="filterType = 'all'"
          >
            All Tickets ({{ workPackages.length }})
          </button>
          <button
            class="pill-btn"
            :class="{ active: filterType === 'bug' }"
            @click="filterType = 'bug'"
          >
            Bugs ({{ bugCount }})
          </button>
          <button
            class="pill-btn"
            :class="{ active: filterType === 'feature' }"
            @click="filterType = 'feature'"
          >
            Features ({{ featureCount }})
          </button>
        </div>

        <div class="search-wrapper">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Filter by title, ID or keyword..."
            class="search-field"
          />
        </div>
      </section>

      <!-- Work Packages Grid -->
      <section class="work-grid">
        <div v-if="loadingPackages" class="grid-placeholder glass-panel">
          <span class="spinner"></span>
          <p>Syncing with OpenProject API...</p>
        </div>

        <div v-else-if="filteredPackages.length === 0" class="grid-placeholder glass-panel">
          <p>No tickets match the selected criteria.</p>
        </div>

        <WorkItemCard
          v-for="item in filteredPackages"
          :key="item.id"
          :item="item"
          :isRunning="runningTicketId === item.id"
          @run-agent="handleRunAgent"
        />
      </section>

      <!-- History & Commit Log -->
      <section class="history-panel glass-panel">
        <div class="panel-header">
          <div class="header-tag">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <h3 class="panel-title">Autonomous Execution & Git Commit History</h3>
          </div>
          <button class="btn btn-secondary btn-sm" @click="fetchRuns">Refresh History</button>
        </div>

        <div class="table-container">
          <table class="runs-table">
            <thead>
              <tr>
                <th>Run</th>
                <th>Work Item</th>
                <th>Type</th>
                <th>Status</th>
                <th>Git Branch</th>
                <th>Commit</th>
                <th>Time</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="runs.length === 0">
                <td colspan="8" class="empty-table-msg">No agent executions recorded yet. Click "Run Agent" on BUG-101 above to execute.</td>
              </tr>
              <tr v-for="r in runs" :key="r.id">
                <td class="font-mono">#{{ r.id }}</td>
                <td>
                  <strong>{{ r.ticket_id }}</strong>: {{ r.ticket_title }}
                </td>
                <td>
                  <span :class="['badge', r.ticket_type.toLowerCase() === 'bug' ? 'badge-bug' : 'badge-feature']">
                    {{ r.ticket_type }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', r.status === 'completed' ? 'badge-status-resolved' : r.status === 'running' ? 'badge-status-progress' : 'badge-bug']">
                    {{ r.status }}
                  </span>
                </td>
                <td class="font-mono">{{ r.branch_name || '—' }}</td>
                <td class="font-mono">
                  <span v-if="r.commit_hash" class="hash-chip">{{ r.commit_hash }}</span>
                  <span v-else>—</span>
                </td>
                <td>{{ formatDate(r.created_at) }}</td>
                <td>
                  <button class="btn btn-secondary btn-xs" @click="viewRunLogs(r.id)">
                    View Logs
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <!-- Execution Modal -->
    <AgentExecutionModal
      v-if="showModal && activeRunId"
      :ticketId="modalTicketId"
      :ticketTitle="modalTicketTitle"
      :runId="activeRunId"
      :isRunning="runningTicketId === modalTicketId"
      :initialLogs="modalInitialLogs"
      @close="closeModal"
      @finished="onRunFinished"
    />

    <!-- Git Diff Modal -->
    <div v-if="showDiffModal" class="modal-backdrop" @click.self="showDiffModal = false">
      <div class="modal-dialog glass-panel fade-in" style="max-width: 860px;">
        <div class="modal-header">
          <h2 class="modal-title">Target Repository &bull; Git Diff Viewer</h2>
          <button class="btn-close" @click="showDiffModal = false">&times;</button>
        </div>
        <div class="modal-body" style="grid-template-columns: 1fr;">
          <div class="terminal-block" style="height: 400px;">
            <pre v-if="gitDiffText">{{ gitDiffText }}</pre>
            <p v-else class="text-secondary">No uncommitted changes found. Everything is committed on target branch.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDiffModal = false">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Navbar from '../components/Navbar.vue';
import WorkItemCard from '../components/WorkItemCard.vue';
import AgentExecutionModal from '../components/AgentExecutionModal.vue';
import { api, type User, type WorkPackage, type AgentRun, type AgentLog } from '../services/api';

const router = useRouter();

const currentUser = ref<User | null>(null);
const workPackages = ref<WorkPackage[]>([]);
const runs = ref<AgentRun[]>([]);
const loadingPackages = ref(false);
const filterType = ref<'all' | 'bug' | 'feature'>('all');
const searchQuery = ref('');

// Execution state
const runningTicketId = ref<string | null>(null);
const showModal = ref(false);
const activeRunId = ref<number | null>(null);
const modalTicketId = ref('');
const modalTicketTitle = ref('');
const modalInitialLogs = ref<AgentLog[]>([]);

// Diff modal
const showDiffModal = ref(false);
const gitDiffText = ref('');
const resettingDemo = ref(false);

const bugCount = computed(() => workPackages.value.filter(p => p.type.toLowerCase() === 'bug').length);
const featureCount = computed(() => workPackages.value.filter(p => p.type.toLowerCase() === 'feature').length);
const resolvedCount = computed(() => workPackages.value.filter(p => p.status.toLowerCase() === 'resolved').length);

const filteredPackages = computed(() => {
  return workPackages.value.filter(item => {
    const matchesType = filterType.value === 'all' || item.type.toLowerCase() === filterType.value;
    const q = searchQuery.value.toLowerCase().trim();
    const matchesSearch = !q || item.id.toLowerCase().includes(q) || item.subject.toLowerCase().includes(q) || item.description.toLowerCase().includes(q);
    return matchesType && matchesSearch;
  });
});

const fetchCurrentUser = async () => {
  try {
    currentUser.value = await api.getMe();
  } catch {
    router.push('/login');
  }
};

const fetchPackages = async () => {
  loadingPackages.value = true;
  try {
    workPackages.value = await api.getWorkPackages();
  } catch (err) {
    console.error('Failed to fetch work packages', err);
  } finally {
    loadingPackages.value = false;
  }
};

const fetchRuns = async () => {
  try {
    runs.value = await api.getRuns();
  } catch (err) {
    console.error('Failed to fetch runs', err);
  }
};

const handleRunAgent = async (item: WorkPackage) => {
  runningTicketId.value = item.id;
  modalTicketId.value = item.id;
  modalTicketTitle.value = item.subject;
  modalInitialLogs.value = [];

  try {
    const res = await api.runAgent(item.id);
    activeRunId.value = res.run_id;
    showModal.value = true;
  } catch (err: any) {
    alert(err.message || 'Failed to start agent');
    runningTicketId.value = null;
  }
};

const triggerQuickDemo = async () => {
  const bugItem = workPackages.value.find(p => p.id === 'BUG-101') || workPackages.value[0];
  if (bugItem) {
    // If already resolved, reset first for a pristine demo experience
    if (bugItem.status.toLowerCase() === 'resolved') {
      await api.resetDemo();
      await fetchPackages();
    }
    const freshBug = workPackages.value.find(p => p.id === 'BUG-101') || bugItem;
    await handleRunAgent(freshBug);
  }
};

const onRunFinished = async () => {
  runningTicketId.value = null;
  await fetchPackages();
  await fetchRuns();
};

const closeModal = () => {
  showModal.value = false;
  runningTicketId.value = null;
};

const viewRunLogs = async (runId: number) => {
  try {
    const run = await api.getRun(runId);
    activeRunId.value = run.id;
    modalTicketId.value = run.ticket_id;
    modalTicketTitle.value = run.ticket_title;
    modalInitialLogs.value = run.logs || [];
    showModal.value = true;
  } catch (err: any) {
    alert('Failed to load run details');
  }
};

const openDiffModal = async () => {
  try {
    const res = await api.getGitDiff();
    gitDiffText.value = res.diff || 'No recent diffs found.';
    showDiffModal.value = true;
  } catch {
    gitDiffText.value = 'Failed to load git diff.';
    showDiffModal.value = true;
  }
};

const handleResetDemo = async () => {
  resettingDemo.value = true;
  try {
    const res = await api.resetDemo();
    alert(res.message || 'Demo reset successfully!');
    await fetchPackages();
    await fetchRuns();
  } catch (err: any) {
    alert(err.message || 'Reset failed');
  } finally {
    resettingDemo.value = false;
  }
};

const formatDate = (isoStr?: string) => {
  if (!isoStr) return '—';
  try {
    const d = new Date(isoStr);
    return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch {
    return isoStr;
  }
};

onMounted(async () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    router.push('/login');
    return;
  }
  await fetchCurrentUser();
  await fetchPackages();
  await fetchRuns();
});
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.dashboard-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 28px 24px 64px 24px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* Hero Command Banner */
.hero-banner {
  padding: 28px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
  background: linear-gradient(180deg, rgba(22, 27, 34, 0.8) 0%, rgba(13, 17, 23, 0.95) 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--accent-cyan);
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.2);
  padding: 3px 10px;
  border-radius: 9999px;
  margin-bottom: 10px;
}

.sparkle-icon {
  font-size: 0.85rem;
}

.hero-title {
  font-size: 1.65rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.hero-desc {
  font-size: 0.88rem;
  color: var(--text-secondary);
  max-width: 600px;
  line-height: 1.55;
  margin-bottom: 18px;
}

.kpi-row {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  background: rgba(13, 17, 23, 0.7);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 8px 16px;
}

.kpi-item {
  display: flex;
  flex-direction: column;
}

.kpi-num {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
}

.kpi-lbl {
  font-size: 0.68rem;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 600;
}

.accent-text {
  color: var(--accent-emerald);
}

.kpi-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.08);
}

.hero-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 280px;
}

.demo-launch-btn {
  padding: 12px 20px;
  font-size: 0.92rem;
  font-weight: 700;
  border-radius: var(--radius-sm);
}

.action-subgroup {
  display: flex;
  gap: 8px;
}

.action-subgroup .btn {
  flex: 1;
  font-size: 0.78rem;
  padding: 8px 12px;
}

/* Board Controls */
.board-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-pills {
  display: flex;
  gap: 6px;
  background: rgba(22, 27, 34, 0.6);
  padding: 3px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.pill-btn {
  background: none;
  border: none;
  padding: 6px 14px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  border-radius: var(--radius-xs);
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn.active {
  background: var(--bg-elevated);
  color: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.search-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(22, 27, 34, 0.6);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 7px 12px;
  width: 100%;
  max-width: 320px;
  color: var(--text-muted);
}

.search-field {
  background: none;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 0.82rem;
  width: 100%;
}

/* Grid */
.work-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.grid-placeholder {
  grid-column: 1 / -1;
  padding: 40px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
}

/* History Panel */
.history-panel {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
}

.panel-title {
  font-size: 1.05rem;
  font-weight: 700;
}

.table-container {
  overflow-x: auto;
}

.runs-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.82rem;
}

.runs-table th {
  padding: 10px 14px;
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-subtle);
}

.runs-table td {
  padding: 12px 14px;
  color: var(--text-primary);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.runs-table tr:hover td {
  background: rgba(255, 255, 255, 0.015);
}

.hash-chip {
  background: rgba(99, 102, 241, 0.12);
  color: #c7d2fe;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.font-mono {
  font-family: 'JetBrains Mono', monospace;
}

.btn-xs {
  padding: 4px 10px;
  font-size: 0.75rem;
}

.empty-table-msg {
  text-align: center;
  color: var(--text-muted);
  padding: 24px;
}
</style>
