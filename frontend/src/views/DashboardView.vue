<template>
  <div class="dashboard-container">
    <!-- Welcome Header -->
    <header class="dashboard-header glass-panel">
      <div class="header-content">
        <span class="role-badge">
          <span class="badge-dot"></span>
          {{ isHrRole ? 'HR Recruiter Account' : 'Job Seeker Account' }}
        </span>
        <h2 style="font-size: 1.25rem; font-weight: 700;">Welcome back, {{ userName }}!</h2>
        <p class="subtitle-dashboard">Here is your recruitment overview and quick actions.</p>
      </div>
    </header>

    <!-- HR Dashboard Statistics Cards -->
    <div v-if="isHrRole" class="hr-stats-container">
      <div v-if="statsLoading" class="stats-loading-shimmer glass-panel">
        Loading recruitment statistics...
      </div>
      <div v-else-if="statsError" class="stats-error-banner glass-panel">
        ⚠️ Failed to load statistics. <button @click="fetchHrStats" class="btn-retry-stats">Retry</button>
      </div>
      <div v-else class="stats-row">
        <!-- Total Candidates -->
        <div class="stat-card glass-panel border-blue">
          <div class="stat-icon-bg primary-bg">👥</div>
          <div class="stat-details">
            <span class="stat-val">{{ hrStats.total_candidates }}</span>
            <span class="stat-lbl">Total Candidates</span>
          </div>
        </div>
        
        <!-- Screening -->
        <div class="stat-card glass-panel border-cyan">
          <div class="stat-icon-bg cyan-bg">🔍</div>
          <div class="stat-details">
            <span class="stat-val">{{ hrStats.screening }}</span>
            <span class="stat-lbl">Screening</span>
          </div>
        </div>

        <!-- Talent Pool -->
        <div class="stat-card glass-panel border-purple">
          <div class="stat-icon-bg purple-bg">📂</div>
          <div class="stat-details">
            <span class="stat-val">{{ hrStats.talent_pool }}</span>
            <span class="stat-lbl">Talent Pool</span>
          </div>
        </div>

        <!-- Interview -->
        <div class="stat-card glass-panel border-amber">
          <div class="stat-icon-bg amber-bg">📅</div>
          <div class="stat-details">
            <span class="stat-val">{{ hrStats.interview }}</span>
            <span class="stat-lbl">Interviews</span>
          </div>
        </div>

        <!-- Hired -->
        <div class="stat-card glass-panel border-green">
          <div class="stat-icon-bg green-bg">🎉</div>
          <div class="stat-details">
            <span class="stat-val">{{ hrStats.hired }}</span>
            <span class="stat-lbl">Hired</span>
          </div>
        </div>

        <!-- Rejected -->
        <div class="stat-card glass-panel border-red">
          <div class="stat-icon-bg red-bg">❌</div>
          <div class="stat-details">
            <span class="stat-val">{{ hrStats.rejected }}</span>
            <span class="stat-lbl">Rejected</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Layout Grid -->
    <div class="dashboard-grid">
      <!-- Profile Card -->
      <section class="profile-section glass-panel">
        <h3>User Profile Summary</h3>
        <div class="profile-details">
          <div class="profile-avatar">
            {{ userInitial }}
          </div>
          <div class="profile-info">
            <div class="info-row">
              <span class="info-label">Name</span>
              <span class="info-val">{{ userName }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Email</span>
              <span class="info-val">{{ userEmail }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Role</span>
              <span class="info-val capitalize">{{ userRoleName }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Provider</span>
              <span class="info-val capitalize">{{ userProvider }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Quick Actions / Features -->
      <section class="actions-section">
        <div class="section-title">
          <h3>Quick Actions</h3>
        </div>

        <!-- HR Actions -->
        <div v-if="isHrRole" class="actions-grid">
          <router-link to="/hr/rank-cv" class="action-card glass-panel">
            <span class="action-icon">🏆</span>
            <div class="action-content-card">
              <h4>Rank CV</h4>
              <p>Upload multiple resumes to match and rank them against a job description.</p>
              <span class="action-link-text">Open Module →</span>
            </div>
          </router-link>

          <router-link to="/hr/talent-pool" class="action-card glass-panel">
            <span class="action-icon">👥</span>
            <div class="action-content-card">
              <h4>Talent Pool Management</h4>
              <p>Store, filter, and track top matching profiles for future vacancies.</p>
              <span class="action-link-text">Open Module →</span>
            </div>
          </router-link>

          <router-link to="/hr/interviews" class="action-card glass-panel">
            <span class="action-icon">📅</span>
            <div class="action-content-card">
              <h4>AI Interview Scheduler</h4>
              <p>Generate screening questions and schedule video interviews automatically.</p>
              <span class="action-link-text">Open Module →</span>
            </div>
          </router-link>



          <router-link to="/hr-dashboard" class="action-card glass-panel">
            <span class="action-icon">📊</span>
            <div class="action-content-card">
              <h4>HR Analytics Dashboard</h4>
              <p>Track recruitment metrics, conversion pipelines, and skills demand using AI analytics.</p>
              <span class="action-link-text">Open Dashboard →</span>
            </div>
          </router-link>
        </div>

        <!-- Job Seeker Actions -->
        <div v-else class="actions-grid jobseeker">
          <router-link to="/jobseeker/analyze" class="action-card glass-panel">
            <span class="action-icon">📄</span>
            <div class="action-content-card">
              <h4>Check Resume</h4>
              <p>Analyze how well your resume matches a specific job description.</p>
              <span class="action-link-text">Analyze Now →</span>
            </div>
          </router-link>

          <router-link to="/jobseeker/scrape" class="action-card glass-panel">
            <span class="action-icon">🔍</span>
            <div class="action-content-card">
              <h4>Job Scraper</h4>
              <p>Scrape real job listings from LinkedIn based on keywords and location.</p>
              <span class="action-link-text">Scrape Jobs →</span>
            </div>
          </router-link>

          <router-link to="/resume-advisor" class="action-card glass-panel advisor-card">
            <span class="action-icon">🤖</span>
            <div class="action-content-card">
              <h4>AI Resume Advisor</h4>
              <p>Get personalized learning roadmap, resume tips, and career insights powered by Gemini.</p>
              <span class="action-link-text advisor-link-text">Open Advisor →</span>
            </div>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { authState } from '../stores/auth'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const user = computed(() => authState.user || {})

const userName = computed(() => user.value.name || 'User')
const userEmail = computed(() => user.value.email || '-')
const userRoleName = computed(() => user.value.role === 'hr' ? 'HR Recruiter' : 'Job Seeker')
const userProvider = computed(() => user.value.provider || 'email')
const isHrRole = computed(() => user.value.role === 'hr')

const userInitial = computed(() => {
  return userName.value.charAt(0).toUpperCase()
})

// HR Stats states
const hrStats = ref({
  total_candidates: 0,
  screening: 0,
  talent_pool: 0,
  interview: 0,
  rejected: 0,
  hired: 0
})
const statsLoading = ref(false)
const statsError = ref(false)

const fetchHrStats = async () => {
  if (!isHrRole.value) return
  statsLoading.value = true
  statsError.value = false
  try {
    const res = await axios.get(`${API_BASE_URL}/api/dashboard/hr-stats`)
    hrStats.value = res.data
  } catch (error) {
    console.error(error)
    statsError.value = true
  } finally {
    statsLoading.value = false
  }
}

onMounted(() => {
  fetchHrStats()
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1180px;
  margin: 0 auto;
}

.dashboard-header {
  padding: 2.2rem 2.8rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.dashboard-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 12% 18%, rgba(56, 189, 248, 0.08), transparent 26%);
  pointer-events: none;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid rgba(14, 165, 233, 0.25);
  background: rgba(14, 165, 233, 0.12);
  color: var(--primary-dark);
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.35rem 0.68rem;
  margin-bottom: 0.75rem;
}

.badge-dot {
  width: 0.44rem;
  height: 0.44rem;
  margin-right: 0.4rem;
  border-radius: 999px;
  background: #22C55E;
  box-shadow: 0 0 0 5px rgba(34, 197, 94, 0.15);
}

.subtitle-dashboard {
  color: var(--text-muted);
  margin: 0;
  font-size: 1rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 1.75rem;
}

/* Profile Card Styling */
.profile-section {
  padding: 2rem;
  height: fit-content;
}

.profile-section h3 {
  margin: 0 0 1.5rem;
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-soft);
}

.profile-details {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.profile-avatar {
  width: 5.5rem;
  height: 5.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--indigo) 100%);
  color: #FFFFFF;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2.5rem;
  font-weight: 800;
  box-shadow: var(--shadow-sm);
}

.profile-info {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-bottom: 1px solid rgba(14, 116, 144, 0.08);
  padding-bottom: 0.75rem;
}

.info-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-label {
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-val {
  font-size: 0.94rem;
  font-weight: 650;
  color: var(--text-soft);
  word-break: break-all;
}

.capitalize {
  text-transform: capitalize;
}

/* Action Section Styling */
.actions-section h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 850;
  color: var(--text-soft);
}

.section-title {
  margin-bottom: 1.25rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.2rem;
}

.actions-grid.jobseeker {
  grid-template-columns: repeat(3, 1fr);
}

/* Advisor card highlight */
.advisor-card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.06) 0%, rgba(99, 102, 241, 0.04) 100%) !important;
  border-color: rgba(139, 92, 246, 0.2) !important;
}

.advisor-card:hover:not(.disabled) {
  border-color: rgba(139, 92, 246, 0.4) !important;
  background: rgba(139, 92, 246, 0.1) !important;
}

.advisor-link-text {
  color: #7C3AED !important;
}

.action-card {
  display: flex;
  gap: 1.2rem;
  padding: 1.75rem;
  align-items: flex-start;
  text-decoration: none;
  color: inherit;
  position: relative;
  transition: all 0.25s ease;
  box-sizing: border-box;
}

.action-card:hover:not(.disabled) {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: var(--shadow-strong);
  border-color: rgba(255, 255, 255, 0.95);
}

.action-icon {
  font-size: 1.8rem;
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(99, 102, 241, 0.1));
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}

.action-content-card {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.action-content-card h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--primary-dark);
}

.action-content-card p {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--text-muted);
}

.action-link-text {
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--primary);
  margin-top: 0.5rem;
  transition: transform 0.2s ease;
}

.action-card:hover:not(.disabled) .action-link-text {
  transform: translateX(3px);
}

/* Disabled/Coming Soon State */
.action-card.disabled {
  opacity: 0.65;
  cursor: not-allowed;
  pointer-events: none;
}

.disabled-text {
  color: var(--text-muted);
}

.coming-soon-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 0.68rem;
  font-weight: 850;
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.12);
  color: var(--indigo);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

@media (max-width: 960px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .profile-section {
    height: auto;
  }
}

@media (max-width: 580px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
  .dashboard-header {
    padding: 1.5rem 1.8rem;
  }
  .action-card {
    flex-direction: column;
    gap: 1rem;
  }
}

/* HR Stats Cards Styling */
.hr-stats-container {
  margin-bottom: 2rem;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 640px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  transition: all 0.25s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-strong);
}

.stat-icon-bg {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.primary-bg {
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

.red-bg {
  background-color: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.green-bg {
  background-color: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.stat-details {
  display: flex;
  flex-direction: column;
}

.stat-val {
  font-size: 1.4rem;
  font-weight: 900;
  color: var(--text-soft);
  line-height: 1.2;
}

.stat-lbl {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Border Glows */
.border-blue:hover { border-color: rgba(14, 165, 233, 0.45); }
.border-cyan:hover { border-color: rgba(34, 211, 238, 0.45); }
.border-purple:hover { border-color: rgba(139, 92, 246, 0.45); }
.border-amber:hover { border-color: rgba(245, 158, 11, 0.45); }
.border-green:hover { border-color: rgba(34, 197, 94, 0.45); }
.border-red:hover { border-color: rgba(239, 68, 68, 0.45); }

.stats-loading-shimmer, .stats-error-banner {
  padding: 1.5rem;
  text-align: center;
  border-radius: 20px;
  font-weight: 700;
  color: var(--text-muted);
}

.btn-retry-stats {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.35rem 0.8rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  margin-left: 0.5rem;
}

.btn-retry-stats:hover {
  background: var(--primary-dark);
}
</style>
