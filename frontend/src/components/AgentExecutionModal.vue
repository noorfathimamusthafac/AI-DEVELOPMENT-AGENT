<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-dialog glass-panel fade-in" :class="{ 'pulse-active': isRunning }">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-main">
          <div class="agent-avatar" :class="{ 'avatar-running': isRunning, 'avatar-success': isFinished && !hasError, 'avatar-error': hasError }">
            <svg v-if="isRunning" class="spin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
            </svg>
            <svg v-else-if="isFinished && !hasError" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </div>
          <div>
            <div class="ticket-ref">
              <span class="ref-id">{{ ticketId }}</span>
              <span class="ref-title">{{ ticketTitle }}</span>
            </div>
            <h2 class="modal-title">AI Development Agent &bull; Autonomous Orchestrator</h2>
          </div>
        </div>

        <button id="btn-close-modal" class="btn-close" @click="$emit('close')" title="Close">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- Modal Content -->
      <div class="modal-body">
        <!-- Vertical Stepper Timeline -->
        <div class="stepper-col">
          <div class="stepper-header">
            <span class="stepper-title">Execution Workflow</span>
            <span class="progress-pill">{{ completedCount }} / {{ steps.length }}</span>
          </div>

          <div class="timeline-container">
            <div
              v-for="(step, idx) in steps"
              :key="step.name"
              class="timeline-item"
              :class="getStepClass(step.name)"
            >
              <div class="timeline-axis">
                <div class="timeline-node">
                  <svg v-if="getStepStatus(step.name) === 'success'" class="check-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <span v-else-if="getStepStatus(step.name) === 'running'" class="node-spinner"></span>
                  <span v-else-if="getStepStatus(step.name) === 'failed'" class="node-cross">✕</span>
                  <span v-else class="node-idx">{{ idx + 1 }}</span>
                </div>
                <div v-if="idx < steps.length - 1" class="timeline-connector"></div>
              </div>

              <div class="timeline-details">
                <span class="step-name">{{ step.name }}</span>
                <span v-if="getStepMessage(step.name)" class="step-hint">{{ getStepMessage(step.name) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Terminal Stream -->
        <div class="terminal-col">
          <div class="terminal-bar">
            <div class="window-controls">
              <span class="win-dot red"></span>
              <span class="win-dot yellow"></span>
              <span class="win-dot green"></span>
            </div>
            <div class="terminal-meta">
              <span class="stream-badge" :class="{ 'is-live': isRunning }">
                <span class="live-pulse"></span>
                {{ isRunning ? 'STREAMING' : 'COMPLETED' }}
              </span>
              <span v-if="branchName" class="branch-pill">
                <code>{{ branchName }}</code>
              </span>
            </div>
          </div>

          <div class="terminal-viewport" ref="terminalContainer">
            <div v-for="(log, idx) in activityLogs" :key="idx" class="log-row" :class="'log-' + log.status">
              <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              <span class="log-status">[{{ log.status.toUpperCase() }}]</span>
              <span class="log-step">&lt;{{ log.step }}&gt;</span>
              <span class="log-msg">{{ log.message }}</span>
              <pre v-if="log.details" class="log-snippet">{{ log.details }}</pre>
            </div>
            <div v-if="isRunning" class="log-prompt">
              <span class="cursor-caret">&gt;</span> Running MCP tools and code inspection...
              <span class="blink-cursor">_</span>
            </div>
          </div>

          <!-- Completion Banner -->
          <div v-if="isFinished && !hasError" class="result-banner fade-in">
            <div class="result-grid">
              <div class="result-item">
                <span class="item-label">Git Branch</span>
                <div class="item-value-box">
                  <code>{{ branchName || 'N/A' }}</code>
                  <button class="copy-btn" @click="copyText(branchName)" title="Copy branch">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <div class="result-item">
                <span class="item-label">Commit Hash</span>
                <div class="item-value-box">
                  <span class="commit-badge">{{ commitHash || 'N/A' }}</span>
                  <button class="copy-btn" @click="copyText(commitHash)" title="Copy hash">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <div class="result-item">
                <span class="item-label">OpenProject Status</span>
                <div>
                  <span class="badge badge-status-resolved">✓ Status: Resolved</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button v-if="isFinished" id="btn-done-execution" class="btn btn-primary" @click="$emit('close')">
          Return to Board
        </button>
        <button v-else id="btn-cancel-execution" class="btn btn-secondary" @click="$emit('close')">
          Keep Running in Background
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';
import type { AgentLog } from '../services/api';

const props = defineProps<{
  ticketId: string;
  ticketTitle: string;
  runId: number;
  isRunning: boolean;
  initialLogs?: AgentLog[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'finished'): void;
}>();

const terminalContainer = ref<HTMLElement | null>(null);

const steps = [
  { name: 'Work item retrieved' },
  { name: 'Requirement analyzed' },
  { name: 'Repository analyzed' },
  { name: 'Relevant files identified' },
  { name: 'Code modified' },
  { name: 'Tests executed' },
  { name: 'Tests passed' },
  { name: 'Git branch created' },
  { name: 'Changes committed' },
  { name: 'OpenProject updated' }
];

const activityLogs = ref<AgentLog[]>(props.initialLogs ? [...props.initialLogs] : []);
const branchName = ref<string>('');
const commitHash = ref<string>('');
const isFinished = ref<boolean>(false);
const hasError = ref<boolean>(false);

let eventSource: EventSource | null = null;

const completedCount = computed(() => {
  return steps.filter(s => getStepStatus(s.name) === 'success').length;
});

const getStepStatus = (stepName: string) => {
  const matchingLogs = activityLogs.value.filter(l => l.step === stepName);
  if (!matchingLogs.length) return 'pending';
  const last = matchingLogs[matchingLogs.length - 1];
  return last.status;
};

const getStepMessage = (stepName: string) => {
  const matchingLogs = activityLogs.value.filter(l => l.step === stepName);
  if (!matchingLogs.length) return '';
  const last = matchingLogs[matchingLogs.length - 1];
  return last.status === 'running' ? last.message : '';
};

const getStepClass = (stepName: string) => {
  const s = getStepStatus(stepName);
  if (s === 'success') return 'is-success';
  if (s === 'running') return 'is-running';
  if (s === 'failed') return 'is-failed';
  return 'is-pending';
};

const formatTime = (ts?: string) => {
  if (!ts) return new Date().toLocaleTimeString();
  try {
    return new Date(ts).toLocaleTimeString();
  } catch {
    return ts;
  }
};

const copyText = (txt: string) => {
  if (txt) {
    navigator.clipboard.writeText(txt);
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (terminalContainer.value) {
    terminalContainer.value.scrollTop = terminalContainer.value.scrollHeight;
  }
};

watch(() => activityLogs.value.length, () => {
  scrollToBottom();
});

onMounted(() => {
  const streamUrl = `http://localhost:8000/api/agent/stream/${props.runId}`;
  eventSource = new EventSource(streamUrl);

  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (data.type === 'step_update') {
        activityLogs.value.push({
          id: Date.now(),
          step: data.step,
          status: data.status,
          message: data.message,
          details: data.details,
          timestamp: data.timestamp
        });
      } else if (data.type === 'completed') {
        isFinished.value = true;
        branchName.value = data.branch_name;
        commitHash.value = data.commit_hash;
        emit('finished');
        if (eventSource) eventSource.close();
      } else if (data.type === 'failed') {
        isFinished.value = true;
        hasError.value = true;
        emit('finished');
        if (eventSource) eventSource.close();
      }
    } catch (err) {
      console.error('Failed to parse SSE event', err);
    }
  };

  eventSource.onerror = () => {
    if (eventSource) {
      eventSource.close();
    }
  };
});

onUnmounted(() => {
  if (eventSource) {
    eventSource.close();
  }
});
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 6, 11, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.modal-dialog {
  width: 100%;
  max-width: 1100px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  background: #0d1117;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.8), 0 0 35px rgba(99, 102, 241, 0.2);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.modal-header {
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 14px;
}

.agent-avatar {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: var(--accent-indigo);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-running {
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
}

.avatar-success {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.3);
  color: #34d399;
}

.avatar-error {
  background: rgba(244, 63, 94, 0.12);
  border-color: rgba(244, 63, 94, 0.3);
  color: #fb7185;
}

.spin-icon {
  width: 22px;
  height: 22px;
  animation: spin 0.8s linear infinite;
}

.ticket-ref {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.ref-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--accent-cyan);
}

.ref-title {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.modal-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.modal-body {
  padding: 22px 24px;
  display: grid;
  grid-template-columns: 310px 1fr;
  gap: 20px;
  overflow-y: auto;
  flex: 1;
}

/* Timeline Stepper */
.stepper-col {
  background: rgba(22, 27, 34, 0.5);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.stepper-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.stepper-title {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-secondary);
}

.progress-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  padding: 2px 7px;
  background: rgba(99, 102, 241, 0.15);
  color: #c7d2fe;
  border-radius: 9999px;
  font-weight: 600;
}

.timeline-container {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  align-items: stretch;
  gap: 12px;
  position: relative;
}

.timeline-axis {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 22px;
}

.timeline-node {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(33, 38, 45, 0.8);
  border: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  z-index: 2;
  transition: all 0.3s ease;
}

.timeline-connector {
  flex: 1;
  width: 2px;
  background: rgba(255, 255, 255, 0.08);
  min-height: 18px;
  margin: 2px 0;
  transition: background 0.3s ease;
}

.timeline-details {
  display: flex;
  flex-direction: column;
  padding-bottom: 16px;
}

.step-name {
  font-size: 0.825rem;
  font-weight: 500;
  color: var(--text-secondary);
  line-height: 1.3;
}

.step-hint {
  font-size: 0.72rem;
  color: var(--accent-cyan);
  margin-top: 2px;
  line-height: 1.3;
}

/* Timeline State Modifiers */
.timeline-item.is-success .timeline-node {
  background: #10b981;
  border-color: #10b981;
  color: #ffffff;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
}

.timeline-item.is-success .timeline-connector {
  background: #10b981;
}

.timeline-item.is-success .step-name {
  color: #ffffff;
  font-weight: 600;
}

.timeline-item.is-running .timeline-node {
  background: var(--accent-indigo);
  border-color: var(--accent-cyan);
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.6);
}

.timeline-item.is-running .step-name {
  color: #ffffff;
  font-weight: 700;
}

.timeline-item.is-failed .timeline-node {
  background: #ef4444;
  border-color: #ef4444;
  color: #ffffff;
}

.check-svg {
  width: 12px;
  height: 12px;
}

.node-spinner {
  width: 10px;
  height: 10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #ffffff;
  animation: spin 0.75s linear infinite;
}

/* Terminal Column */
.terminal-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.terminal-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #06090f;
  padding: 10px 14px;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-bottom: none;
}

.window-controls {
  display: flex;
  gap: 6px;
}

.win-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}
.win-dot.red { background: #ff5f56; }
.win-dot.yellow { background: #ffbd2e; }
.win-dot.green { background: #27c93f; }

.terminal-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stream-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
}

.stream-badge.is-live {
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
}

.live-pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 6px currentColor;
}

.branch-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: #c7d2fe;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  padding: 2px 8px;
  border-radius: 4px;
}

.terminal-viewport {
  height: 360px;
  background: #06090f;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  padding: 14px;
  overflow-y: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  line-height: 1.6;
}

.log-row {
  margin-bottom: 5px;
  word-break: break-all;
}

.log-time {
  color: #484f58;
  margin-right: 6px;
}

.log-status {
  color: var(--accent-cyan);
  margin-right: 6px;
  font-weight: 600;
}

.log-step {
  color: #a5b4fc;
  margin-right: 8px;
}

.log-success .log-status { color: #34d399; }
.log-failed .log-status { color: #f87171; }
.log-running .log-status { color: #fcd34d; }

.log-snippet {
  background: rgba(0, 0, 0, 0.4);
  border-left: 2px solid var(--accent-indigo);
  padding: 8px 12px;
  margin: 6px 0;
  border-radius: 4px;
  color: #8b949e;
  font-size: 0.75rem;
  white-space: pre-wrap;
}

.log-prompt {
  color: var(--accent-cyan);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.cursor-caret {
  font-weight: 700;
}

.blink-cursor {
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

/* Result Banner */
.result-banner {
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-label {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 600;
}

.item-value-box {
  display: flex;
  align-items: center;
  gap: 6px;
}

.item-value-box code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: #ffffff;
}

.commit-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: #a5b4fc;
  background: rgba(99, 102, 241, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
}

.copy-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
}

.copy-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.modal-footer {
  padding: 14px 24px;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 800px) {
  .modal-body {
    grid-template-columns: 1fr;
  }
}
</style>
