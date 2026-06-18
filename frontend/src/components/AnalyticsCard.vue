<template>
  <div class="glass-panel analytics-card" :class="borderClass">
    <div class="card-top">
      <div class="card-icon-bg" :class="iconBgClass">
        <span class="card-icon">{{ icon }}</span>
      </div>
      
      <div class="trend-badge" :class="trendClass" v-if="trend && trend !== '0%'">
        <span class="trend-arrow" v-if="!isNewTrend">{{ isPositiveTrend ? '▲' : '▼' }}</span>
        <span class="trend-arrow" v-else>✦</span>
        <span class="trend-text">{{ trend }}</span>
      </div>
      <div class="trend-badge trend-neutral" v-else>
        <span class="trend-text">–</span>
      </div>
    </div>

    <div class="card-details">
      <span class="card-val">{{ count }}</span>
      <span class="card-lbl">{{ title }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  count: {
    type: [Number, String],
    required: true
  },
  trend: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: '👥'
  },
  theme: {
    type: String,
    default: 'blue' // blue, cyan, purple, amber, green, red
  }
})

const isNewTrend = computed(() => props.trend === 'New')

const isPositiveTrend = computed(() => {
  return props.trend && props.trend.startsWith('+')
})

const borderClass = computed(() => {
  return `border-${props.theme}`
})

const iconBgClass = computed(() => {
  return `${props.theme}-bg`
})

const trendClass = computed(() => {
  if (isNewTrend.value) return 'trend-new'
  return isPositiveTrend.value ? 'trend-up' : 'trend-down'
})
</script>

<style scoped>
.analytics-card {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  padding: 1.5rem 1.65rem;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  transition: all 0.25s ease;
  text-align: left;
}

.analytics-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-strong);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-icon-bg {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

/* Icon backgrounds HSL */
.blue-bg {
  background-color: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(14, 165, 233, 0.2);
}
.cyan-bg {
  background-color: rgba(34, 211, 238, 0.12);
  border: 1px solid rgba(34, 211, 238, 0.2);
}
.purple-bg {
  background-color: rgba(139, 92, 246, 0.12);
  border: 1px solid rgba(139, 92, 246, 0.2);
}
.amber-bg {
  background-color: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.2);
}
.green-bg {
  background-color: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.2);
}
.red-bg {
  background-color: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

/* Border Glows */
.border-blue:hover { border-color: rgba(14, 165, 233, 0.45); }
.border-cyan:hover { border-color: rgba(34, 211, 238, 0.45); }
.border-purple:hover { border-color: rgba(139, 92, 246, 0.45); }
.border-amber:hover { border-color: rgba(245, 158, 11, 0.45); }
.border-green:hover { border-color: rgba(34, 197, 94, 0.45); }
.border-red:hover { border-color: rgba(239, 68, 68, 0.45); }

/* Trend Badges */
.trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.55rem;
  border-radius: 8px;
  font-size: 0.74rem;
  font-weight: 800;
  border: 1px solid transparent;
}

.trend-up {
  background-color: rgba(34, 197, 94, 0.1);
  color: #16A34A;
  border-color: rgba(34, 197, 94, 0.2);
}

.trend-down {
  background-color: rgba(239, 68, 68, 0.1);
  color: #DC2626;
  border-color: rgba(239, 68, 68, 0.2);
}

.trend-neutral {
  background-color: rgba(148, 163, 184, 0.1);
  color: #64748B;
  border-color: rgba(148, 163, 184, 0.2);
}

.trend-new {
  background-color: rgba(14, 165, 164, 0.08);
  color: var(--accent);
  border-color: rgba(14, 165, 164, 0.2);
}

/* Details */
.card-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.card-val {
  font-size: 1.85rem;
  font-weight: 900;
  color: var(--text-soft);
  line-height: 1.15;
}

.card-lbl {
  font-size: 0.76rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}
</style>
