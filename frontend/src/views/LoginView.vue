<template>
  <div class="auth-container">
    <div class="auth-card glass-panel">
      <div class="auth-header">
        <img class="auth-logo" src="/icon.svg" alt="CV Matcher Pro logo" />
        <h2>Welcome Back</h2>
        <p class="subtitle">Log in to your CV Matcher Pro account</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div v-if="error" class="alert error">
          <span class="alert-icon">⚠️</span>
          <span class="alert-message">{{ error }}</span>
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
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="input-field"
            required
            :disabled="loading"
          />
        </div>

        <button type="submit" class="btn-primary auth-submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span>{{ loading ? 'Logging in...' : 'Log In' }}</span>
        </button>
      </form>

      <div class="divider">
        <span>or</span>
      </div>

      <div class="google-auth-wrapper">
        <div ref="googleBtn" class="google-btn-container"></div>
      </div>

      <div class="auth-footer">
        <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { login, loginWithGoogle } from '../stores/auth'

const router = useRouter()
const toast = inject('toast')

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const googleBtn = ref(null)

function getRedirectByRole(role) {
  if (role === 'admin')     return '/admin'
  if (role === 'hr')        return '/hr-dashboard'
  return '/dashboard'
}

async function handleLogin() {
  if (!email.value || !password.value) return
  loading.value = true
  error.value = null
  try {
    const user = await login(email.value, password.value)
    toast?.success(`Welcome back, ${user.name}!`)
    router.push(getRedirectByRole(user.role))
  } catch (err) {
    error.value = err.message || 'Invalid email or password.'
    toast?.error(error.value)
  } finally {
    loading.value = false
  }
}

async function handleGoogleCallback(response) {
  loading.value = true
  error.value = null
  try {
    const user = await loginWithGoogle(response.credential)
    toast?.success(`Welcome, ${user.name}!`)
    router.push(getRedirectByRole(user.role))
  } catch (err) {
    error.value = err.message || 'Google authentication failed.'
    toast?.error(error.value)
  } finally {
    loading.value = false
  }
}

function initGoogleSignIn() {
  if (window.google) {
    try {
      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
        callback: handleGoogleCallback,
        auto_select: false
      })
      window.google.accounts.id.renderButton(googleBtn.value, {
        type: 'standard',
        theme: 'outline',
        size: 'large',
        text: 'signin_with',
        shape: 'pill',
        logo_alignment: 'left',
        width: '320'
      })
    } catch (e) {
      console.warn('Failed to initialize Google Sign-In client:', e)
    }
  } else {
    // Retry loading Google script in case of slow connections
    setTimeout(initGoogleSignIn, 1000)
  }
}

onMounted(() => {
  initGoogleSignIn()
})
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
  max-width: 440px;
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

.auth-submit-btn {
  width: 100%;
  margin-top: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: var(--text-muted);
  margin: 1.5rem 0;
  font-size: 0.88rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid rgba(14, 116, 144, 0.14);
}

.divider:not(:empty)::before {
  margin-right: .75em;
}

.divider:not(:empty)::after {
  margin-left: .75em;
}

.google-auth-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.google-btn-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.auth-footer {
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-muted);
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
</style>
