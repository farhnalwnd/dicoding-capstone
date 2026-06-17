<template>
  <div class="glass-panel ranking-card" :class="borderClass">
    <div class="card-header">
      <div class="rank-info">
        <span class="rank-badge">Rank #{{ rank }}</span>
        <h4 class="candidate-name">{{ name }}</h4>
      </div>
      
      <div class="score-badge" :class="scoreClass">
        <span class="score-pct">{{ score.toFixed(1) }}%</span>
        <span class="score-lbl">Match</span>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="progress-container">
      <div class="progress-track">
        <div class="progress-fill" :class="progressFillClass" :style="{ width: score + '%' }"></div>
      </div>
    </div>

    <!-- Details/Metrics list -->
    <div class="card-details">
      <div class="detail-row">
        <span class="detail-label">Semantic Similarity</span>
        <span class="detail-val">{{ semanticScore !== undefined ? semanticScore.toFixed(1) + '%' : '-' }}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Domain Skill Match</span>
        <span class="detail-val">{{ skillScore !== undefined ? skillScore.toFixed(1) + '%' : '-' }}</span>
      </div>
      <div class="detail-row" v-if="matchedCount !== undefined && missingCount !== undefined">
        <span class="detail-label">Core Skills</span>
        <span class="detail-val text-success">
          {{ matchedCount }} Match <span class="text-muted">/</span> <span class="text-danger">{{ missingCount }} Miss</span>
        </span>
      </div>
      <div class="detail-row file-row" v-if="filename">
        <span class="detail-label">File</span>
        <span class="detail-val filename">{{ filename }}</span>
      </div>
    </div>

    <!-- Actions row (only shown if status is 'screening' and showActions is true) -->
    <div class="card-actions" v-if="status === 'screening' && showActions">
      <button 
        type="button" 
        class="btn-action btn-pool"
        @click.stop="$emit('move-to-talent-pool')"
      >
        <span>👥</span> Move to Talent Pool
      </button>
      <button 
        type="button" 
        class="btn-action btn-interview"
        @click.stop="$emit('move-to-interview')"
      >
        <span>📅</span> Move to Interview
      </button>
    </div>
    
    <!-- Status display if not screening -->
    <div class="status-display" v-else-if="status">
      <span class="status-label-text">Status:</span>
      <CandidateStatusBadge :status="status" />
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
  rank: {
    type: Number,
    required: true
  },
  semanticScore: {
    type: Number,
    default: undefined
  },
  skillScore: {
    type: Number,
    default: undefined
  },
  matchedCount: {
    type: Number,
    default: undefined
  },
  missingCount: {
    type: Number,
    default: undefined
  },
  filename: {
    type: String,
    default: ''
  },
  status: {
    type: String,
    default: 'screening'
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

defineEmits(['move-to-talent-pool', 'move-to-interview'])

// Dynamic border highlight based on score
const borderClass = computed(() => {
  if (props.score >= 90) return 'border-green'
  if (props.score >= 75) return 'border-blue'
  if (props.score >= 60) return 'border-amber'
  return 'border-red'
})

// Dynamic classes for score badge
const scoreClass = computed(() => {
  if (props.score >= 90) return 'score-green'
  if (props.score >= 75) return 'score-blue'
  if (props.score >= 60) return 'score-amber'
  return 'score-red'
})

// Dynamic progress bar classes
const progressFillClass = computed(() => {
  if (props.score >= 90) return 'fill-green'
  if (props.score >= 75) return 'fill-blue'
  if (props.score >= 60) return 'fill-amber'
  return 'fill-red'
})
</script>

<style scoped>
.ranking-card {
  padding: 1.5rem;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.62);
  border: 1.5px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.ranking-card:hover {
  transform: translateY(-2.5px);
  box-shadow: var(--shadow-strong);
}

/* Border Styles */
.border-green:hover {
  border-color: rgba(34, 197, 94, 0.5);
}
.border-blue:hover {
  border-color: rgba(14, 165, 233, 0.5);
}
.border-amber:hover {
  border-color: rgba(245, 158, 11, 0.5);
}
.border-red:hover {
  border-color: rgba(239, 68, 68, 0.5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.85rem;
}

.rank-info {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.rank-badge {
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
  color: var(--primary-dark);
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.15);
  padding: 0.2rem 0.55rem;
  border-radius: 8px;
  align-self: flex-start;
  letter-spacing: 0.5px;
}

.candidate-name {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-soft);
}

/* Score Badges */
.score-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.45rem 0.75rem;
  border-radius: 14px;
  border: 1px solid;
  min-width: 65px;
}

.score-pct {
  font-size: 1rem;
  font-weight: 900;
  line-height: 1;
}

.score-lbl {
  font-size: 0.55rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.85;
}

.score-green {
  background: rgba(34, 197, 94, 0.08);
  border-color: rgba(34, 197, 94, 0.25);
  color: #16A34A;
}

.score-blue {
  background: rgba(14, 165, 233, 0.08);
  border-color: rgba(14, 165, 233, 0.25);
  color: #0284C7;
}

.score-amber {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.25);
  color: #D97706;
}

.score-red {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.25);
  color: #DC2626;
}

/* Progress bar styling */
.progress-container {
  width: 100%;
}

.progress-track {
  width: 100%;
  height: 8px;
  background: rgba(148, 163, 184, 0.1);
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  width: 0;
  transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.fill-green {
  background: linear-gradient(90deg, #4ADE80 0%, #22C55E 100%);
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.25);
}

.fill-blue {
  background: linear-gradient(90deg, #38BDF8 0%, #0284C7 100%);
  box-shadow: 0 0 6px rgba(14, 165, 233, 0.25);
}

.fill-amber {
  background: linear-gradient(90deg, #FDE047 0%, #EAB308 100%);
  box-shadow: 0 0 6px rgba(234, 179, 8, 0.25);
}

.fill-red {
  background: linear-gradient(90deg, #F87171 0%, #EF4444 100%);
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.25);
}

/* Details list styling */
.card-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border-top: 1px solid rgba(14, 116, 144, 0.06);
  padding-top: 0.85rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.78rem;
  font-weight: 700;
}

.detail-label {
  color: var(--text-muted);
}

.detail-val {
  color: var(--text-soft);
  text-align: right;
}

.text-success {
  color: #16A34A;
}

.text-danger {
  color: #DC2626;
}

.text-muted {
  color: var(--text-muted);
  font-weight: 500;
}

.file-row {
  font-size: 0.72rem;
  border-top: 1px dashed rgba(14, 116, 144, 0.05);
  padding-top: 0.4rem;
}

.filename {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--mono);
}

/* Card Actions styling */
.card-actions {
  display: flex;
  gap: 0.65rem;
  margin-top: 0.5rem;
  border-top: 1px solid rgba(14, 116, 144, 0.06);
  padding-top: 0.85rem;
}

.btn-action {
  flex: 1;
  padding: 0.55rem 0.65rem;
  border-radius: 10px;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
}

.btn-pool {
  background: rgba(99, 102, 241, 0.12);
  color: #4F46E5;
  border-color: rgba(99, 102, 241, 0.22);
}

.btn-pool:hover {
  background: #4F46E5;
  color: white;
  box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2);
}

.btn-interview {
  background: rgba(34, 197, 94, 0.12);
  color: #16A34A;
  border-color: rgba(34, 197, 94, 0.22);
}

.btn-interview:hover {
  background: #16A34A;
  color: white;
  box-shadow: 0 4px 10px rgba(34, 197, 94, 0.2);
}

/* Status display styling */
.status-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid rgba(14, 116, 144, 0.06);
  padding-top: 0.85rem;
  font-size: 0.78rem;
  font-weight: 700;
}

.status-label-text {
  color: var(--text-muted);
}
</style>
