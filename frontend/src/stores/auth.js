import { reactive, computed } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'

// Load initial token and user from localStorage if they exist
const savedToken = localStorage.getItem('token')
let savedUser = null
try {
  const userJson = localStorage.getItem('user')
  if (userJson) {
    savedUser = JSON.parse(userJson)
  }
} catch (e) {
  console.error('Error parsing saved user', e)
}

export const authState = reactive({
  user: savedUser,
  token: savedToken,
  loading: false,
  error: null,
  needsRoleSelection: false
})

export const isAuthenticated = computed(() => !!authState.token)
export const isHR = computed(() => authState.user?.role === 'hr')
export const isJobSeeker = computed(() => authState.user?.role === 'jobseeker')
export const isAdmin = computed(() => authState.user?.role === 'admin')

// Helper to set authorization header globally on axios
export function setAuthHeader(token) {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete axios.defaults.headers.common['Authorization']
  }
}

// Initialize axios auth header if token exists
if (savedToken) {
  setAuthHeader(savedToken)
}

export async function login(email, password) {
  authState.loading = true
  authState.error = null
  try {
    const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
      email,
      password
    })
    const { access_token, user } = response.data
    authState.token = access_token
    authState.user = user
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))
    setAuthHeader(access_token)
    return user
  } catch (err) {
    const errMsg = err.message || err.response?.data?.detail || 'Login failed. Please check your credentials.'
    authState.error = errMsg
    throw new Error(errMsg)
  } finally {
    authState.loading = false
  }
}

export async function register(name, email, password, role) {
  authState.loading = true
  authState.error = null
  try {
    const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
      name,
      email,
      password,
      role
    })
    const { access_token, user } = response.data
    authState.token = access_token
    authState.user = user
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))
    setAuthHeader(access_token)
    return user
  } catch (err) {
    const errMsg = err.message || err.response?.data?.detail || 'Registration failed. Please try again.'
    authState.error = errMsg
    throw new Error(errMsg)
  } finally {
    authState.loading = false
  }
}

export async function loginWithGoogle(credential) {
  authState.loading = true
  authState.error = null
  authState.needsRoleSelection = false
  try {
    const response = await axios.post(`${API_BASE_URL}/api/auth/google`, {
      credential
    })
    const { access_token, user, needs_role_selection } = response.data
    authState.token = access_token
    authState.user = user
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))
    setAuthHeader(access_token)

    if (needs_role_selection) {
      authState.needsRoleSelection = true
    }

    return { user, needs_role_selection }
  } catch (err) {
    const errMsg = err.message || err.response?.data?.detail || 'Google Sign-In failed.'
    authState.error = errMsg
    throw new Error(errMsg)
  } finally {
    authState.loading = false
  }
}

export async function setRole(role) {
  authState.loading = true
  authState.error = null
  try {
    const response = await axios.post(`${API_BASE_URL}/api/auth/set-role`, { role })
    const { access_token, user } = response.data
    authState.token = access_token
    authState.user = user
    authState.needsRoleSelection = false
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))
    setAuthHeader(access_token)
    return user
  } catch (err) {
    const errMsg = err.message || err.response?.data?.detail || 'Failed to set role.'
    authState.error = errMsg
    throw new Error(errMsg)
  } finally {
    authState.loading = false
  }
}

export function logout() {
  authState.token = null
  authState.user  = null
  authState.error = null
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  setAuthHeader(null)
  // Navigation is handled by the caller via vue-router (no full page reload)
}

export async function fetchCurrentUser() {
  if (!authState.token) return null
  try {
    const response = await axios.get(`${API_BASE_URL}/api/auth/me`)
    authState.user = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
    return response.data
  } catch (err) {
    logout()
    return null
  }
}
