<template>
  <div class="glass-panel candidate-card" :class="{ 'best-match-card': rank === 1 }">
    <!-- Best Match Badge Highlight for Rank #1 -->
    <div v-if="rank === 1" class="best-match-badge">
      <span class="badge-text">🏆 Best Match</span>
    </div>

    <div class="card-header">
      <div class="candidate-info">
        <span class="rank-number">#{{ rank }}</span>
        <h3 class="candidate-name">{{ name }}</h3>
      </div>
      
      <!-- Score Badge -->
      <div class="score-badge" :class="scoreClass">
        <span class="score-percentage">{{ Number(score).toFixed(1) }}%</span>
        <span class="score-label">Match</span>
      </div>
    </div>

    <!-- Candidate Meta Info (Job Position, Date, Status) -->
    <div class="candidate-meta" v-if="jobPosition || dateAdded || status">
      <div class="meta-row" v-if="jobPosition">
        <span class="meta-icon">💼</span>
        <span class="meta-text">{{ jobPosition }}</span>
      </div>
      <div class="meta-row" v-if="dateAdded">
        <span class="meta-icon">📅</span>
        <span class="meta-text">Added on {{ formatDate(dateAdded) }}</span>
      </div>
      <div class="meta-row" v-if="status">
        <span class="meta-icon">🛡️</span>
        <span class="meta-text">
          <CandidateStatusBadge :status="status" />
        </span>
      </div>
    </div>

    <!-- Match Visualization Progress Bar -->
    <div class="progress-section">
      <div class="progress-header">
        <span class="progress-title">Similarity Score</span>
        <span class="progress-val">{{ Math.round(score) }}%</span>
      </div>
      <div class="progress-track-glass">
        <div 
          class="progress-fill-gradient" 
          :class="scoreProgressClass"
          :style="{ width: score + '%' }"
        ></div>
      </div>
    </div>

    <!-- Skills Section (Only if skills are present and not empty) -->
    <div class="skills-section" v-if="skills && skills.length">
      <h4 class="skills-title">Key Skills</h4>
      <div class="skills-pills">
        <span v-for="skill in skills" :key="skill" class="skill-pill">
          {{ skill }}
        </span>
      </div>
    </div>

    <!-- Action Buttons Row -->
    <div class="card-actions" v-if="showActions">
      <button 
        type="button" 
        class="btn-action btn-interview"
        @click.stop="$emit('move-to-interview')"
      >
        <span>📅</span> Move to Interview
      </button>
      <button 
        type="button" 
        class="btn-action btn-reject"
        @click.stop="$emit('remove')"
      >
        <span>❌</span> Remove
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CandidateStatusBadge from './CandidateStatusBadge.vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  score: {
    type: Number,
    required: true
  },
  skills: {
    type: Array,
    default: () => []
  },
  rank: {
    type: Number,
    required: true
  },
  jobPosition: {
    type: String,
    default: ''
  },
  dateAdded: {
    type: String,
    default: ''
  },
  status: {
    type: String,
    default: ''
  },
  showActions: {
    type: Boolean,
    default: false
  }
})

defineEmits(['move-to-interview', 'remove'])

// Determine styling class based on similarity score
const scoreClass = computed(() => {
  if (props.score >= 90) return 'score-green'
  if (props.score >= 75) return 'score-blue'
  if (props.score >= 60) return 'score-amber'
  return 'score-red'
})

const scoreProgressClass = computed(() => {
  if (props.score >= 90) return 'bg-green'
  if (props.score >= 75) return 'bg-blue'
  if (props.score >= 60) return 'bg-amber'
  return 'bg-red'
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch (e) {
    return dateStr
  }
}
</script>

<style scoped>
.candidate-card {
  padding: 1.8rem;
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  position: relative;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.candidate-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-strong);
  border-color: rgba(255, 255, 255, 0.85);
}

/* 1. Best Match Card Highlight (#1) */
.best-match-card {
  border: 1px solid rgba(34, 197, 94, 0.4);
  box-shadow: 0 16px 48px rgba(34, 197, 94, 0.14), var(--shadow-soft);
}

.best-match-card::before {
  content: '';
  position: absolute;
  inset: -1.5px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.5), rgba(74, 222, 128, 0.2), rgba(14, 165, 233, 0.3));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  z-index: 1;
}

.best-match-card:hover {
  box-shadow: 0 24px 60px rgba(34, 197, 94, 0.22), var(--shadow-strong);
  border-color: rgba(34, 197, 94, 0.6);
}

.best-match-badge {
  position: absolute;
  top: -12px;
  left: 24px;
  background: linear-gradient(135deg, #22C55E 0%, #10B981 100%);
  color: white;
  padding: 0.35rem 0.95rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  box-shadow: 0 8px 20px rgba(34, 197, 94, 0.3);
  z-index: 2;
  text-transform: uppercase;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.candidate-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.rank-number {
  font-size: 1.15rem;
  font-weight: 850;
  color: var(--primary-dark);
  background: rgba(14, 165, 233, 0.08);
  padding: 0.25rem 0.65rem;
  border-radius: 10px;
  border: 1px solid rgba(14, 165, 233, 0.12);
}

.candidate-name {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-soft);
}

/* Score Badges */
.score-badge {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.45rem 0.85rem;
  border-radius: 16px;
  border: 1px solid;
  min-width: 68px;
}

.score-percentage {
  font-size: 1.05rem;
  font-weight: 900;
  line-height: 1.1;
}

.score-label {
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.8;
}

.score-green {
  background: rgba(34, 197, 94, 0.12);
  border-color: rgba(34, 197, 94, 0.3);
  color: #16A34A;
}

.score-blue {
  background: rgba(14, 165, 233, 0.12);
  border-color: rgba(14, 165, 233, 0.3);
  color: #0284C7;
}

.score-amber {
  background: rgba(245, 158, 11, 0.12);
  border-color: rgba(245, 158, 11, 0.3);
  color: #D97706;
}

.score-red {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.3);
  color: #DC2626;
}

/* Candidate Meta Info styling */
.candidate-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.6rem 0;
  border-top: 1px solid rgba(14, 116, 144, 0.08);
  border-bottom: 1px solid rgba(14, 116, 144, 0.08);
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.88rem;
  color: var(--text-soft);
}

.meta-icon {
  font-size: 1rem;
}

.meta-text {
  font-weight: 500;
}

/* Progress bar section */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-muted);
}

.progress-track-glass {
  width: 100%;
  height: 10px;
  background: rgba(148, 163, 184, 0.12);
  border-radius: 999px;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
  border: 1.5px solid rgba(255, 255, 255, 0.5);
}

.progress-fill-gradient {
  height: 100%;
  border-radius: 999px;
  width: 0;
  transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.bg-green {
  background: linear-gradient(90deg, #4ADE80 0%, #22C55E 100%);
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.3);
}

.bg-blue {
  background: linear-gradient(90deg, #38BDF8 0%, #0284C7 100%);
  box-shadow: 0 0 8px rgba(14, 165, 233, 0.3);
}

.bg-amber {
  background: linear-gradient(90deg, #FDE047 0%, #EAB308 100%);
  box-shadow: 0 0 8px rgba(234, 179, 8, 0.3);
}

.bg-red {
  background: linear-gradient(90deg, #F87171 0%, #EF4444 100%);
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.3);
}

/* Skills Section */
.skills-section {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.skills-title {
  margin: 0;
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.85;
}

.skills-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.skill-pill {
  display: inline-block;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  font-weight: 650;
  font-size: 0.78rem;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.05), rgba(99, 102, 241, 0.08));
  border: 1px solid rgba(14, 165, 233, 0.22);
  color: var(--primary-dark);
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  cursor: default;
}

.skill-pill:hover {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(99, 102, 241, 0.15));
  transform: translateY(-1.5px);
  box-shadow: 0 4px 10px rgba(14, 165, 233, 0.15);
}

/* Card Actions styling */
.card-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-action {
  flex: 1;
  padding: 0.65rem 0.8rem;
  border-radius: 12px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
}

.btn-interview {
  background: rgba(34, 197, 94, 0.12);
  color: #16A34A;
  border-color: rgba(34, 197, 94, 0.22);
}

.btn-interview:hover {
  background: #16A34A;
  color: white;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.25);
}

.btn-reject {
  background: rgba(239, 68, 68, 0.12);
  color: #DC2626;
  border-color: rgba(239, 68, 68, 0.22);
}

.btn-reject:hover {
  background: #DC2626;
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}
</style>
