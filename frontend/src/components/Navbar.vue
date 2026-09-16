<template>
  <header class="navbar-wrapper">
    <div class="nav-container">
      <div class="nav-brand">
        <div class="brand-logo">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
          </svg>
        </div>
        <div class="brand-meta">
          <span class="brand-title">DevAgent</span>
          <span class="brand-sub">OpenProject Integration</span>
        </div>
      </div>

      <div class="nav-status-group">
        <div class="status-pill status-connected">
          <span class="pulse-dot"></span>
          <span class="pill-text">OpenProject: <strong>Connected</strong></span>
        </div>
        <div class="status-pill repo-pill">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="18" cy="18" r="3"></circle>
            <circle cx="6" cy="6" r="3"></circle>
            <path d="M13 6h3a2 2 0 0 1 2 2v7"></path>
            <line x1="6" y1="9" x2="6" y2="21"></line>
          </svg>
          <span class="pill-text">Repo: <code>test-repository</code></span>
        </div>
      </div>

      <div class="nav-user-area" v-if="currentUser">
        <div class="user-badge">
          <div class="user-avatar">
            {{ currentUser.full_name ? currentUser.full_name.charAt(0).toUpperCase() : 'D' }}
          </div>
          <div class="user-meta">
            <span class="user-name">{{ currentUser.full_name || currentUser.email }}</span>
            <span class="user-role-tag" :class="'role-' + currentUser.role">{{ currentUser.role }}</span>
          </div>
        </div>

        <button id="btn-logout" class="btn btn-secondary btn-icon" @click="handleLogout" title="Sign out">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import type { User } from '../services/api';

const props = defineProps<{
  currentUser: User | null;
}>();

const router = useRouter();

const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_info');
  router.push('/login');
};
</script>

<style scoped>
.navbar-wrapper {
  background: rgba(9, 12, 16, 0.82);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  z-index: 40;
  padding: 10px 24px;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-logo {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: linear-gradient(135deg, #6366f1, #38bdf8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.brand-meta {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #ffffff;
  line-height: 1.15;
}

.brand-sub {
  font-size: 0.68rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.nav-status-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 0.76rem;
  font-weight: 500;
  border: 1px solid var(--border-subtle);
  background: rgba(22, 27, 34, 0.6);
}

.status-connected {
  border-color: rgba(16, 185, 129, 0.25);
  background: rgba(16, 185, 129, 0.08);
  color: #34d399;
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.repo-pill {
  color: var(--text-secondary);
}

.repo-pill code {
  color: var(--accent-cyan);
  font-family: 'JetBrains Mono', monospace;
  font-weight: 500;
}

.nav-user-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 10px 3px 5px;
  border-radius: 9999px;
  background: rgba(22, 27, 34, 0.6);
  border: 1px solid var(--border-subtle);
}

.user-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #0284c7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
}

.user-meta {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.1;
}

.user-role-tag {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
}

.role-developer {
  color: var(--accent-cyan);
}

.role-admin {
  color: var(--accent-purple);
}

.btn-icon {
  padding: 6px;
  border-radius: 8px;
  color: var(--text-secondary);
}

.btn-icon:hover {
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .nav-status-group {
    display: none;
  }
}
</style>
