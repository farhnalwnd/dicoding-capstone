<template>
  <div class="glass-panel error-state-card">
    <div class="error-icon-ring" :class="`type-${type}`">
      <span class="error-emoji">{{ getEmoji(type) }}</span>
    </div>
    <h3 class="error-title">{{ title || getDefaultTitle(type) }}</h3>
    <p class="error-message">{{ message || getDefaultMessage(type) }}</p>
    <button v-if="retryFunction" @click="retryFunction" class="btn-primary retry-btn">
      <span>🔄</span> Retry
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'backend' // 'network', 'backend', 'validation', 'timeout', 'empty'
  },
  retryFunction: {
    type: Function,
    default: null
  }
})

const getEmoji = (type) => {
  switch (type) {
    case 'network': return '📶'
    case 'validation': return '📋'
    case 'timeout': return '⏱'
    case 'empty': return '🔍'
    case 'backend':
    default: return '⚠️'
  }
}

const getDefaultTitle = (type) => {
  switch (type) {
    case 'network': return 'Network Connection Failed'
    case 'validation': return 'Validation Error'
    case 'timeout': return 'Request Timeout'
    case 'empty': return 'No Results Found'
    case 'backend':
    default: return 'AI Service Error'
  }
}

const getDefaultMessage = (type) => {
  switch (type) {
    case 'network': return 'Unable to connect to HIREZY server. Please check your internet connection.'
    case 'validation': return 'Please verify that all fields and uploads are correct.'
    case 'timeout': return 'The analysis is taking longer than expected. Please try again.'
    case 'empty': return 'Try different keywords or criteria.'
    case 'backend':
    default: return 'The AI service encountered an unexpected issue. Please try again in a few moments.'
  }
}
</script>

<style scoped>
.error-state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2.5rem 2rem;
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  max-width: 600px;
  width: 100%;
  margin: 2rem auto;
  gap: 1.1rem;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-icon-ring {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.85rem;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
  margin-bottom: 0.25rem;
}

.type-network {
  background: rgba(239, 68, 68, 0.12);
  border: 2px solid var(--danger);
  color: var(--danger);
}

.type-backend {
  background: rgba(245, 158, 11, 0.12);
  border: 2px solid var(--warning);
  color: var(--warning);
}

.type-validation {
  background: rgba(14, 165, 233, 0.12);
  border: 2px solid var(--secondary);
  color: var(--secondary);
}

.type-timeout {
  background: rgba(99, 102, 241, 0.12);
  border: 2px solid var(--indigo);
  color: var(--indigo);
}

.type-empty {
  background: rgba(100, 116, 139, 0.12);
  border: 2px solid var(--text-muted);
  color: var(--text-muted);
}

.error-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 850;
  color: var(--text-soft);
}

.error-message {
  margin: 0;
  font-size: 0.94rem;
  color: var(--text-muted);
  line-height: 1.55;
  max-width: 440px;
}

.retry-btn {
  margin-top: 0.5rem;
  min-width: 150px;
  min-height: 40px;
}
</style>
