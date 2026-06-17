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
import { ref, onMounted } from 'vue'

const visible = ref(false)
const message = ref('')
const type = ref('info')
const duration = ref(3000)
let timeoutId = null

const show = (msg, options = {}) => {
  message.value = msg
  type.value = options.type || 'info'
  duration.value = options.duration || 3000
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

onMounted(() => {
  // Auto-hide after duration
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
  z-index: 9999;
  font-family: 'Inter', sans-serif;
  border: 1px solid rgba(3, 105, 161, 0.15);
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
  border-left: 4px solid #0369A1;
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
  background: rgba(3, 105, 161, 0.15);
  color: #0369A1;
}

.toast-message {
  font-size: 0.95rem;
  font-weight: 500;
  color: #0C4A6E;
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #64748B;
  cursor: pointer;
  padding: 0;
  margin-left: 8px;
  line-height: 1;
}

.toast-close:hover {
  color: #0369A1;
}

/* Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>