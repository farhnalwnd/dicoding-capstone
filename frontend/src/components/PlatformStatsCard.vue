<template>
  <div class="pstats-card glass-panel" :class="`border-${color}`">
    <div class="pstats-icon-bg" :class="`icon-${color}`">
      <span>{{ icon }}</span>
    </div>
    <div class="pstats-details">
      <span class="pstats-value">{{ formattedValue }}</span>
      <span class="pstats-label">{{ label }}</span>
      <span v-if="sub" class="pstats-sub">{{ sub }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon:  { type: String, default: '📊' },
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  sub:   { type: String, default: '' },
  color: { type: String, default: 'blue' }  // blue | green | purple | amber | red | cyan | indigo | teal
})

const formattedValue = computed(() => {
  const v = Number(props.value)
  if (isNaN(v)) return props.value
  if (v >= 1000000) return (v / 1000000).toFixed(1) + 'M'
  if (v >= 1000) return (v / 1000).toFixed(1) + 'K'
  return v.toString()
})
</script>

<style scoped>
.pstats-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: 20px;
  transition: all 0.25s ease;
  cursor: default;
}

.pstats-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-strong);
}

.pstats-icon-bg {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  flex-shrink: 0;
}

.pstats-details {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.pstats-value {
  font-size: 1.6rem;
  font-weight: 900;
  color: var(--text-soft);
  line-height: 1.1;
}

.pstats-label {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pstats-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-style: italic;
}

/* Color system */
.border-blue   { border-left: 3px solid rgba(14,165,233,0.5); }
.border-green  { border-left: 3px solid rgba(34,197,94,0.5); }
.border-purple { border-left: 3px solid rgba(139,92,246,0.5); }
.border-amber  { border-left: 3px solid rgba(245,158,11,0.5); }
.border-red    { border-left: 3px solid rgba(239,68,68,0.5); }
.border-cyan   { border-left: 3px solid rgba(34,211,238,0.5); }
.border-indigo { border-left: 3px solid rgba(99,102,241,0.5); }
.border-teal   { border-left: 3px solid rgba(20,184,166,0.5); }

.icon-blue   { background:rgba(14,165,233,0.12);  border:1px solid rgba(14,165,233,0.2); }
.icon-green  { background:rgba(34,197,94,0.12);   border:1px solid rgba(34,197,94,0.2); }
.icon-purple { background:rgba(139,92,246,0.12);  border:1px solid rgba(139,92,246,0.2); }
.icon-amber  { background:rgba(245,158,11,0.12);  border:1px solid rgba(245,158,11,0.2); }
.icon-red    { background:rgba(239,68,68,0.12);   border:1px solid rgba(239,68,68,0.2); }
.icon-cyan   { background:rgba(34,211,238,0.12);  border:1px solid rgba(34,211,238,0.2); }
.icon-indigo { background:rgba(99,102,241,0.12);  border:1px solid rgba(99,102,241,0.2); }
.icon-teal   { background:rgba(20,184,166,0.12);  border:1px solid rgba(20,184,166,0.2); }
</style>
