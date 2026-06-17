<template>
  <div class="glass-panel best-candidate-card">
    <div class="best-candidate-badge">
      <span>🏆 Best Candidate</span>
    </div>

    <div class="card-content">
      <div class="header-section">
        <div class="name-area">
          <h3 class="candidate-name">{{ name }}</h3>
          <span class="file-name" v-if="filename">📄 {{ filename }}</span>
        </div>
        <div class="score-badge">
          <span class="score-num">{{ score.toFixed(1) }}%</span>
          <span class="score-label">Match Score</span>
        </div>
      </div>

      <div class="progress-section">
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: score + '%' }"></div>
        </div>
      </div>

      <div class="metrics-grid">
        <div class="metric-box">
          <span class="metric-val">{{ semanticScore.toFixed(1) }}%</span>
          <span class="metric-lbl">Semantic Match</span>
        </div>
        <div class="metric-box">
          <span class="metric-val">{{ skillScore.toFixed(1) }}%</span>
          <span class="metric-lbl">Skill Coverage</span>
        </div>
        <div class="metric-box">
          <span class="metric-val">{{ matchedCount }}</span>
          <span class="metric-lbl">Matched Skills</span>
        </div>
        <div class="metric-box">
          <span class="metric-val text-danger">{{ missingCount }}</span>
          <span class="metric-lbl">Missing Skills</span>
        </div>
      </div>

      <!-- Skill Breakdown tags -->
      <div class="skills-breakdown" v-if="matchedSkills.length || missingSkills.length">
        <div class="skills-col" v-if="matchedSkills.length">
          <h4 class="col-title text-success">✓ Matched Core Skills</h4>
          <div class="skills-pills">
            <span v-for="skill in matchedSkills.slice(0, 6)" :key="skill" class="skill-pill matched-pill">
              {{ skill }}
            </span>
            <span v-if="matchedSkills.length > 6" class="more-count">+{{ matchedSkills.length - 6 }} more</span>
          </div>
        </div>

        <div class="skills-col" v-if="missingSkills.length">
          <h4 class="col-title text-danger">× Missing Core Skills</h4>
          <div class="skills-pills">
            <span v-for="skill in missingSkills.slice(0, 6)" :key="skill" class="skill-pill missing-pill">
              {{ skill }}
            </span>
            <span v-if="missingSkills.length > 6" class="more-count">+{{ missingSkills.length - 6 }} more</span>
          </div>
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
  semanticScore: {
    type: Number,
    default: 0
  },
  skillScore: {
    type: Number,
    default: 0
  },
  matchedCount: {
    type: Number,
    default: 0
  },
  missingCount: {
    type: Number,
    default: 0
  },
  matchedSkills: {
    type: Array,
    default: () => []
  },
  missingSkills: {
    type: Array,
    default: () => []
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
</script>

<style scoped>
.best-candidate-card {
  padding: 2.2rem;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.72);
  border: 2.5px solid rgba(234, 179, 8, 0.45);
  box-shadow: 0 20px 50px rgba(234, 179, 8, 0.18), var(--shadow-soft);
  position: relative;
  overflow: visible;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.best-candidate-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 28px 60px rgba(234, 179, 8, 0.26), var(--shadow-strong);
  border-color: rgba(234, 179, 8, 0.65);
}

.best-candidate-badge {
  position: absolute;
  top: -14px;
  left: 28px;
  background: linear-gradient(135deg, #EAB308 0%, #D97706 100%);
  color: white;
  padding: 0.45rem 1.2rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 850;
  letter-spacing: 0.6px;
  box-shadow: 0 8px 22px rgba(234, 179, 8, 0.45);
  z-index: 2;
  text-transform: uppercase;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.candidate-name {
  margin: 0;
  font-size: 1.55rem;
  font-weight: 850;
  color: var(--text-soft);
}

.file-name {
  display: inline-block;
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-top: 0.35rem;
  font-weight: 500;
}

.score-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(234, 179, 8, 0.08);
  border: 1.5px solid rgba(234, 179, 8, 0.3);
  padding: 0.55rem 1rem;
  border-radius: 18px;
  color: #D97706;
  min-width: 95px;
}

.score-num {
  font-size: 1.35rem;
  font-weight: 900;
  line-height: 1.1;
}

.score-label {
  font-size: 0.58rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.9;
}

.progress-section {
  width: 100%;
}

.progress-track {
  width: 100%;
  height: 12px;
  background: rgba(148, 163, 184, 0.12);
  border-radius: 999px;
  overflow: hidden;
  border: 1.5px solid rgba(255, 255, 255, 0.65);
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #FDE047 0%, #EAB308 50%, #D97706 100%);
  box-shadow: 0 0 12px rgba(234, 179, 8, 0.5);
  transition: width 1.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.85rem;
}

.metric-box {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(14, 116, 144, 0.08);
  padding: 0.75rem 0.5rem;
  border-radius: 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.metric-val {
  font-size: 1.1rem;
  font-weight: 850;
  color: var(--text-soft);
}

.metric-lbl {
  font-size: 0.64rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-top: 0.2rem;
  letter-spacing: 0.2px;
}

.text-danger {
  color: var(--danger);
}

.skills-breakdown {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  border-top: 1px dashed rgba(14, 116, 144, 0.12);
  padding-top: 1.2rem;
}

.skills-col {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.col-title {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.text-success {
  color: #16A34A;
}

.skills-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.skill-pill {
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.3rem 0.65rem;
  border-radius: 8px;
  cursor: default;
}

.matched-pill {
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.2);
  color: #16A34A;
}

.missing-pill {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #DC2626;
}

.more-count {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 700;
  align-self: center;
}

/* Card Actions styling */
.card-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
  border-top: 1px solid rgba(14, 116, 144, 0.06);
  padding-top: 1.2rem;
}

.btn-action {
  flex: 1;
  padding: 0.7rem 0.8rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
}

.btn-pool {
  background: rgba(99, 102, 241, 0.12);
  color: #4F46E5;
  border-color: rgba(99, 102, 241, 0.22);
}

.btn-pool:hover {
  background: #4F46E5;
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
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

/* Status display styling */
.status-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid rgba(14, 116, 144, 0.06);
  padding-top: 1.2rem;
  font-size: 0.85rem;
  font-weight: 700;
}

.status-label-text {
  color: var(--text-muted);
}

@media (max-width: 600px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .skills-breakdown {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>
