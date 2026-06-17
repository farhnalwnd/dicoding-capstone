<template>
  <div class="advisor-container">
    <!-- Header -->
    <header class="advisor-header glass-panel">
      <div class="header-content">
        <span class="advisor-badge">
          <span class="badge-dot"></span>
          AI Resume Advisor — Powered by Gemini
        </span>
        <h2>Your Personalized Career Roadmap</h2>
        <p class="advisor-subtitle">
          AI-generated recommendations based on your CV-JD match analysis.
        </p>
      </div>
      <div class="header-score-pill" v-if="analysisData">
        <span class="score-label">Current Match</span>
        <span class="score-number" :class="scoreClass">{{ analysisData.match_score }}%</span>
      </div>
    </header>

    <!-- No Data State -->
    <div v-if="!analysisData" class="empty-advisor glass-panel">
      <div class="empty-advisor-icon">🤖</div>
      <h3>No Analysis Data Found</h3>
      <p>
        Please complete a <strong>CV-JD Analysis</strong> first. Your analysis results will automatically
        appear here for AI-powered recommendations.
      </p>
      <router-link to="/jobseeker/analyze" class="btn-primary" id="go-analyze-btn">
        Go to CV-JD Analysis →
      </router-link>
    </div>

    <!-- Main Content -->
    <div v-else class="advisor-content">

      <!-- CTA: Generate / Regenerate -->
      <div v-if="!recommendations && !loading" class="generate-cta glass-panel">
        <div class="cta-icon-wrap">🚀</div>
        <div class="cta-text">
          <h3>Ready to get your personalized plan?</h3>
          <p>Click below to generate your AI-driven learning roadmap, resume tips, and career insights.</p>
        </div>
        <button id="generate-advisor-btn" class="btn-primary" @click="generateAdvisor" :disabled="loading">
          Generate AI Recommendations
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="advisor-loading glass-panel">
        <div class="spinner-ring"></div>
        <p>Analyzing your profile with AI...</p>
        <p class="loading-sub">This may take a few seconds</p>
      </div>

      <!-- Error Banner -->
      <div v-if="errorMessage && !loading" class="error-banner glass-panel">
        <span class="error-icon">⚠️</span>
        <span>{{ errorMessage }}</span>
        <button class="btn-retry" @click="generateAdvisor">Retry</button>
      </div>

      <!-- Results Panel -->
      <div v-if="recommendations && !loading" class="results-grid">

        <!-- Score Improvement Card -->
        <div class="result-card glass-panel score-improvement-card">
          <div class="card-header">
            <span class="card-icon-wrap teal-icon">📈</span>
            <h3>Score Improvement Potential</h3>
          </div>
          <div class="score-comparison">
            <div class="score-item">
              <span class="score-item-label">Current Score</span>
              <div class="score-ring" :class="scoreClass">
                <span>{{ recommendations.current_score }}%</span>
              </div>
            </div>
            <div class="score-arrow">→</div>
            <div class="score-item">
              <span class="score-item-label">Potential Score</span>
              <div class="score-ring score-ring-green">
                <span>{{ recommendations.estimated_score }}%</span>
              </div>
            </div>
          </div>
          <p class="score-delta-note">
            +{{ (recommendations.estimated_score - recommendations.current_score).toFixed(1) }}% estimated improvement after applying recommendations
          </p>
        </div>

        <!-- Missing Skills Summary -->
        <div class="result-card glass-panel">
          <div class="card-header">
            <span class="card-icon-wrap red-icon">🎯</span>
            <h3>Skills Assessment</h3>
          </div>
          <p class="skills-summary-text">{{ recommendations.missing_skills_summary }}</p>

          <!-- Matched Skills -->
          <div v-if="analysisData.matched_skills?.length" class="skills-section">
            <span class="section-mini-title matched-title">Matched Skills</span>
            <div class="skill-tags">
              <span
                v-for="skill in analysisData.matched_skills"
                :key="skill"
                class="skill-chip chip-green"
              >{{ skill }}</span>
            </div>
          </div>

          <!-- Missing Skills -->
          <div v-if="analysisData.missing_skills?.length" class="skills-section">
            <span class="section-mini-title missing-title">Missing Skills</span>
            <div class="skill-tags">
              <span
                v-for="skill in analysisData.missing_skills"
                :key="skill"
                class="skill-chip chip-red"
              >{{ skill }}</span>
            </div>
          </div>
        </div>

        <!-- Learning Roadmap -->
        <div class="result-card glass-panel full-width-card">
          <div class="card-header">
            <span class="card-icon-wrap purple-icon">🗺️</span>
            <h3>Week-by-Week Learning Roadmap</h3>
          </div>
          <div class="timeline">
            <div
              v-for="(plan, index) in recommendations.learning_plan"
              :key="index"
              class="timeline-item"
              :class="{ 'is-last': index === recommendations.learning_plan.length - 1 }"
            >
              <div class="timeline-dot"></div>
              <div class="timeline-body">
                <span class="timeline-duration">{{ plan.duration }}</span>
                <ul class="timeline-tasks">
                  <li v-for="(task, ti) in plan.tasks" :key="ti">{{ task }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Resume Tips -->
        <div class="result-card glass-panel">
          <div class="card-header">
            <span class="card-icon-wrap amber-icon">📝</span>
            <h3>Resume Optimization Tips</h3>
          </div>
          <ul class="tips-list">
            <li
              v-for="(tip, i) in recommendations.resume_tips"
              :key="i"
              class="tip-item"
            >
              <span class="tip-bullet">✓</span>
              {{ tip }}
            </li>
          </ul>
        </div>

        <!-- Interview Tips -->
        <div class="result-card glass-panel">
          <div class="card-header">
            <span class="card-icon-wrap blue-icon">🎤</span>
            <h3>Interview Preparation</h3>
          </div>
          <ul class="tips-list">
            <li
              v-for="(tip, i) in recommendations.interview_tips"
              :key="i"
              class="tip-item"
            >
              <span class="tip-bullet tip-bullet-blue">→</span>
              {{ tip }}
            </li>
          </ul>
        </div>

        <!-- Career Insights -->
        <div class="result-card glass-panel full-width-card career-card">
          <div class="card-header">
            <span class="card-icon-wrap indigo-icon">🚀</span>
            <h3>AI Career Insights</h3>
          </div>
          <p class="career-suitability">{{ recommendations.career_recommendations?.career_suitability }}</p>

          <div class="career-chips-row">
            <div class="career-chip-group">
              <span class="career-chip-label">Recommended Roles</span>
              <div class="skill-tags">
                <span
                  v-for="role in recommendations.career_recommendations?.recommended_roles"
                  :key="role"
                  class="skill-chip chip-indigo"
                >{{ role }}</span>
              </div>
            </div>
            <div class="career-chip-group">
              <span class="career-chip-label">Technologies to Learn</span>
              <div class="skill-tags">
                <span
                  v-for="tech in recommendations.career_recommendations?.recommended_technologies"
                  :key="tech"
                  class="skill-chip chip-teal"
                >{{ tech }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions Row -->
        <div class="actions-row full-width-card">
          <button id="export-pdf-btn" class="btn-export" @click="exportPdf" :disabled="exportLoading">
            <span>{{ exportLoading ? 'Generating PDF...' : '⬇ Download PDF Report' }}</span>
          </button>
          <button id="regenerate-btn" class="btn-secondary" @click="generateAdvisor" :disabled="loading">
            🔄 Regenerate
          </button>
          <router-link to="/jobseeker/analyze" class="btn-secondary">
            ← Back to Analysis
          </router-link>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const toast = inject('toast')

const analysisData = ref(null)
const recommendations = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const exportLoading = ref(false)

const scoreClass = computed(() => {
  if (!analysisData.value) return ''
  const s = analysisData.value.match_score
  if (s < 30) return 'ring-danger'
  if (s < 50) return 'ring-warning'
  if (s < 75) return 'ring-moderate'
  return 'ring-success'
})

onMounted(() => {
  // Load saved analysis result from localStorage
  try {
    const saved = localStorage.getItem('advisor_analysis')
    if (saved) {
      analysisData.value = JSON.parse(saved)
    }
  } catch (e) {
    console.error('Failed to load analysis data', e)
  }
})

const generateAdvisor = async () => {
  if (!analysisData.value) return
  loading.value = true
  errorMessage.value = ''
  recommendations.value = null

  try {
    const token = localStorage.getItem('token') || ''
    const res = await axios.post(
      `${API_BASE_URL}/api/resume-advisor`,
      {
        match_score: analysisData.value.match_score,
        matched_skills: analysisData.value.matched_skills || [],
        missing_skills: analysisData.value.missing_skills || [],
        recommendation: analysisData.value.recommendation || 'N/A',
        job_description: analysisData.value.job_description || ''
      },
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    recommendations.value = res.data
    toast?.success('AI recommendations generated successfully!')
  } catch (err) {
    console.error(err)
    errorMessage.value = err?.response?.data?.detail || 'Failed to generate AI recommendations. Please try again.'
    toast?.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}

const exportPdf = async () => {
  if (!recommendations.value) return
  exportLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const res = await axios.post(
      `${API_BASE_URL}/api/resume-advisor/export`,
      recommendations.value,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    )
    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
    const a = document.createElement('a')
    a.href = url
    a.download = 'AI_Resume_Advisor_Report.pdf'
    a.click()
    window.URL.revokeObjectURL(url)
    toast?.success('PDF report downloaded successfully!')
  } catch (err) {
    console.error(err)
    toast?.error('Failed to export PDF. Please try again.')
  } finally {
    exportLoading.value = false
  }
}
</script>

<style scoped>
.advisor-container {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

/* Header */
.advisor-header {
  padding: 2.2rem 2.8rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  position: relative;
  overflow: hidden;
}

.advisor-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 8% 20%, rgba(139, 92, 246, 0.1), transparent 30%),
              radial-gradient(circle at 90% 80%, rgba(14, 165, 233, 0.08), transparent 25%);
  pointer-events: none;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.advisor-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 999px;
  border: 1px solid rgba(139, 92, 246, 0.3);
  background: rgba(139, 92, 246, 0.1);
  color: #7C3AED;
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.35rem 0.8rem;
}

.badge-dot {
  width: 0.44rem;
  height: 0.44rem;
  border-radius: 999px;
  background: #8B5CF6;
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2);
}

.advisor-subtitle {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.95rem;
}

.header-score-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  flex-shrink: 0;
}

.score-label {
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.score-number {
  font-size: 2.2rem;
  font-weight: 900;
  line-height: 1;
}

.score-number.ring-success { color: #16A34A; }
.score-number.ring-moderate { color: #0EA5E9; }
.score-number.ring-warning { color: #D97706; }
.score-number.ring-danger { color: #DC2626; }

/* Empty State */
.empty-advisor {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-advisor-icon {
  font-size: 3.5rem;
  filter: drop-shadow(0 8px 20px rgba(139, 92, 246, 0.25));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.empty-advisor h3 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-soft);
}

.empty-advisor p {
  color: var(--text-muted);
  max-width: 420px;
  line-height: 1.6;
  margin: 0;
}

/* Generate CTA */
.generate-cta {
  display: flex;
  align-items: center;
  gap: 1.75rem;
  padding: 2rem 2.5rem;
}

.cta-icon-wrap {
  font-size: 2.5rem;
  filter: drop-shadow(0 4px 12px rgba(139, 92, 246, 0.3));
  flex-shrink: 0;
  animation: float 3s ease-in-out infinite;
}

.cta-text h3 {
  margin: 0 0 0.3rem;
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-soft);
}

.cta-text p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted);
}

/* Loading */
.advisor-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
}

.spinner-ring {
  width: 52px;
  height: 52px;
  border: 4px solid rgba(139, 92, 246, 0.15);
  border-top-color: #8B5CF6;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-sub {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.75rem;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 16px;
  color: #DC2626;
  font-weight: 600;
}

.btn-retry {
  background: #EF4444;
  color: white;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  margin-left: auto;
  transition: background 0.2s;
}

.btn-retry:hover { background: #DC2626; }

/* Results Grid */
.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.full-width-card {
  grid-column: 1 / -1;
}

.result-card {
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Card Header */
.card-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-soft);
}

.card-icon-wrap {
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  flex-shrink: 0;
}

.teal-icon   { background: rgba(20, 184, 166, 0.12); border: 1px solid rgba(20, 184, 166, 0.2); }
.red-icon    { background: rgba(239, 68, 68, 0.1);   border: 1px solid rgba(239, 68, 68, 0.18); }
.purple-icon { background: rgba(139, 92, 246, 0.12); border: 1px solid rgba(139, 92, 246, 0.2); }
.amber-icon  { background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.2); }
.blue-icon   { background: rgba(14, 165, 233, 0.12); border: 1px solid rgba(14, 165, 233, 0.2); }
.indigo-icon { background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.2); }

/* Score Comparison */
.score-comparison {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
}

.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.7rem;
}

.score-item-label {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.score-ring {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 900;
  border: 3px solid;
}

.score-ring.ring-success { border-color: #22C55E; color: #16A34A; background: rgba(34, 197, 94, 0.1); }
.score-ring.ring-moderate { border-color: #0EA5E9; color: #0369A1; background: rgba(14, 165, 233, 0.1); }
.score-ring.ring-warning { border-color: #F59E0B; color: #D97706; background: rgba(245, 158, 11, 0.1); }
.score-ring.ring-danger { border-color: #EF4444; color: #DC2626; background: rgba(239, 68, 68, 0.1); }
.score-ring-green { border-color: #22C55E; color: #16A34A; background: rgba(34, 197, 94, 0.12); }

.score-arrow {
  font-size: 1.5rem;
  color: var(--text-muted);
}

.score-delta-note {
  text-align: center;
  font-size: 0.85rem;
  color: #16A34A;
  font-weight: 700;
  margin: 0;
}

/* Skills */
.skills-summary-text {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-soft);
}

.skills-section {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.section-mini-title {
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.matched-title { color: #16A34A; }
.missing-title { color: #DC2626; }

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-chip {
  display: inline-block;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
  border: 1px solid;
  transition: transform 0.18s ease;
}

.skill-chip:hover { transform: scale(1.05); }

.chip-green  { background: rgba(34, 197, 94, 0.1);  border-color: rgba(34, 197, 94, 0.3);  color: #15803D; }
.chip-red    { background: rgba(239, 68, 68, 0.1);   border-color: rgba(239, 68, 68, 0.3);   color: #B91C1C; }
.chip-indigo { background: rgba(99, 102, 241, 0.1);  border-color: rgba(99, 102, 241, 0.3);  color: #4338CA; }
.chip-teal   { background: rgba(20, 184, 166, 0.1);  border-color: rgba(20, 184, 166, 0.3);  color: #0F766E; }

/* Timeline */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.timeline-item {
  display: flex;
  gap: 1.25rem;
  padding-bottom: 1.5rem;
  position: relative;
}

.timeline-item:not(.is-last)::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 20px;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, rgba(139, 92, 246, 0.4), rgba(139, 92, 246, 0.05));
}

.timeline-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8B5CF6, #6366F1);
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.15);
  flex-shrink: 0;
  margin-top: 2px;
}

.timeline-body {
  flex: 1;
}

.timeline-duration {
  display: inline-block;
  font-size: 0.82rem;
  font-weight: 800;
  color: #7C3AED;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  margin-bottom: 0.6rem;
}

.timeline-tasks {
  margin: 0;
  padding-left: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.timeline-tasks li {
  font-size: 0.92rem;
  color: var(--text-soft);
  line-height: 1.5;
}

/* Tips List */
.tips-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.tip-item {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  font-size: 0.93rem;
  color: var(--text-soft);
  line-height: 1.5;
}

.tip-bullet {
  flex-shrink: 0;
  font-weight: 900;
  color: #16A34A;
  margin-top: 1px;
}

.tip-bullet-blue { color: #0EA5E9; }

/* Career Card */
.career-suitability {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-soft);
  line-height: 1.6;
  font-style: italic;
  border-left: 3px solid rgba(99, 102, 241, 0.4);
  padding-left: 1rem;
}

.career-chips-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.career-chip-group {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.career-chip-label {
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Actions Row */
.actions-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-export {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #7C3AED, #6366F1);
  color: white;
  border: none;
  padding: 0.85rem 1.6rem;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35);
}

.btn-export:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(124, 58, 237, 0.45);
}

.btn-export:disabled { opacity: 0.65; cursor: not-allowed; }

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.6);
  color: var(--text-soft);
  border: 1px solid var(--glass-border);
  padding: 0.8rem 1.4rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.85);
  transform: translateY(-1px);
}

.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }

/* Score Improvement Card special layout */
.score-improvement-card {
  text-align: center;
}

@media (max-width: 860px) {
  .results-grid {
    grid-template-columns: 1fr;
  }

  .full-width-card {
    grid-column: auto;
  }

  .career-chips-row {
    grid-template-columns: 1fr;
  }

  .advisor-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .generate-cta {
    flex-direction: column;
    text-align: center;
  }
}
</style>
