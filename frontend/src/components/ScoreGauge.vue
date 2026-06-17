<template>
  <div class="score-gauge" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :viewBox="`0 0 ${viewBox} ${viewBox}`" class="gauge-svg">
      <!-- Background circle -->
      <circle
        class="gauge-bg"
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke-width="strokeWidth"
      />
      <!-- Animated fill circle -->
      <circle
        class="gauge-fill"
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke-width="strokeWidth"
        :stroke="strokeColor"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="currentOffset"
        :style="{ transition: animated ? 'stroke-dashoffset 1.5s cubic-bezier(0.22, 1, 0.36, 1), stroke 0.4s ease' : 'none' }"
      />
    </svg>
    <div class="gauge-center">
      <div class="gauge-value" :style="{ color: textColor }">
        <span class="gauge-number">{{ displayScore }}</span><span class="gauge-percent">%</span>
      </div>
      <div class="gauge-label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  score: {
    type: Number,
    default: 0,
    validator: (v) => v >= 0 && v <= 100
  },
  size: {
    type: Number,
    default: 180
  },
  label: {
    type: String,
    default: 'Match Score'
  },
  animated: {
    type: Boolean,
    default: true
  }
})

const viewBox = 200
const center = 100
const strokeWidth = 12
const radius = 88
const circumference = 2 * Math.PI * radius

const displayScore = ref(0)
const currentOffset = ref(circumference)
let animationFrame = null

const targetOffset = computed(() => {
  const clamped = Math.min(100, Math.max(0, props.score))
  return circumference - (clamped / 100) * circumference
})

const strokeColor = computed(() => {
  if (props.score < 40) return '#EF4444'
  if (props.score <= 70) return '#F59E0B'
  return '#22C55E'
})

const textColor = computed(() => {
  if (props.score < 40) return '#EF4444'
  if (props.score <= 70) return '#F59E0B'
  return '#22C55E'
})

function animateCounter(from, to, duration) {
  if (animationFrame) cancelAnimationFrame(animationFrame)
  const startTime = performance.now()

  function tick(now) {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    // Ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3)
    displayScore.value = Math.round(from + (to - from) * eased)

    if (progress < 1) {
      animationFrame = requestAnimationFrame(tick)
    }
  }

  animationFrame = requestAnimationFrame(tick)
}

function animateIn() {
  if (props.animated) {
    currentOffset.value = circumference
    displayScore.value = 0
    // Trigger reflow, then animate
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        currentOffset.value = targetOffset.value
        animateCounter(0, props.score, 1500)
      })
    })
  } else {
    currentOffset.value = targetOffset.value
    displayScore.value = props.score
  }
}

onMounted(() => {
  animateIn()
})

watch(() => props.score, (newVal, oldVal) => {
  currentOffset.value = targetOffset.value
  if (props.animated) {
    animateCounter(oldVal || 0, newVal, 1500)
  } else {
    displayScore.value = newVal
  }
})
</script>

<style scoped>
.score-gauge {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.gauge-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.gauge-bg {
  stroke: var(--line, rgba(14, 116, 144, 0.14));
  transition: stroke 0.3s ease;
}

[data-theme='dark'] .gauge-bg {
  stroke: rgba(148, 163, 184, 0.12);
}

.gauge-fill {
  filter: drop-shadow(0 0 6px currentColor);
}

.gauge-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.gauge-value {
  display: flex;
  align-items: baseline;
  line-height: 1;
}

.gauge-number {
  font-size: 2.6rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

.gauge-percent {
  font-size: 1.2rem;
  font-weight: 700;
  margin-left: 2px;
  opacity: 0.8;
}

.gauge-label {
  margin-top: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-muted, #64748B);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

[data-theme='dark'] .gauge-label {
  color: var(--text-muted, #64748B);
}
</style>
