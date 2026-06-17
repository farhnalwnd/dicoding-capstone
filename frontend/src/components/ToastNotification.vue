<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="visible" :class="['toast', `toast-${type}`]">
        <div class="toast-icon">
          <span v-if="type === 'success'">✓</span>
          <span v-else-if="type === 'error'">✕</span>
          <span v-else-if="type === 'warning'">⚠</span>
          <span v-else>ℹ</span>
        </div>
        <div class="toast-message">{{ message }}</div>
        <button class="toast-close" @click="hide">×</button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
const type = ref('info')
const duration = ref(4000)
let timeoutId = null

const show = (msg, options = {}) => {
  message.value = msg
  type.value = options.type || 'info'
  duration.value = options.duration || 4000
  visible.value = true
  
  if (timeoutId) clearTimeout(timeoutId)
  timeoutId = setTimeout(hide, duration.value)
}

const hide = () => {
  visible.value = false
  if (timeoutId) {
    clearTimeout(timeoutId)
    timeoutId = null
  }
}

defineExpose({ show, hide })
</script>

<style scoped>
.toast {
  position: fixed;
  top: 88px; /* Safely below the sticky navbar height + padding */
  right: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  z-index: 9999;
  font-family: 'Inter', sans-serif;
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.toast-success {
  border-left: 4px solid #22C55E;
}

.toast-error {
  border-left: 4px solid #EF4444;
}

.toast-warning {
  border-left: 4px solid #EAB308;
}

.toast-info {
  border-left: 4px solid #0EA5E9;
}

.toast-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: bold;
  font-size: 14px;
}

.toast-success .toast-icon {
  background: rgba(34, 197, 94, 0.15);
  color: #16A34A;
}

.toast-error .toast-icon {
  background: rgba(239, 68, 68, 0.15);
  color: #DC2626;
}

.toast-warning .toast-icon {
  background: rgba(234, 179, 8, 0.15);
  color: #CA8A04;
}

.toast-info .toast-icon {
  background: rgba(14, 165, 233, 0.15);
  color: #0284C7;
}

.toast-message {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-soft);
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  margin-left: 8px;
  line-height: 1;
}

.toast-close:hover {
  color: var(--text-soft);
}

/* Transitions: Fade + Slide */
.toast-enter-active,
.toast-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(50px) scale(0.95);
}
</style>
