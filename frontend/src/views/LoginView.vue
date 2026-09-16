<template>
  <div class="auth-page">
    <div class="auth-card glass-panel">
      <div class="auth-header">
        <div class="brand-badge-logo">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
        <h1 class="auth-title">Welcome Back</h1>
        <p class="auth-desc">Sign in to orchestrate OpenProject AI development workflows</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div v-if="errorMessage" class="alert-box error">
          {{ errorMessage }}
        </div>

        <div class="form-group">
          <label for="input-email">Work Email</label>
          <input
            id="input-email"
            type="email"
            v-model="email"
            placeholder="developer@example.com"
            required
            class="form-control"
          />
        </div>

        <div class="form-group">
          <label for="input-password">Password</label>
          <input
            id="input-password"
            type="password"
            v-model="password"
            placeholder="••••••••"
            required
            class="form-control"
          />
        </div>

        <button id="btn-login-submit" type="submit" class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span>{{ loading ? 'Authenticating...' : 'Sign In to Dashboard' }}</span>
        </button>

        <div class="quick-fill-section">
          <span class="quick-fill-label">Quick Demo Access:</span>
          <div class="quick-fill-buttons">
            <button
              id="btn-fill-dev"
              type="button"
              class="btn-demo"
              @click="quickFill('dev@example.com', 'password123')"
            >
              Developer (dev@example.com)
            </button>
            <button
              id="btn-fill-admin"
              type="button"
              class="btn-demo"
              @click="quickFill('admin@example.com', 'admin123')"
            >
              Lead Admin (admin@example.com)
            </button>
          </div>
        </div>

        <div class="auth-footer">
          <span>Don't have an account?</span>
          <router-link to="/register" class="link-highlight">Create Account</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../services/api';

const router = useRouter();
const email = ref('dev@example.com');
const password = ref('password123');
const loading = ref(false);
const errorMessage = ref('');

const quickFill = (e: string, p: string) => {
  email.value = e;
  password.value = p;
};

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    const res = await api.login(email.value, password.value);
    localStorage.setItem('access_token', res.access_token);
    localStorage.setItem('user_info', JSON.stringify(res.user));
    router.push('/');
  } catch (err: any) {
    errorMessage.value = err.message || 'Login failed. Please verify credentials.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 440px;
  padding: 36px 32px;
}

.auth-header {
  text-align: center;
  margin-bottom: 28px;
}

.brand-badge-logo {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 16px auto;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.auth-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 6px;
}

.auth-desc {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.form-control {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  color: #ffffff;
  font-size: 0.9rem;
  outline: none;
  transition: all 0.2s ease;
}

.form-control:focus {
  border-color: var(--accent-indigo);
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.3);
}

.btn-block {
  width: 100%;
  padding: 12px;
  margin-top: 6px;
}

.alert-box {
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.alert-box.error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

.quick-fill-section {
  margin-top: 10px;
  padding: 12px;
  background: rgba(30, 41, 59, 0.4);
  border-radius: var(--radius-md);
  border: 1px dashed var(--border-glass);
}

.quick-fill-label {
  display: block;
  font-size: 0.72rem;
  color: var(--text-dim);
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 8px;
}

.quick-fill-buttons {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.btn-demo {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-glass);
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 0.75rem;
  color: var(--accent-cyan);
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.btn-demo:hover {
  background: rgba(6, 182, 212, 0.15);
  border-color: rgba(6, 182, 212, 0.3);
}

.auth-footer {
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.link-highlight {
  color: var(--accent-cyan);
  font-weight: 600;
}
.link-highlight:hover {
  text-decoration: underline;
}
</style>
