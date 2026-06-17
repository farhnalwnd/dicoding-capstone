import axios from 'axios'

// Response Interceptor to map status codes and handle errors globally
axios.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Log original error and stack trace to console for developers
    console.error('[Developer Error Log]', error)

    let serverDetail = error.response?.data?.detail

    let errorPayload = {
      type: 'backend',
      message: serverDetail || 'The AI service encountered an unexpected issue. Please try again in a few moments.',
      originalError: error
    }

    if (error.code === 'ECONNABORTED' || (error.message && error.message.toLowerCase().includes('timeout'))) {
      errorPayload.type = 'timeout'
      errorPayload.message = 'The analysis is taking longer than expected. Please try again.'
    } else if (!error.response) {
      // Network Error (e.g. server down or offline)
      errorPayload.type = 'network'
      errorPayload.message = 'Unable to connect to HIREZY server. Please check your internet connection.'
    } else {
      const status = error.response.status
      
      switch (status) {
        case 400:
          errorPayload.type = 'validation'
          errorPayload.message = serverDetail || 'Invalid request.'
          break
        case 401:
          errorPayload.message = serverDetail || 'Access denied. Please check your credentials.'
          // Only auto-redirect for non-auth endpoints
          if (!error.config?.url?.includes('/api/auth/')) {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            delete axios.defaults.headers.common['Authorization']
            if (window.location.pathname !== '/login') {
              window.location.href = '/login'
            }
          }
          break
        case 403:
          errorPayload.message = 'Access forbidden. You do not have permission.'
          break
        case 404:
          errorPayload.message = 'Requested resource not found.'
          break
        case 408:
          errorPayload.type = 'timeout'
          errorPayload.message = 'The server timed out waiting for the request.'
          break
        case 429:
          errorPayload.message = 'Too many requests. Please wait and try again.'
          break
        case 409:
          errorPayload.message = serverDetail || 'This resource already exists.'
          break
        case 500:
          errorPayload.message = serverDetail || 'Internal server error.'
          break
        case 502:
        case 503:
        case 504:
          errorPayload.message = 'Service temporarily unavailable.'
          break
        default:
          if (error.response.data && error.response.data.message) {
            errorPayload.message = error.response.data.message
          }
          break
      }
    }

    return Promise.reject(errorPayload)
  }
)
