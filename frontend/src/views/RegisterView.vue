<template>
  <div class="auth-container">
    <div class="auth-card glass-panel">
      <div class="auth-header">
        <img class="auth-logo" src="/hirezy-logo.png" alt="HIREZY logo" />
        <h2>Create Account</h2>
        <p class="subtitle">Join HIREZY to start screening or analyzing CVs</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div v-if="error" class="alert error">
          <span class="alert-icon">⚠️</span>
          <span class="alert-message">{{ error }}</span>
        </div>

        <div class="form-group">
          <label for="name">Full Name</label>
          <input
            id="name"
            v-model="name"
            type="text"
            placeholder="John Doe"
            class="input-field"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="email">Email Address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="name@company.com"
            class="input-field"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label>Select Your Role</label>
          <div class="role-selector">
            <button
              type="button"
              class="role-card"
              :class="{ selected: role === 'jobseeker' }"
              @click="role = 'jobseeker'"
              :disabled="loading"
            >
              <span class="role-icon">🔍</span>
              <div class="role-meta">
                <span class="role-title">Job Seeker</span>
                <span class="role-desc">Analyze CV and find jobs</span>
              </div>
            </button>

            <button
              type="button"
              class="role-card"
              :class="{ selected: role === 'hr' }"
              @click="role = 'hr'"
              :disabled="loading"
            >
              <span class="role-icon">💼</span>
              <div class="role-meta">
                <span class="role-title">HR Recruiter</span>
                <span class="role-desc">Rank and cluster candidates</span>
              </div>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Min. 6 characters"
            class="input-field"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Re-enter password"
            class="input-field"
            required
            :disabled="loading"
          />
        </div>

        <button type="submit" class="btn-primary auth-submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span>{{ loading ? 'Creating account...' : 'Create Account' }}</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>Already have an account? <router-link to="/login">Login here</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../stores/auth'

const router = useRouter()
const toast = inject('toast')

const name = ref('')
const email = ref('')
const role = ref('jobseeker')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref(null)

async function handleRegister() {
  if (!name.value || !email.value || !password.value || !confirmPassword.value) {
    return
  }

  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters long.'
    toast?.warning(error.value)
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.'
    toast?.warning(error.value)
    return
  }

  loading.value = true
  error.value = null

  try {
    const user = await register(name.value, email.value, password.value, role.value)
    toast?.success(`Account created successfully! Welcome, ${user.name}.`)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.message || 'Registration failed. Please try again.'
    toast?.error(error.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 1.5rem;
}

.auth-card {
  width: 100%;
  max-width: 480px;
  padding: 2.5rem;
  box-sizing: border-box;
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-logo {
  width: 3.5rem;
  height: 3.5rem;
  margin-bottom: 1rem;
  filter: drop-shadow(0 8px 16px rgba(3, 105, 161, 0.2));
}

.auth-header h2 {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0 0 0.5rem;
}

.subtitle {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-top: 0.25rem;
}

.role-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.52);
  border: 1px solid rgba(14, 116, 144, 0.14);
  cursor: pointer;
  transition: all 0.2s ease;
}

.role-card:hover {
  background: rgba(255, 255, 255, 0.82);
  border-color: rgba(14, 165, 233, 0.36);
  transform: translateY(-2px);
}

.role-card.selected {
  background: rgba(14, 165, 233, 0.08);
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.16);
}

.role-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.role-meta {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.role-title {
  font-weight: 850;
  font-size: 0.9rem;
  color: var(--text-soft);
}

.role-desc {
  font-size: 0.72rem;
  color: var(--text-muted);
  line-height: 1.2;
}

.auth-submit-btn {
  width: 100%;
  margin-top: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.auth-footer {
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-top: 1.5rem;
}

.auth-footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 700;
}

.auth-footer a:hover {
  text-decoration: underline;
}

/* Alert Styles */
.alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.9rem 1.1rem;
  border-radius: 14px;
  font-size: 0.88rem;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.alert.error {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.22);
  color: #DC2626;
}

.alert-icon {
  font-size: 1.1rem;
}

/* Spinner */
.spinner {
  width: 1.2rem;
  height: 1.2rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #FFFFFF;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 420px) {
  .role-selector {
    grid-template-columns: 1fr;
  }
}
</style>
