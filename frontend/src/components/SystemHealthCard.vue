<template>
  <div class="health-card glass-panel" :class="`health-${service.status}`">
    <div class="health-header">
      <div class="health-icon-wrap" :class="`icon-${service.status}`">
        <span>{{ iconMap[service.icon] || '🔧' }}</span>
      </div>
      <div class="health-info">
        <span class="health-name">{{ service.name }}</span>
        <span class="health-time" v-if="service.response_ms != null">
          {{ service.response_ms }}ms
        </span>
      </div>
      <span class="health-badge" :class="`badge-${service.status}`">
        {{ statusLabel[service.status] || service.status }}
      </span>
    </div>
    <p v-if="service.detail" class="health-detail">{{ service.detail }}</p>
    <div class="health-indicator" :class="`ind-${service.status}`"></div>
  </div>
</template>

<script setup>
defineProps({
  service: { type: Object, required: true }
})

const iconMap = {
  server:     '🖥️',
  database:   '🗄️',
  chart:      '📊',
  graph:      '📈',
  experiment: '🔬',
  ci:         '⚙️',
}

const statusLabel = {
  healthy: 'Healthy',
  warning: 'Warning',
  error:   'Error',
  unknown: 'Unknown',
}
</script>

<style scoped>
.health-card {
  padding: 1.25rem 1.5rem;
  border-radius: 18px;
  position: relative;
  overflow: hidden;
  transition: all 0.25s ease;
}

.health-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-strong);
}

.health-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.health-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.icon-healthy { background: rgba(34,197,94,0.12);  border: 1px solid rgba(34,197,94,0.2); }
.icon-warning { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.2); }
.icon-error   { background: rgba(239,68,68,0.12);  border: 1px solid rgba(239,68,68,0.2); }
.icon-unknown { background: rgba(100,116,139,0.12);border: 1px solid rgba(100,116,139,0.2); }

.health-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.health-name {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-soft);
}

.health-time {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
}

.health-badge {
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.badge-healthy { background:rgba(34,197,94,0.12);  color:#15803D; border:1px solid rgba(34,197,94,0.25); }
.badge-warning { background:rgba(245,158,11,0.12); color:#B45309; border:1px solid rgba(245,158,11,0.25); }
.badge-error   { background:rgba(239,68,68,0.12);  color:#DC2626; border:1px solid rgba(239,68,68,0.25); }
.badge-unknown { background:rgba(100,116,139,0.1); color:#64748b; border:1px solid rgba(100,116,139,0.2); }

.health-detail {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0.5rem 0 0;
  padding-left: 0.25rem;
  font-style: italic;
}

/* Bottom indicator strip */
.health-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
}

.ind-healthy { background: linear-gradient(90deg, #22C55E, #16A34A); }
.ind-warning { background: linear-gradient(90deg, #F59E0B, #D97706); }
.ind-error   { background: linear-gradient(90deg, #EF4444, #DC2626); }
.ind-unknown { background: linear-gradient(90deg, #94A3B8, #64748B); }
</style>
