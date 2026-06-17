<template>
  <div class="glass-panel leaderboard-card">
    <div class="card-header">
      <div class="header-icon">🏆</div>
      <h3 class="card-title">Ranking Leaderboard</h3>
    </div>

    <div class="leaderboard-list">
      <div 
        v-for="(candidate, index) in candidates" 
        :key="candidate.filename || candidate.name" 
        class="leaderboard-item"
        :class="getItemClass(index + 1)"
        style="cursor: pointer;"
        @click="$emit('select-candidate', candidate)"
      >
        <div class="rank-badge-col">
          <span v-if="index === 0" class="emoji-badge gold-glow">🥇</span>
          <span v-else-if="index === 1" class="emoji-badge silver-glow">🥈</span>
          <span v-else-if="index === 2" class="emoji-badge bronze-glow">🥉</span>
          <span v-else class="rank-number">#{{ index + 1 }}</span>
        </div>

        <div class="candidate-info">
          <div class="name-row-wrapper">
            <span class="candidate-name">{{ candidate.name }}</span>
            <CandidateStatusBadge v-if="candidate.status" :status="candidate.status" class="mini-status" />
          </div>
          <span class="candidate-file" v-if="candidate.filename">{{ candidate.filename }}</span>
        </div>

        <div class="score-col">
          <span class="score-percentage">{{ candidate.score.toFixed(1) }}%</span>
        </div>
      </div>
      
      <div v-if="!candidates.length" class="empty-list">
        No candidates available.
      </div>
    </div>
  </div>
</template>

<script setup>
import CandidateStatusBadge from './CandidateStatusBadge.vue'

const props = defineProps({
  candidates: {
    type: Array,
    required: true
  }
})

defineEmits(['select-candidate'])

const getItemClass = (rank) => {
  if (rank === 1) return 'rank-1-gold'
  if (rank === 2) return 'rank-2-silver'
  if (rank === 3) return 'rank-3-bronze'
  return 'rank-standard'
}
</script>

<style scoped>
.leaderboard-card {
  padding: 1.8rem;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(14, 116, 144, 0.08);
  padding-bottom: 1rem;
}

.header-icon {
  font-size: 1.4rem;
}

.card-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 850;
  color: var(--text-soft);
}

.leaderboard-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  padding: 0.95rem 1.2rem;
  border-radius: 18px;
  transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 1px solid transparent;
}

.leaderboard-item:hover {
  transform: translateX(4px);
}

/* Rank 1: Gold Style */
.rank-1-gold {
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.45) 0%, rgba(251, 191, 36, 0.12) 100%);
  border: 1.5px solid rgba(251, 191, 36, 0.45);
  box-shadow: 0 8px 20px rgba(251, 191, 36, 0.08);
}

.rank-1-gold:hover {
  box-shadow: 0 12px 28px rgba(251, 191, 36, 0.16);
  border-color: rgba(251, 191, 36, 0.65);
}

.rank-1-gold .candidate-name {
  color: #B45309;
  font-weight: 850;
}

.rank-1-gold .score-percentage {
  color: #B45309;
  font-weight: 900;
}

/* Rank 2: Silver Style */
.rank-2-silver {
  background: linear-gradient(135deg, rgba(241, 245, 249, 0.55) 0%, rgba(148, 163, 184, 0.12) 100%);
  border: 1.5px solid rgba(148, 163, 184, 0.4);
  box-shadow: 0 8px 20px rgba(148, 163, 184, 0.05);
}

.rank-2-silver:hover {
  box-shadow: 0 12px 28px rgba(148, 163, 184, 0.12);
  border-color: rgba(148, 163, 184, 0.6);
}

.rank-2-silver .candidate-name {
  color: #475569;
  font-weight: 800;
}

.rank-2-silver .score-percentage {
  color: #475569;
  font-weight: 850;
}

/* Rank 3: Bronze Style */
.rank-3-bronze {
  background: linear-gradient(135deg, rgba(255, 237, 213, 0.45) 0%, rgba(249, 115, 22, 0.08) 100%);
  border: 1.5px solid rgba(249, 115, 22, 0.35);
  box-shadow: 0 8px 20px rgba(249, 115, 22, 0.05);
}

.rank-3-bronze:hover {
  box-shadow: 0 12px 28px rgba(249, 115, 22, 0.12);
  border-color: rgba(249, 115, 22, 0.5);
}

.rank-3-bronze .candidate-name {
  color: #C2410C;
  font-weight: 800;
}

.rank-3-bronze .score-percentage {
  color: #C2410C;
  font-weight: 850;
}

/* Standard Rank Style */
.rank-standard {
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(148, 163, 184, 0.08);
}

.rank-standard:hover {
  background: rgba(255, 255, 255, 0.65);
  border-color: rgba(14, 165, 233, 0.2);
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.03);
}

.rank-standard .candidate-name {
  color: var(--text-soft);
  font-weight: 700;
}

.rank-standard .score-percentage {
  color: var(--text-soft);
  font-weight: 800;
}

/* Sub components */
.rank-badge-col {
  width: 50px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.emoji-badge {
  font-size: 1.5rem;
  line-height: 1;
}

.gold-glow {
  filter: drop-shadow(0 0 4px rgba(251, 191, 36, 0.6));
}

.silver-glow {
  filter: drop-shadow(0 0 4px rgba(148, 163, 184, 0.5));
}

.bronze-glow {
  filter: drop-shadow(0 0 4px rgba(249, 115, 22, 0.5));
}

.rank-number {
  font-size: 0.88rem;
  font-weight: 800;
  color: var(--text-muted);
  background: rgba(148, 163, 184, 0.08);
  padding: 0.2rem 0.5rem;
  border-radius: 8px;
}

.candidate-info {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  gap: 0.2rem;
}

.name-row-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.candidate-name {
  font-size: 1.05rem;
}

.mini-status {
  transform: scale(0.8);
  transform-origin: left center;
}

.candidate-file {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 500;
}

.score-col {
  flex-shrink: 0;
  font-size: 1.15rem;
  text-align: right;
}

.empty-list {
  text-align: center;
  color: var(--text-muted);
  font-style: italic;
  padding: 1rem 0;
}
</style>
