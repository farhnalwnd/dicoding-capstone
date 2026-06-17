<template>
  <span class="status-badge" :class="badgeClass">
    <span class="badge-dot"></span>
    <span class="badge-text">{{ formatStatus(status) }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (val) => ['screening', 'talent_pool', 'interview', 'hired', 'rejected'].includes(val)
  }
})

const badgeClass = computed(() => {
  return `status-${props.status}`
})

function formatStatus(status) {
  if (!status) return ''
  if (status === 'talent_pool') return 'Talent Pool'
  return status.charAt(0).toUpperCase() + status.slice(1)
}
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid transparent;
  width: fit-content;
}

.badge-dot {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 50%;
}

/* Status variants */
.status-screening {
  background: rgba(14, 165, 233, 0.1);
  color: var(--accent);
  border-color: rgba(14, 165, 233, 0.2);
}
.status-screening .badge-dot {
  background: var(--accent);
}

.status-talent_pool {
  background: rgba(99, 102, 241, 0.1);
  color: #4f46e5;
  border-color: rgba(99, 102, 241, 0.2);
}
.status-talent_pool .badge-dot {
  background: #4f46e5;
}

.status-interview {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
  border-color: rgba(245, 158, 11, 0.2);
}
.status-interview .badge-dot {
  background: #d97706;
}

.status-hired {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border-color: rgba(16, 185, 129, 0.2);
}
.status-hired .badge-dot {
  background: #10b981;
}

.status-rejected {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border-color: rgba(239, 68, 68, 0.2);
}
.status-rejected .badge-dot {
  background: #ef4444;
}
</style>
