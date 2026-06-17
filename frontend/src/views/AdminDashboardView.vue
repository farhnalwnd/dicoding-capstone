<template>
  <div class="admin-container">
    <!-- Header -->
    <header class="admin-header glass-panel">
      <div class="admin-header-left">
        <span class="admin-badge">
          <span class="badge-dot"></span>
          Admin Control Center
        </span>
        <h2>Platform Overview</h2>
        <p class="header-sub">HIREZY — Full system visibility and control.</p>
      </div>
      <div class="admin-header-right">
        <span class="admin-time">{{ currentTime }}</span>
      </div>
    </header>

    <!-- Tab Navigation -->
    <nav class="admin-tabs glass-panel">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ 'is-active': activeTab === tab.id }"
        @click="activeTab = tab.id"
        :id="`tab-${tab.id}`"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </nav>

    <!-- ==================== TAB: OVERVIEW ==================== -->
    <div v-if="activeTab === 'overview'" class="tab-content">

      <!-- KPI Cards -->
      <div v-if="statsLoading" class="loading-shimmer glass-panel">Loading statistics...</div>
      <div v-else class="kpi-grid">
        <PlatformStatsCard icon="👥" label="Total Users"       :value="stats.total_users"       color="blue"   />
        <PlatformStatsCard icon="💼" label="HR Recruiters"     :value="stats.total_hr"          color="indigo" />
        <PlatformStatsCard icon="🎓" label="Job Seekers"       :value="stats.total_jobseekers"  color="purple" />
        <PlatformStatsCard icon="📄" label="Total Candidates"  :value="stats.total_candidates"  color="cyan"   />
        <PlatformStatsCard icon="📅" label="Interviews"        :value="stats.total_interviews"  color="amber"  />
        <PlatformStatsCard icon="📂" label="Talent Pool"       :value="stats.total_talent_pool" color="teal"   />
        <PlatformStatsCard icon="🎉" label="Hired"             :value="stats.total_hired"       color="green"  />
        <PlatformStatsCard icon="🔍" label="CV Analyses"       :value="stats.total_cv_analyses" color="red"    />
      </div>

      <!-- Recruitment Overview Chart -->
      <div class="overview-grid">
        <div class="chart-card glass-panel">
          <div class="card-header">
            <span class="card-icon amber-icon">📊</span>
            <h3>Recruitment Overview</h3>
          </div>
          <div v-if="recruitLoading" class="chart-loading">Loading...</div>
          <div v-else class="recruit-stats-row">
            <div class="recruit-stat">
              <span class="rs-val">{{ recruitData.total_applications }}</span>
              <span class="rs-lbl">Applications</span>
            </div>
            <div class="recruit-stat">
              <span class="rs-val">{{ recruitData.total_interviews }}</span>
              <span class="rs-lbl">Interviews</span>
            </div>
            <div class="recruit-stat">
              <span class="rs-val">{{ recruitData.total_hired }}</span>
              <span class="rs-lbl">Hired</span>
            </div>
            <div class="recruit-stat text-green">
              <span class="rs-val">{{ recruitData.hiring_rate }}%</span>
              <span class="rs-lbl">Hire Rate</span>
            </div>
          </div>

          <!-- Simple bar chart (monthly) -->
          <div class="mini-bars" v-if="recruitData.monthly_trend?.length">
            <div
              v-for="m in recruitData.monthly_trend"
              :key="m.month"
              class="mini-bar-group"
            >
              <div class="mini-bar-wrap">
                <div
                  class="mini-bar bar-blue"
                  :style="{ height: barHeight(m.applications, maxApps) }"
                  :title="`${m.month}: ${m.applications} applications`"
                ></div>
                <div
                  class="mini-bar bar-green"
                  :style="{ height: barHeight(m.hired, maxApps) }"
                  :title="`${m.month}: ${m.hired} hired`"
                ></div>
              </div>
              <span class="mini-bar-label">{{ m.month.split(' ')[0] }}</span>
            </div>
          </div>
          <div class="chart-legend">
            <span class="legend-dot blue-dot"></span><span>Applications</span>
            <span class="legend-dot green-dot"></span><span>Hired</span>
          </div>
        </div>

        <!-- AI Usage Card -->
        <div class="chart-card glass-panel">
          <div class="card-header">
            <span class="card-icon purple-icon">🤖</span>
            <h3>AI Usage Analytics</h3>
          </div>
          <div v-if="aiLoading" class="chart-loading">Loading...</div>
          <div v-else class="ai-usage-list">
            <div class="ai-usage-row">
              <span class="ai-lbl">CV Analysis Requests</span>
              <span class="ai-val blue-val">{{ aiUsage.cv_analysis_requests }}</span>
            </div>
            <div class="ai-usage-row">
              <span class="ai-lbl">Resume Advisor Requests</span>
              <span class="ai-val purple-val">{{ aiUsage.resume_advisor_requests }}</span>
            </div>
            <div class="ai-usage-row">
              <span class="ai-lbl">Semantic Search Requests</span>
              <span class="ai-val cyan-val">{{ aiUsage.semantic_search_requests }}</span>
            </div>
            <div class="ai-usage-row">
              <span class="ai-lbl">HR Ranking Requests</span>
              <span class="ai-val amber-val">{{ aiUsage.hr_ranking_requests }}</span>
            </div>
            <div class="ai-usage-row highlight-row">
              <span class="ai-lbl">Avg Match Score</span>
              <span class="ai-val green-val">{{ aiUsage.average_match_score }}%</span>
            </div>
            <div class="ai-usage-row">
              <span class="ai-lbl">Total CVs Analyzed</span>
              <span class="ai-val">{{ aiUsage.total_candidates_analyzed }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== TAB: SYSTEM HEALTH ==================== -->
    <div v-if="activeTab === 'health'" class="tab-content">
      <div class="section-header">
        <h3>System Health Monitor</h3>
        <button class="btn-refresh" @click="fetchHealth" :disabled="healthLoading" id="refresh-health-btn">
          {{ healthLoading ? 'Checking...' : '🔄 Refresh' }}
        </button>
      </div>

      <div v-if="healthData.overall" class="overall-health glass-panel" :class="`overall-${healthData.overall}`">
        <span class="overall-icon">
          {{ healthData.overall === 'healthy' ? '✅' : healthData.overall === 'warning' ? '⚠️' : '❌' }}
        </span>
        <div>
          <strong>Overall: {{ healthData.overall?.toUpperCase() }}</strong>
          <span class="overall-time" v-if="healthData.checked_at">
            — Checked at {{ formatTime(healthData.checked_at) }}
          </span>
        </div>
      </div>

      <div v-if="healthLoading" class="loading-shimmer glass-panel">Checking services...</div>
      <div v-else class="health-grid">
        <SystemHealthCard
          v-for="svc in healthData.services"
          :key="svc.name"
          :service="svc"
        />
      </div>

      <!-- Monitoring Links -->
      <div class="monitor-links-grid">
        <a :href="prometheusUrl" target="_blank" class="monitor-link glass-panel">
          <span>📊</span>
          <div>
            <strong>Prometheus</strong>
            <p>View raw metrics</p>
          </div>
          <span class="ext-link">↗</span>
        </a>
        <a :href="grafanaUrl" target="_blank" class="monitor-link glass-panel">
          <span>📈</span>
          <div>
            <strong>Grafana</strong>
            <p>Visual dashboards</p>
          </div>
          <span class="ext-link">↗</span>
        </a>
        <a :href="mlflowUrl" target="_blank" class="monitor-link glass-panel">
          <span>🔬</span>
          <div>
            <strong>MLflow</strong>
            <p>Experiment tracking</p>
          </div>
          <span class="ext-link">↗</span>
        </a>
      </div>
    </div>

    <!-- ==================== TAB: AUDIT LOGS ==================== -->
    <div v-if="activeTab === 'audit'" class="tab-content">
      <div class="section-header">
        <h3>Audit Logs</h3>
        <p class="section-sub">All admin actions are tracked here.</p>
      </div>
      <AuditLogTable ref="auditTable" />
    </div>

    <!-- ==================== TAB: NOTIFICATIONS ==================== -->
    <div v-if="activeTab === 'notifications'" class="tab-content">
      <div class="section-header">
        <h3>System Notifications</h3>
      </div>

      <div class="notif-list">
        <!-- Error services from health -->
        <template v-if="errorServices.length">
          <div v-for="svc in errorServices" :key="svc.name" class="notif-item notif-error glass-panel">
            <span class="notif-icon">❌</span>
            <div>
              <strong>Service Error: {{ svc.name }}</strong>
              <p>{{ svc.detail || 'Service is unreachable' }}</p>
            </div>
            <span class="notif-time">{{ formatTime(healthData.checked_at) }}</span>
          </div>
        </template>

        <template v-if="warnServices.length">
          <div v-for="svc in warnServices" :key="svc.name" class="notif-item notif-warn glass-panel">
            <span class="notif-icon">⚠️</span>
            <div>
              <strong>Warning: {{ svc.name }}</strong>
              <p>{{ svc.detail || 'Service responding slowly' }}</p>
            </div>
            <span class="notif-time">{{ formatTime(healthData.checked_at) }}</span>
          </div>
        </template>

        <div v-if="!errorServices.length && !warnServices.length" class="notif-empty glass-panel">
          <span>✅</span>
          <p>All systems are operating normally. No active alerts.</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import PlatformStatsCard from '../components/PlatformStatsCard.vue'
import SystemHealthCard from '../components/SystemHealthCard.vue'
import AuditLogTable from '../components/AuditLogTable.vue'

const activeTab = ref('overview')

const tabs = [
  { id: 'overview',       label: 'Overview',       icon: '📊' },
  { id: 'health',         label: 'System Health',  icon: '💚' },
  { id: 'audit',          label: 'Audit Logs',     icon: '📋' },
  { id: 'notifications',  label: 'Notifications',  icon: '🔔' },
]

// Time
const currentTime = ref('')
setInterval(() => {
  currentTime.value = new Date().toLocaleString('id-ID')
}, 1000)

// External links
const prometheusUrl = computed(() => `${window.location.protocol}//${window.location.hostname}:9090`)
const grafanaUrl    = computed(() => `${window.location.protocol}//${window.location.hostname}:3000`)
const mlflowUrl     = computed(() => `${window.location.protocol}//${window.location.hostname}:5000`)

// ── Stats ──────────────────────────────────────────
const stats = ref({
  total_users: 0, total_hr: 0, total_jobseekers: 0, total_candidates: 0,
  total_interviews: 0, total_talent_pool: 0, total_hired: 0, total_cv_analyses: 0
})
const statsLoading = ref(false)

async function fetchStats() {
  statsLoading.value = true
  try {
    const res = await axios.get(`${API_BASE_URL}/api/admin/stats`)
    stats.value = res.data
  } catch (e) { console.error(e) } finally { statsLoading.value = false }
}

// ── Recruitment ──────────────────────────────────
const recruitData   = ref({ total_applications: 0, total_interviews: 0, total_hired: 0, hiring_rate: 0, monthly_trend: [] })
const recruitLoading = ref(false)
const maxApps = computed(() => Math.max(...(recruitData.value.monthly_trend?.map(m => m.applications) || [1]), 1))

function barHeight(val, max) {
  const pct = max > 0 ? Math.round((val / max) * 80) : 0
  return `${Math.max(pct, 2)}px`
}

async function fetchRecruitment() {
  recruitLoading.value = true
  try {
    const res = await axios.get(`${API_BASE_URL}/api/admin/recruitment-overview`)
    recruitData.value = res.data
  } catch (e) { console.error(e) } finally { recruitLoading.value = false }
}

// ── AI Usage ────────────────────────────────────
const aiUsage = ref({ cv_analysis_requests: 0, resume_advisor_requests: 0, semantic_search_requests: 0, hr_ranking_requests: 0, average_match_score: 0, total_candidates_analyzed: 0 })
const aiLoading = ref(false)

async function fetchAiUsage() {
  aiLoading.value = true
  try {
    const res = await axios.get(`${API_BASE_URL}/api/admin/ai-usage`)
    aiUsage.value = res.data
  } catch (e) { console.error(e) } finally { aiLoading.value = false }
}

// ── System Health ────────────────────────────────
const healthData    = ref({ overall: '', services: [], checked_at: '' })
const healthLoading = ref(false)
const errorServices = computed(() => healthData.value.services?.filter(s => s.status === 'error') || [])
const warnServices  = computed(() => healthData.value.services?.filter(s => s.status === 'warning') || [])

async function fetchHealth() {
  healthLoading.value = true
  try {
    const res = await axios.get(`${API_BASE_URL}/api/admin/system-health`)
    healthData.value = res.data
  } catch (e) { console.error(e) } finally { healthLoading.value = false }
}

function formatTime(ts) {
  if (!ts) return '—'
  try { return new Date(ts).toLocaleString('id-ID') } catch { return ts }
}

onMounted(() => {
  fetchStats()
  fetchRecruitment()
  fetchAiUsage()
  fetchHealth()
})
</script>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.admin-header {
  padding: 2rem 2.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  position: relative;
  overflow: hidden;
}

.admin-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 10% 20%, rgba(239,68,68,0.07), transparent 30%),
              radial-gradient(circle at 90% 80%, rgba(14,165,233,0.06), transparent 25%);
  pointer-events: none;
}

.admin-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.25);
  color: #B91C1C;
  margin-bottom: 0.5rem;
}

.badge-dot {
  width: 0.44rem;
  height: 0.44rem;
  border-radius: 50%;
  background: #EF4444;
  box-shadow: 0 0 0 4px rgba(239,68,68,0.2);
}

.header-sub {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.92rem;
}

.admin-time {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-muted);
  white-space: nowrap;
}

/* Tabs */
.admin-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem;
  border-radius: 16px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.2rem;
  border-radius: 10px;
  border: none;
  background: transparent;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover { background: rgba(255,255,255,0.5); color: var(--text-soft); }
.tab-btn.is-active { background: rgba(255,255,255,0.85); color: var(--primary-dark); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

.tab-icon { font-size: 1rem; }

/* Tab content */
.tab-content { display: flex; flex-direction: column; gap: 1.5rem; }

/* KPI grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.2rem;
}

@media (max-width: 1024px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 580px)  { .kpi-grid { grid-template-columns: 1fr; } }

/* Overview charts */
.overview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 860px) { .overview-grid { grid-template-columns: 1fr; } }

.chart-card {
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.card-header h3 { margin: 0; font-size: 1rem; font-weight: 800; color: var(--text-soft); }

.card-icon {
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.amber-icon  { background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.2); }
.purple-icon { background:rgba(139,92,246,0.12); border:1px solid rgba(139,92,246,0.2); }

.chart-loading { color: var(--text-muted); font-size: 0.9rem; text-align: center; padding: 1rem; }

/* Recruitment stats */
.recruit-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.recruit-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
}

.rs-val {
  font-size: 1.6rem;
  font-weight: 900;
  color: var(--text-soft);
  line-height: 1;
}

.rs-lbl {
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.text-green .rs-val { color: #16A34A; }

/* Mini bar chart */
.mini-bars {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  height: 90px;
  padding-bottom: 1.5rem;
  position: relative;
}

.mini-bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  flex: 1;
}

.mini-bar-wrap {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 80px;
}

.mini-bar {
  width: 12px;
  border-radius: 4px 4px 0 0;
  transition: height 0.4s ease;
  min-height: 2px;
}

.bar-blue  { background: rgba(14,165,233,0.7); }
.bar-green { background: rgba(34,197,94,0.7); }

.mini-bar-label { font-size: 0.68rem; color: var(--text-muted); font-weight: 700; }

.chart-legend {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 600;
}

.legend-dot { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }
.blue-dot  { background: rgba(14,165,233,0.7); }
.green-dot { background: rgba(34,197,94,0.7); }

/* AI Usage */
.ai-usage-list { display: flex; flex-direction: column; gap: 0.75rem; }

.ai-usage-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-radius: 10px;
  background: rgba(255,255,255,0.4);
  border: 1px solid rgba(14,116,144,0.06);
}

.highlight-row { background: rgba(34,197,94,0.05); border-color: rgba(34,197,94,0.15); }

.ai-lbl { font-size: 0.88rem; color: var(--text-soft); font-weight: 600; }
.ai-val { font-size: 1.1rem; font-weight: 900; color: var(--text-soft); }

.blue-val   { color: #0369A1; }
.purple-val { color: #7C3AED; }
.cyan-val   { color: #0891B2; }
.amber-val  { color: #D97706; }
.green-val  { color: #16A34A; }

/* Section header */
.section-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.section-header h3 { margin: 0; font-size: 1.15rem; font-weight: 800; color: var(--text-soft); }
.section-sub { margin: 0; font-size: 0.88rem; color: var(--text-muted); }

.btn-refresh {
  background: rgba(255,255,255,0.7);
  border: 1px solid var(--glass-border);
  padding: 0.5rem 1rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: auto;
}
.btn-refresh:hover:not(:disabled) { background: rgba(255,255,255,0.95); }
.btn-refresh:disabled { opacity: 0.5; cursor: not-allowed; }

/* Overall health banner */
.overall-health {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.75rem;
  border-radius: 16px;
  font-size: 0.95rem;
  font-weight: 700;
}

.overall-healthy { background:rgba(34,197,94,0.08);  border:1px solid rgba(34,197,94,0.25);  color:#15803D; }
.overall-warning { background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.25); color:#B45309; }
.overall-error   { background:rgba(239,68,68,0.08);  border:1px solid rgba(239,68,68,0.25);  color:#DC2626; }

.overall-icon { font-size: 1.5rem; }
.overall-time { font-weight: 500; opacity: 0.75; }

/* Health grid */
.health-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.2rem;
}

@media (max-width: 860px) { .health-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 580px) { .health-grid { grid-template-columns: 1fr; } }

/* Monitoring links */
.monitor-links-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.2rem;
}

@media (max-width: 860px) { .monitor-links-grid { grid-template-columns: 1fr; } }

.monitor-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  text-decoration: none;
  color: inherit;
  border-radius: 16px;
  transition: all 0.2s;
  font-size: 1.5rem;
}

.monitor-link:hover { transform: translateY(-3px); box-shadow: var(--shadow-strong); }
.monitor-link strong { display: block; font-weight: 800; color: var(--text-soft); font-size: 0.95rem; }
.monitor-link p { margin: 0; font-size: 0.78rem; color: var(--text-muted); }
.monitor-link div { flex: 1; }
.ext-link { font-size: 1rem; color: var(--text-muted); }

/* Notifications */
.notif-list { display: flex; flex-direction: column; gap: 1rem; }

.notif-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: 16px;
}

.notif-error { background:rgba(239,68,68,0.07);  border:1px solid rgba(239,68,68,0.2); }
.notif-warn  { background:rgba(245,158,11,0.07); border:1px solid rgba(245,158,11,0.2); }

.notif-icon { font-size: 1.4rem; flex-shrink: 0; }

.notif-item strong { display: block; font-size: 0.95rem; color: var(--text-soft); }
.notif-item p { margin: 0.2rem 0 0; font-size: 0.82rem; color: var(--text-muted); }

.notif-time { margin-left: auto; font-size: 0.75rem; color: var(--text-muted); white-space: nowrap; }

.notif-empty {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 2rem 1.5rem;
  border-radius: 16px;
  font-size: 0.95rem;
  color: var(--text-muted);
  background: rgba(34,197,94,0.05);
  border: 1px solid rgba(34,197,94,0.15);
}

/* Shared loading shimmer */
.loading-shimmer {
  padding: 1.5rem;
  text-align: center;
  border-radius: 16px;
  color: var(--text-muted);
  font-weight: 600;
}
</style>
