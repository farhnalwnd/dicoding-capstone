<template>
  <transition name="slide-down">
    <div v-if="modelValue" class="floating-banner sub-glass-card">
      <div class="banner-content">
        <span class="banner-icon">⚠️</span>
        <div class="banner-text">
          <h5 class="banner-title">{{ title || 'AI Request Failed' }}</h5>
          <p class="banner-message">{{ message }}</p>
        </div>
      </div>
      <div class="banner-actions">
        <button v-if="retryFunction" @click="handleRetry" class="banner-btn retry-btn">
          <span>🔄</span> Retry
        </button>
        <button @click="close" class="banner-close-btn" aria-label="Close banner">
          &times;
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    required: true
  },
  retryFunction: {
    type: Function,
    default: null
  },
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

const handleRetry = () => {
  if (props.retryFunction) {
    props.retryFunction()
  }
  close()
}
</script>

<style scoped>
.floating-banner {
  position: fixed;
  top: 84px; /* navbar height + spacing */
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 40px);
  max-width: 800px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.95rem 1.4rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(239, 68, 68, 0.25);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  z-index: 999;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  text-align: left;
}

.banner-icon {
  font-size: 1.35rem;
}

.banner-text {
  display: flex;
  flex-direction: column;
}

.banner-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 800;
  color: #7F1D1D;
}

.banner-message {
  margin: 0.15rem 0 0;
  font-size: 0.82rem;
  font-weight: 600;
  color: #991B1B;
}

.banner-actions {
  display: flex;
  align-items: center;
  gap: 0.95rem;
}

.banner-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.9rem;
  font-size: 0.8rem;
  font-weight: 800;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn {
  background: #FEF2F2;
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #991B1B;
}

.retry-btn:hover {
  background: #FEE2E2;
  transform: translateY(-1px);
}

.banner-close-btn {
  background: none;
  border: none;
  font-size: 1.45rem;
  color: #991B1B;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  opacity: 0.75;
  transition: opacity 0.2s ease;
}

.banner-close-btn:hover {
  opacity: 1;
}

/* Transitions */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translate(-50%, -20px);
  opacity: 0;
}

@media (max-width: 768px) {
  .floating-banner {
    top: 76px;
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    padding: 0.8rem 1.1rem;
  }
  
  .banner-actions {
    justify-content: flex-end;
  }
}
</style>
