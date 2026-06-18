import { ref, computed } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const TOKEN_KEY = 'cvmatcher_jwt'
const USER_KEY = 'cvmatcher_user'

// ── Shared reactive state (singleton across all consumers) ───────────────
const token = ref(localStorage.getItem(TOKEN_KEY) || '')
const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))
const isNewUser = ref(false)

const isAuthenticated = computed(() => !!token.value && !!user.value)
const userRole = computed(() => user.value?.role || '')

// ── Helpers ──────────────────────────────────────────────────────────────
function persistSession(jwt, userData) {
  token.value = jwt
  user.value = userData
  localStorage.setItem(TOKEN_KEY, jwt)
  localStorage.setItem(USER_KEY, JSON.stringify(userData))
}

function clearSession() {
  token.value = ''
  user.value = null
  isNewUser.value = false
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

// ── Public API ───────────────────────────────────────────────────────────
export function useAuth() {
  /**
   * Set the user's role after initial registration.
   * Calls backend, updates localStorage, and refreshes the JWT.
   */
  async function setRole(role) {
    const { data } = await axios.post(
      `${API_BASE_URL}/api/auth/set-role`,
      { role },
      { headers: { Authorization: `Bearer ${token.value}` } }
    )
    // Update JWT if backend returns a new one
    const newToken = data.access_token || token.value
    const updatedUser = { ...user.value, role }
    persistSession(newToken, updatedUser)
    isNewUser.value = false
    return data
  }

  /**
   * Clear all local auth state and redirect to /login.
   */
  function logout() {
    // Fire-and-forget backend call (no real server state to clear)
    axios.post(`${API_BASE_URL}/api/auth/logout`).catch(() => {})
    clearSession()
    // Redirect handled by the navigation guard once state is cleared
    window.location.href = '/login'
  }

  /**
   * Return an Authorization header object ready for axios / fetch.
   */
  function getAuthHeaders() {
    if (!token.value) return {}
    return { Authorization: `Bearer ${token.value}` }
  }

  return {
    // Reactive state
    isAuthenticated,
    user,
    token,
    userRole,
    isNewUser,
    // Methods
    logout,
    setRole,
    getAuthHeaders,
  }
}
