<template>
  <div class="job-card">
    <div class="job-header">
      <div class="job-rank">#{{ rank }}</div>
      <div class="job-score" :class="scoreClass">{{ score }}%</div>
    </div>
    <div class="job-body">
      <a :href="url" target="_blank" class="job-title">{{ title }}</a>
      <div class="job-company">{{ company }}</div>
      <div class="job-location">📍 {{ location }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  rank: {
    type: Number,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  company: {
    type: String,
    required: true
  },
  location: {
    type: String,
    required: true
  },
  score: {
    type: Number,
    required: true
  },
  url: {
    type: String,
    required: true
  }
})

const scoreClass = computed(() => {
  if (props.score >= 80) return 'score-high'
  if (props.score >= 60) return 'score-medium'
  return 'score-low'
})
</script>

<style scoped>
.job-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(3, 105, 161, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.job-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-sm);
  border-color: rgba(3, 105, 161, 0.4);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.job-rank {
  font-weight: 700;
  color: #0369A1;
  font-size: 0.9rem;
}

.job-score {
  font-weight: 700;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.85rem;
}

.score-high {
  background-color: rgba(34, 197, 94, 0.2);
  color: #16A34A;
}

.score-medium {
  background-color: rgba(59, 130, 246, 0.2);
  color: #1D4ED8;
}

.score-low {
  background-color: rgba(239, 68, 68, 0.2);
  color: #DC2626;
}

.job-body {
  flex: 1;
}

.job-title {
  display: block;
  font-weight: 600;
  color: #0369A1;
  text-decoration: none;
  margin-bottom: 0.5rem;
  font-size: 1.05rem;
  transition: color 0.2s ease;
}

.job-title:hover {
  color: #0EA5E9;
  text-decoration: underline;
}

.job-company {
  color: #0C4A6E;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.job-location {
  color: #475569;
  font-size: 0.9rem;
}
</style>
