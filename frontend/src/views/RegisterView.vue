<template>
  <div class="auth-page">
    <div class="auth-card glass-panel">
      <div class="auth-header">
        <div class="brand-badge-logo">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="8.5" cy="7" r="4"></circle>
            <line x1="20" y1="8" x2="20" y2="14"></line>
            <line x1="23" y1="11" x2="17" y2="11"></line>
          </svg>
        </div>
        <h1 class="auth-title">Create Account</h1>
        <p class="auth-desc">Register a Developer or Admin profile to access DevAgent</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div v-if="errorMessage" class="alert-box error">
          {{ errorMessage }}
        </div>

        <div class="form-group">
          <label for="reg-name">Full Name</label>
          <input
            id="reg-name"
            type="text"
            v-model="fullName"
            placeholder="John Engineer"
            required
            class="form-control"
          />
        </div>

        <div class="form-group">
          <label for="reg-email">Work Email</label>
          <input
            id="reg-email"
            type="email"
            v-model="email"
            placeholder="john@example.com"
            required
            class="form-control"
          />
        </div>

        <div class="form-group">
          <label for="reg-password">Password</label>
          <input
            id="reg-password"
            type="password"
            v-model="password"
            placeholder="Minimum 6 characters"
            required
            minlength="6"
            class="form-control"
          />
        </div>

        <div class="form-group">
          <label for="reg-role">System Role</label>
          <select id="reg-role" v-model="role" class="form-control select-control">
            <option value="developer">Developer</option>
            <option value="admin">Admin / Lead</option>
          </select>
        </div>

        <button id="btn-register-submit" type="submit" class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span>{{ loading ? 'Creating Account...' : 'Register & Start' }}</span>
        </button>

        <div class="auth-footer">
          <span>Already have an account?</span>
          <router-link to="/login" class="link-highlight">Sign In</router-link>
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
const fullName = ref('');
const email = ref('');
const password = ref('');
const role = ref('developer');
const loading = ref(false);
const errorMessage = ref('');

const handleRegister = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    const res = await api.register(email.value, password.value, fullName.value, role.value);
    localStorage.setItem('access_token', res.access_token);
    localStorage.setItem('user_info', JSON.stringify(res.user));
    router.push('/');
  } catch (err: any) {
    errorMessage.value = err.message || 'Registration failed.';
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

.select-control {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 14px center;
  background-size: 16px;
}

.btn-block {
  width: 100%;
  padding: 12px;
  margin-top: 6px;
}

.alert-box.error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
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
