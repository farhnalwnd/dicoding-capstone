<template>
  <span
    class="skill-pill"
    :class="'skill-pill--' + type"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
  >
    <!-- Status dot -->
    <span class="skill-pill__dot"></span>
    <span class="skill-pill__name">{{ name }}</span>

    <!-- Tooltip -->
    <span
      v-if="score != null && showTooltip"
      class="skill-pill__tooltip"
      role="tooltip"
    >
      {{ score }}% match
    </span>
  </span>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  name: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'neutral',
    validator: (v) => ['matched', 'missing', 'neutral'].includes(v)
  },
  score: {
    type: Number,
    default: null
  }
})

const showTooltip = ref(false)
</script>

<style scoped>
.skill-pill {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  border: 1.5px solid;
  cursor: default;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  white-space: nowrap;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

.skill-pill:hover {
  transform: scale(1.05);
}

/* ── Matched (green) ─────────────────────────────── */
.skill-pill--matched {
  background: rgba(34, 197, 94, 0.08);
  border-color: rgba(34, 197, 94, 0.35);
  color: #16A34A;
}

.skill-pill--matched:hover {
  box-shadow: 0 4px 14px rgba(34, 197, 94, 0.2);
  background: rgba(34, 197, 94, 0.14);
}

.skill-pill--matched .skill-pill__dot {
  background: #22C55E;
}

[data-theme='dark'] .skill-pill--matched {
  background: rgba(34, 197, 94, 0.12);
  border-color: rgba(34, 197, 94, 0.3);
  color: #4ADE80;
}

[data-theme='dark'] .skill-pill--matched:hover {
  box-shadow: 0 4px 14px rgba(34, 197, 94, 0.15);
}

/* ── Missing (red) ────────────────────────────────── */
.skill-pill--missing {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.3);
  color: #DC2626;
}

.skill-pill--missing:hover {
  box-shadow: 0 4px 14px rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.14);
}

.skill-pill--missing .skill-pill__dot {
  background: #EF4444;
}

[data-theme='dark'] .skill-pill--missing {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.25);
  color: #FCA5A5;
}

[data-theme='dark'] .skill-pill--missing:hover {
  box-shadow: 0 4px 14px rgba(239, 68, 68, 0.15);
}

/* ── Neutral (gray) ───────────────────────────────── */
.skill-pill--neutral {
  background: rgba(100, 116, 139, 0.06);
  border-color: rgba(100, 116, 139, 0.2);
  color: #64748B;
}

.skill-pill--neutral:hover {
  box-shadow: 0 4px 14px rgba(100, 116, 139, 0.12);
  background: rgba(100, 116, 139, 0.1);
}

.skill-pill--neutral .skill-pill__dot {
  background: #94A3B8;
}

[data-theme='dark'] .skill-pill--neutral {
  background: rgba(148, 163, 184, 0.1);
  border-color: rgba(148, 163, 184, 0.18);
  color: #94A3B8;
}

/* ── Dot ──────────────────────────────────────────── */
.skill-pill__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ── Name ─────────────────────────────────────────── */
.skill-pill__name {
  line-height: 1.2;
}

/* ── Tooltip ──────────────────────────────────────── */
.skill-pill__tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  padding: 0.3rem 0.6rem;
  border-radius: 8px;
  background: var(--text, #0F172A);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
  pointer-events: none;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: tooltipIn 0.15s ease;
}

.skill-pill__tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: var(--text, #0F172A);
}

[data-theme='dark'] .skill-pill__tooltip {
  background: #F1F5F9;
  color: #0F172A;
}

[data-theme='dark'] .skill-pill__tooltip::after {
  border-top-color: #F1F5F9;
}

@keyframes tooltipIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>
