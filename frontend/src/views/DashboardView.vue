<template>
  <div class="dashboard-container">
    <!-- Welcome Header -->
    <header class="dashboard-header glass-panel">
      <div class="header-content">
        <span class="role-badge">
          <span class="badge-dot"></span>
          {{ isHrRole ? 'HR Recruiter Account' : 'Job Seeker Account' }}
        </span>
        <h2>Welcome back, {{ userName }}!</h2>
        <p class="subtitle-dashboard">Here is your recruitment overview and quick actions.</p>
      </div>
    </header>

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
          <router-link to="/hr/rank" class="action-card glass-panel">
            <span class="action-icon">🏆</span>
            <div class="action-content-card">
              <h4>Bulk CV Ranking</h4>
              <p>Upload multiple resumes to match and rank them against a job description.</p>
              <span class="action-link-text">Open Module →</span>
            </div>
          </router-link>

          <router-link to="/hr/cluster" class="action-card glass-panel">
            <span class="action-icon">🧩</span>
            <div class="action-content-card">
              <h4>Talent Clustering</h4>
              <p>Segment candidates into skill clusters automatically using machine learning.</p>
              <span class="action-link-text">Open Module →</span>
            </div>
          </router-link>

          <!-- Future Modules: Talent Pool & Interview (Easy to extend) -->
          <div class="action-card glass-panel disabled">
            <span class="coming-soon-badge">Coming Soon</span>
            <span class="action-icon">👥</span>
            <div class="action-content-card">
              <h4>Talent Pool Management</h4>
              <p>Store, filter, and track top matching profiles for future vacancies.</p>
              <span class="action-link-text disabled-text">Locked</span>
            </div>
          </div>

          <div class="action-card glass-panel disabled">
            <span class="coming-soon-badge">Coming Soon</span>
            <span class="action-icon">📅</span>
            <div class="action-content-card">
              <h4>AI Interview Scheduler</h4>
              <p>Generate screening questions and schedule video interviews automatically.</p>
              <span class="action-link-text disabled-text">Locked</span>
            </div>
          </div>
        </div>

        <!-- Job Seeker Actions -->
        <div v-else class="actions-grid jobseeker">
          <router-link to="/jobseeker/analyze" class="action-card glass-panel">
            <span class="action-icon">📄</span>
            <div class="action-content-card">
              <h4>CV-JD Analysis</h4>
              <p>Analyze how well your resume matches a specific job description.</p>
              <span class="action-link-text">Analyze Now →</span>
            </div>
          </router-link>

          <router-link to="/jobseeker/search" class="action-card glass-panel">
            <span class="action-icon">🔍</span>
            <div class="action-content-card">
              <h4>Semantic Job Search</h4>
              <p>Find jobs match by upload of your CV using AI semantic searches.</p>
              <span class="action-link-text">Search Jobs →</span>
            </div>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { authState } from '../stores/auth'

const user = computed(() => authState.user || {})

const userName = computed(() => user.value.name || 'User')
const userEmail = computed(() => user.value.email || '-')
const userRoleName = computed(() => user.value.role === 'hr' ? 'HR Recruiter' : 'Job Seeker')
const userProvider = computed(() => user.value.provider || 'email')
const isHrRole = computed(() => user.value.role === 'hr')

const userInitial = computed(() => {
  return userName.value.charAt(0).toUpperCase()
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
  color: #075985;
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
  box-shadow: 0 12px 28px rgba(3, 105, 161, 0.22);
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
  grid-template-columns: 1fr;
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
</style>
