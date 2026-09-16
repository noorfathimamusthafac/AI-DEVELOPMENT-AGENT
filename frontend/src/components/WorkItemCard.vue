<template>
  <div class="work-card glass-panel" :class="{ 'is-resolved': isResolved }">
    <div class="card-glow"></div>
    
    <div class="card-header">
      <div class="header-left">
        <span class="ticket-id">{{ item.id }}</span>
        <span :class="['badge', item.type.toLowerCase() === 'bug' ? 'badge-bug' : 'badge-feature']">
          {{ item.type }}
        </span>
      </div>

      <div class="header-right">
        <span :class="getStatusBadgeClass(item.status)">
          <span class="dot-indicator"></span>
          {{ item.status }}
        </span>
      </div>
    </div>

    <div class="card-content">
      <h3 class="ticket-title">{{ item.subject }}</h3>
      <p class="ticket-description">{{ item.description }}</p>
    </div>

    <div class="card-footer">
      <div class="footer-meta">
        <span :class="['badge', item.priority.toLowerCase() === 'high' ? 'badge-priority-high' : 'badge-priority-normal']">
          Priority: {{ item.priority }}
        </span>
        <span v-if="item.comments && item.comments.length > 0" class="meta-comment">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          {{ item.comments.length }}
        </span>
      </div>

      <button
        :id="'btn-run-agent-' + item.id"
        class="btn btn-primary run-action-btn"
        :disabled="isRunning"
        @click="$emit('run-agent', item)"
      >
        <span v-if="isRunning" class="spinner"></span>
        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        <span>{{ isRunning ? 'Agent Running...' : 'Run Agent' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { WorkPackage } from '../services/api';

const props = defineProps<{
  item: WorkPackage;
  isRunning?: boolean;
}>();

defineEmits<{
  (e: 'run-agent', item: WorkPackage): void;
}>();

const isResolved = computed(() => {
  const s = props.item.status.toLowerCase();
  return s === 'resolved' || s === 'closed';
});

const getStatusBadgeClass = (status: string) => {
  const s = status.toLowerCase();
  if (s === 'new') return 'badge badge-status-new';
  if (s === 'in progress') return 'badge badge-status-progress';
  if (s === 'resolved' || s === 'closed') return 'badge badge-status-resolved';
  return 'badge';
};
</script>

<style scoped>
.work-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  background: var(--bg-glass);
  min-height: 220px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.work-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #38bdf8);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.work-card:hover {
  transform: translateY(-3px);
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: 0 12px 30px -4px rgba(0, 0, 0, 0.6), 0 0 20px rgba(99, 102, 241, 0.2);
  background: var(--bg-glass-hover);
}

.work-card:hover::before {
  opacity: 1;
}

.work-card.is-resolved {
  border-left: 3px solid var(--accent-emerald);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ticket-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent-cyan);
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.2);
  padding: 2px 7px;
  border-radius: var(--radius-xs);
}

.header-right {
  display: flex;
  align-items: center;
}

.dot-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  margin-right: 2px;
}

.card-content {
  flex: 1;
  margin-bottom: 16px;
}

.ticket-title {
  font-size: 1.02rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.ticket-description {
  font-size: 0.825rem;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-comment {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.run-action-btn {
  padding: 7px 15px;
  font-size: 0.82rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
}
</style>
