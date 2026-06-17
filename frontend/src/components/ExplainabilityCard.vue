<template>
  <div class="glass-panel explain-card">
    
    <!-- Premium Domain Badge Header -->
    <div class="explain-card-header">
      <div v-if="domain" class="domain-badge-container">
        <span class="premium-domain-badge">
          <span class="pulse-dot"></span>
          {{ domain.toUpperCase() }} DOMAIN
        </span>
      </div>
      <h3 class="dashboard-title">🔍 AI Recruiter Dashboard</h3>
    </div>

    <!-- 1. Executive Summary Card (Hero Score & Table Details) -->
    <div class="summary-executive-card sub-glass-card">
      <div class="executive-grid">
        
        <!-- Left: Recommendation Hero Section (AI Score Card) -->
        <div class="hero-score-card" :class="colorTheme.colorClass">
          <div class="hero-glow"></div>
          <span class="hero-label">{{ colorTheme.label.toUpperCase() }}</span>
          <span class="hero-score">{{ Number(matchScore).toFixed(2) }}%</span>
          <span class="hero-subtext">Match Compatibility</span>
        </div>

        <!-- Right: AI Assessment Details Table -->
        <div class="executive-details">
          <h4 class="details-title">📄 AI Assessment Summary</h4>
          <div class="details-table">
            <div class="details-row">
              <span class="details-label">Match Score</span>
              <span class="details-value font-bold" :class="colorTheme.colorClass">{{ Number(matchScore).toFixed(2) }}%</span>
            </div>
            <div class="details-row">
              <span class="details-label">Recommendation</span>
              <span class="details-value font-bold" :class="colorTheme.colorClass">{{ colorTheme.label }}</span>
            </div>
            <div class="details-row">
              <span class="details-label">Coverage</span>
              <span class="details-value font-bold">{{ Number(skillCoverageRatio).toFixed(2) }}%</span>
            </div>
            <div class="details-row">
              <span class="details-label">Matched Skills</span>
              <span class="details-value text-success font-bold">{{ matchedSkills ? matchedSkills.length : 0 }}</span>
            </div>
            <div class="details-row">
              <span class="details-label">Missing Skills</span>
              <span class="details-value text-danger font-bold">{{ missingSkills ? missingSkills.length : 0 }}</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 2. Statistics Cards Row -->
    <div class="stats-cards-row">
      <div class="mini-stat-card sub-glass-card">
        <div class="stat-icon-wrapper success-bg">
          <span class="stat-icon text-success">✓</span>
        </div>
        <div class="stat-content">
          <span class="stat-label">Matched Skills</span>
          <span class="stat-number text-success">{{ matchedSkills ? matchedSkills.length : 0 }}</span>
        </div>
      </div>
      
      <div class="mini-stat-card sub-glass-card">
        <div class="stat-icon-wrapper danger-bg">
          <span class="stat-icon text-danger">×</span>
        </div>
        <div class="stat-content">
          <span class="stat-label">Missing Skills</span>
          <span class="stat-number text-danger">{{ missingSkills ? missingSkills.length : 0 }}</span>
        </div>
      </div>
      
      <div class="mini-stat-card sub-glass-card">
        <div class="stat-icon-wrapper primary-bg">
          <span class="stat-icon text-primary">📊</span>
        </div>
        <div class="stat-content">
          <span class="stat-label">Skill Coverage</span>
          <span class="stat-number text-primary">{{ Number(skillCoverageRatio).toFixed(2) }}%</span>
        </div>
      </div>
    </div>

    <!-- 3. Skills Analysis Section -->
    <div class="skills-analysis-section sub-glass-card">
      <h4 class="section-title">🛠️ Skills Analysis</h4>
      
      <!-- Progress Bar with Percentage Label Inside -->
      <div class="progress-bar-container">
        <span class="progress-label">Skill Coverage Ratio</span>
        <div class="modern-progress-track">
          <div 
            class="modern-progress-fill" 
            :class="colorTheme.progressClass"
            :style="{ width: skillCoverageRatio + '%' }"
          >
            <span class="progress-percentage-label" v-if="skillCoverageRatio >= 15">
              {{ Number(skillCoverageRatio).toFixed(2) }}%
            </span>
          </div>
          <span class="progress-percentage-label-outside" v-if="skillCoverageRatio < 15">
            {{ Number(skillCoverageRatio).toFixed(2) }}%
          </span>
        </div>
      </div>

      <!-- Skills Split Layout (Grid 2 Column on Desktop) -->
      <div class="skills-split-grid">
        <!-- Matched Skills Column -->
        <div class="skills-column matched-column">
          <h5 class="column-subtitle text-success">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Matched Skills
          </h5>
          <div class="pills-container">
            <span v-for="skill in matchedSkills" :key="skill" class="pill pill-success">
              {{ skill }}
            </span>
            <span v-if="!matchedSkills || !matchedSkills.length" class="empty-text">
              No matching skills identified.
            </span>
          </div>
        </div>

        <!-- Missing Skills Column -->
        <div class="skills-column missing-column">
          <h5 class="column-subtitle text-danger">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            Missing Skills
          </h5>
          <div class="pills-container">
            <span v-for="skill in missingSkills" :key="skill" class="pill pill-danger">
              {{ skill }}
            </span>
            <span v-if="!missingSkills || !missingSkills.length" class="empty-text text-success-light">
              Excellent! All required skills matched.
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. AI Reasoning Cards Section -->
    <div class="reasoning-section">
      <h4 class="section-title">🤖 AI Reasoning Analysis</h4>
      <div class="reasoning-cards-grid">
        <div v-for="(item, idx) in reasoning" :key="idx" class="reasoning-card-item sub-glass-card">
          <div class="reasoning-icon">
            <svg class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <p class="reasoning-text">{{ item }}</p>
        </div>
        <div v-if="!reasoning || !reasoning.length" class="reasoning-card-item sub-glass-card empty">
          <div class="reasoning-icon">✦</div>
          <p class="reasoning-text italic">No detailed reasoning explanation available.</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  matchScore: {
    type: [Number, String],
    default: 0
  },
  recommendation: {
    type: String,
    default: 'Low Match'
  },
  matchedSkills: {
    type: Array,
    default: () => []
  },
  missingSkills: {
    type: Array,
    default: () => []
  },
  skillCoverageRatio: {
    type: [Number, String],
    default: 0
  },
  reasoning: {
    type: Array,
    default: () => []
  },
  domain: {
    type: String,
    default: ''
  }
})

// 9. Score-Based Color and Recommendation Logic
const colorTheme = computed(() => {
  const score = Number(props.matchScore) || 0
  if (score >= 85) {
    return {
      name: 'strong',
      label: 'Strong Match',
      colorClass: 'theme-strong',
      progressClass: 'progress-fill-strong'
    }
  }
  if (score >= 70) {
    return {
      name: 'good',
      label: 'Good Match',
      colorClass: 'theme-good',
      progressClass: 'progress-fill-good'
    }
  }
  if (score >= 50) {
    return {
      name: 'moderate',
      label: 'Moderate Match',
      colorClass: 'theme-moderate',
      progressClass: 'progress-fill-moderate'
    }
  }
  return {
    name: 'low',
    label: 'Low Match',
    colorClass: 'theme-low',
    progressClass: 'progress-fill-low'
  }
})
</script>

<style scoped>
.explain-card {
  width: 100%;
  margin-top: 2rem;
  padding: 2.2rem;
  text-align: left;
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.explain-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(14, 116, 144, 0.08);
  padding-bottom: 1.2rem;
  margin-bottom: 1.8rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.dashboard-title {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 850;
  color: var(--text);
}

/* 8. Domain Badge Enhancement */
.domain-badge-container {
  display: flex;
  align-items: center;
}

.premium-domain-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.45rem 1rem;
  border-radius: 999px;
  background: rgba(14, 116, 144, 0.08);
  border: 1px solid rgba(14, 116, 144, 0.22);
  color: #0e7490;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 1px;
  box-shadow: 0 0 12px rgba(14, 116, 144, 0.05);
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #0ea5e9;
  box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.7);
  animation: pulse 1.6s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.6); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(14, 165, 233, 0); }
  100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(14, 165, 233, 0); }
}

.sub-glass-card {
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: var(--radius-lg);
  padding: 1.6rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.015);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.sub-glass-card:hover {
  transform: translateY(-2.5px);
  box-shadow: 0 12px 36px rgba(15, 23, 42, 0.035);
  background: rgba(255, 255, 255, 0.55);
}

.section-title {
  margin: 0 0 1.2rem;
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-soft);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 1px dashed rgba(14, 116, 144, 0.1);
  padding-bottom: 0.55rem;
}

/* 1. Executive Summary Card Layout */
.executive-grid {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 1.8rem;
}

@media (max-width: 900px) {
  .executive-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

/* 2. Recommendation Hero Score Card */
.hero-score-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2.2rem 1.6rem;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  text-align: center;
  border: 1px solid;
  transition: all 0.4s ease;
}

.hero-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 70%);
  pointer-events: none;
  mix-blend-mode: overlay;
}

.hero-label {
  font-size: 0.88rem;
  font-weight: 850;
  letter-spacing: 1.2px;
  margin-bottom: 0.8rem;
  z-index: 2;
}

.hero-score {
  font-size: 3rem;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -1px;
  margin-bottom: 0.8rem;
  z-index: 2;
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.35);
}

.hero-subtext {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  z-index: 2;
  opacity: 0.85;
}

/* Executive Details Table Styling */
.executive-details {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.details-title {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--primary-dark);
}

.details-table {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.details-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid rgba(14, 116, 144, 0.08);
}

.details-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.details-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-muted);
}

.details-value {
  font-size: 0.95rem;
  text-align: right;
}

.font-bold {
  font-weight: 800;
}

/* 3. Statistics Cards Row */
.stats-cards-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.2rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .stats-cards-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

.mini-stat-card {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  padding: 1.1rem 1.4rem;
  margin-bottom: 0; /* Override margin from sub-glass-card */
}

.stat-icon-wrapper {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 850;
  font-size: 1.25rem;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.03);
}

.success-bg {
  background-color: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.danger-bg {
  background-color: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.primary-bg {
  background-color: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(14, 165, 233, 0.25);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-number {
  font-size: 1.45rem;
  font-weight: 900;
  line-height: 1.2;
}

/* 6. Progress Bar Enhancement */
.progress-bar-container {
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.85);
  padding: 1.1rem 1.4rem;
  border-radius: 18px;
  margin-bottom: 1.6rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.progress-label {
  font-size: 0.88rem;
  font-weight: 800;
  color: var(--text-soft);
}

.modern-progress-track {
  width: 100%;
  height: 22px; /* Taller track to fit label inside */
  background: rgba(148, 163, 184, 0.12);
  border-radius: 999px;
  position: relative;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
}

.modern-progress-fill {
  height: 100%;
  border-radius: 999px;
  width: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 0.8rem;
  transition: width 1.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.3);
}

.progress-percentage-label {
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 850;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.25);
  animation: fadeInLabel 0.4s ease forwards;
  animation-delay: 1.2s;
  opacity: 0;
}

.progress-percentage-label-outside {
  position: absolute;
  left: calc(v-bind(skillCoverageRatio) * 1% + 10px);
  font-size: 0.78rem;
  font-weight: 850;
  color: var(--text-soft);
}

@keyframes fadeInLabel {
  to { opacity: 1; }
}

/* 4. Skills Analysis 2-Column Layout */
.skills-split-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.8rem;
}

@media (max-width: 900px) {
  .skills-split-grid {
    grid-template-columns: 1fr;
    gap: 1.4rem;
  }
}

.skills-column {
  padding: 0.5rem 0;
}

.column-subtitle {
  margin: 0 0 1rem;
  font-size: 0.95rem;
  font-weight: 850;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.column-subtitle.text-success { color: #16a34a; }
.column-subtitle.text-danger { color: #dc2626; }

.icon {
  width: 15px;
  height: 15px;
}

.pills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

/* 5. Better Skill Pills */
.pill {
  display: inline-block;
  padding: 0.45rem 1rem;
  border-radius: 999px;
  font-weight: 650;
  font-size: 0.82rem;
  border: 1px solid;
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  cursor: default;
  box-shadow: 0 2px 4px rgba(15, 23, 42, 0.02);
}

.pill-success {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), rgba(74, 222, 128, 0.08));
  border-color: rgba(34, 197, 94, 0.3);
  color: #16a34a;
}

.pill-success:hover {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.12), rgba(74, 222, 128, 0.15));
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(34, 197, 94, 0.18);
}

.pill-danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), rgba(248, 113, 113, 0.08));
  border-color: rgba(239, 68, 68, 0.3);
  color: #dc2626;
}

.pill-danger:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(248, 113, 113, 0.15));
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(239, 68, 68, 0.18);
}

.empty-text {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
}

.text-success-light {
  color: #16a34a !important;
  font-weight: 650;
}

/* 7. AI Reasoning Cards Layout */
.reasoning-section {
  margin-top: 1rem;
}

.reasoning-cards-grid {
  display: flex;
  flex-direction: column;
  gap: 0.95rem;
}

.reasoning-card-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.2rem 1.6rem;
  margin-bottom: 0; /* Override margin from sub-glass-card */
  border-radius: 18px;
  animation: slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
}

.reasoning-card-item:nth-child(1) { animation-delay: 0.15s; }
.reasoning-card-item:nth-child(2) { animation-delay: 0.25s; }
.reasoning-card-item:nth-child(3) { animation-delay: 0.35s; }

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-15px); }
  to { opacity: 1; transform: translateX(0); }
}

.reasoning-card-item:hover {
  transform: translateX(4px) translateY(-1px);
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(14, 116, 144, 0.18);
}

.reasoning-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.2);
  color: var(--secondary);
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.check-icon {
  width: 14px;
  height: 14px;
  color: var(--secondary);
}

.reasoning-text {
  margin: 0;
  font-size: 0.94rem;
  line-height: 1.55;
  color: var(--text);
}

.reasoning-card-item.empty {
  color: var(--text-muted);
  animation: none;
  opacity: 1;
}

.italic {
  font-style: italic;
}

/* 9. Score-Based Themes Styling (Colors & Glows) */
.theme-strong {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.12), rgba(74, 222, 128, 0.18)) !important;
  border-color: rgba(34, 197, 94, 0.4) !important;
  color: #16a34a !important;
  box-shadow: 0 12px 32px rgba(34, 197, 94, 0.12), inset 0 2px 4px rgba(255,255,255,0.6) !important;
}
.theme-good {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(56, 189, 248, 0.18)) !important;
  border-color: rgba(14, 165, 233, 0.4) !important;
  color: var(--accent) !important;
  box-shadow: 0 12px 32px rgba(14, 165, 233, 0.12), inset 0 2px 4px rgba(255,255,255,0.6) !important;
}
.theme-moderate {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(251, 191, 36, 0.18)) !important;
  border-color: rgba(245, 158, 11, 0.4) !important;
  color: #d97706 !important;
  box-shadow: 0 12px 32px rgba(245, 158, 11, 0.08), inset 0 2px 4px rgba(255,255,255,0.6) !important;
}
.theme-low {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(248, 113, 113, 0.18)) !important;
  border-color: rgba(239, 68, 68, 0.4) !important;
  color: #dc2626 !important;
  box-shadow: 0 12px 32px rgba(239, 68, 68, 0.08), inset 0 2px 4px rgba(255,255,255,0.6) !important;
}

/* Score Texts */
.score-text.theme-strong {
  background: linear-gradient(135deg, #16a34a, #22c55e);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent !important;
}
.score-text.theme-good {
  background: linear-gradient(135deg, var(--accent), #0ea5e9);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent !important;
}
.score-text.theme-moderate {
  background: linear-gradient(135deg, #d97706, #f59e0b);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent !important;
}
.score-text.theme-low {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent !important;
}

/* Progress Fills */
.progress-fill-strong { background: linear-gradient(90deg, #22c55e, #4ade80); }
.progress-fill-good { background: linear-gradient(90deg, #0ea5e9, #38bdf8); }
.progress-fill-moderate { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.progress-fill-low { background: linear-gradient(90deg, #ef4444, #f87171); }
</style>
