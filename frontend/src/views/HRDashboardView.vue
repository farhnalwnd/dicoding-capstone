<template>
  <div class="dashboard-analytics-container">
    <!-- Header Section -->
    <header class="dashboard-header glass-panel">
      <div class="header-content">
        <span class="role-badge">
          <span class="badge-dot"></span>
          Recruitment Insights
        </span>
        <h2>HR Analytics Dashboard</h2>
        <p class="subtitle">Real-time candidate pipelines, skills demand analysis, and key performance indicators.</p>
      </div>
    </header>

    <!-- Filters Panel -->
    <div class="filters-panel glass-panel">
      <div class="filter-row">
        <div class="filter-group">
          <label for="start-date-filter">Start Date:</label>
          <input 
            id="start-date-filter" 
            type="date" 
            v-model="filters.start_date" 
            class="input-field date-input"
            @change="fetchAnalyticsData"
          />
        </div>
        <div class="filter-group">
          <label for="end-date-filter">End Date:</label>
          <input 
            id="end-date-filter" 
            type="date" 
            v-model="filters.end_date" 
            class="input-field date-input"
            @change="fetchAnalyticsData"
          />
        </div>
        <div class="filter-group">
          <label for="domain-filter">Job Domain:</label>
          <select 
            id="domain-filter" 
            v-model="filters.domain" 
            class="input-field select-input"
            @change="fetchAnalyticsData"
          >
            <option value="all">All Domains</option>
            <option v-for="d in domainOptions" :key="d.value" :value="d.value">
              {{ d.label }}
            </option>
          </select>
        </div>
        <button type="button" @click="resetFilters" class="btn-reset">
          Reset Filters
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="fatalError" class="error-wrapper glass-panel">
      <div class="error-state">
        <span class="error-icon">⚠️</span>
        <p class="error-msg">{{ fatalError.message }}</p>
        <button @click="fetchAnalyticsData" class="btn-primary">Retry Fetching</button>
      </div>
    </div>

    <!-- Skeleton Loading State -->
    <div v-else-if="loading" class="skeleton-wrapper">
      <div class="skeleton-kpis-grid">
        <div v-for="n in 6" :key="n" class="skeleton-card glass-panel loading-shimmer"></div>
      </div>
      <div class="skeleton-scores-grid">
        <div v-for="n in 3" :key="n" class="skeleton-score-card glass-panel loading-shimmer"></div>
      </div>
      <div class="skeleton-charts-grid">
        <div v-for="n in 4" :key="n" class="skeleton-chart-box glass-panel loading-shimmer"></div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="empty-wrapper glass-panel">
      <div class="empty-state">
        <h3>No Recruitment Data Available</h3>
        <p>There are no candidates uploaded or matching the selected filters. Please upload resumes in the Bulk CV Ranking page first.</p>
        <router-link to="/hr/rank-cv" class="btn-primary btn-link-rank">Go to Rank CV</router-link>
      </div>
    </div>

    <!-- Main Content Panel -->
    <div v-else class="analytics-content">
      <!-- KPI Cards Row -->
      <section class="kpis-grid" aria-label="Recruitment KPI Cards">
        <AnalyticsCard 
          title="Total Candidates" 
          :count="stats.counts.total_candidates" 
          :trend="stats.trends.total_candidates" 
          icon="👥" 
          theme="blue"
        />
        <AnalyticsCard 
          title="Screening" 
          :count="stats.counts.screening" 
          :trend="stats.trends.screening" 
          icon="🔍" 
          theme="cyan"
        />
        <AnalyticsCard 
          title="Talent Pool" 
          :count="stats.counts.talent_pool" 
          :trend="stats.trends.talent_pool" 
          icon="📂" 
          theme="purple"
        />
        <AnalyticsCard 
          title="Interview" 
          :count="stats.counts.interview" 
          :trend="stats.trends.interview" 
          icon="📅" 
          theme="amber"
        />
        <AnalyticsCard 
          title="Hired" 
          :count="stats.counts.hired" 
          :trend="stats.trends.hired" 
          icon="🎉" 
          theme="green"
        />
        <AnalyticsCard 
          title="Rejected" 
          :count="stats.counts.rejected" 
          :trend="stats.trends.rejected" 
          icon="❌" 
          theme="red"
        />
      </section>

      <!-- Match Scores & Status Distribution Row -->
      <section class="score-distribution-row">
        <!-- Match Score Stats Cards -->
        <div class="scores-summary-column">
          <div class="score-summary-card glass-panel border-blue">
            <div class="score-details">
              <span class="score-val">{{ stats.scores.average }}%</span>
              <span class="score-lbl">Average Match Score</span>
            </div>
          </div>
          <div class="score-summary-card glass-panel border-green">
            <div class="score-details">
              <span class="score-val">{{ stats.scores.highest }}%</span>
              <span class="score-lbl">Highest Match Score</span>
            </div>
          </div>
          <div class="score-summary-card glass-panel border-red">
            <div class="score-details">
              <span class="score-val">{{ stats.scores.lowest }}%</span>
              <span class="score-lbl">Lowest Match Score</span>
            </div>
          </div>
        </div>

        <!-- Recruitment Status Distribution Pie Chart -->
        <div class="distribution-chart-card glass-panel">
          <h4 class="chart-inner-title">Recruitment Status Distribution</h4>
          <div class="pie-chart-wrapper">
            <Pie :data="pieChartData" :options="pieChartOptions" />
          </div>
        </div>
      </section>

      <!-- Main Analytics Graphs Grid -->
      <section class="charts-grid-layout">
        <!-- Funnel Chart Box (Full Width) -->
        <div class="chart-box glass-panel full-width-chart">
          <FunnelChart :funnel-data="funnel" />
        </div>

        <!-- Skills Demand Box -->
        <div class="chart-box glass-panel">
          <SkillsChart :skills-data="skills" />
        </div>

        <!-- Domains Box -->
        <div class="chart-box glass-panel">
          <CategoryChart :categories-data="categories" />
        </div>

        <!-- Activity Timeline Box (Full Width) -->
        <div class="chart-box glass-panel full-width-chart">
          <TimelineChart :timeline-data="timeline" />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import AnalyticsCard from '../components/AnalyticsCard.vue'
import FunnelChart from '../components/FunnelChart.vue'
import SkillsChart from '../components/SkillsChart.vue'
import CategoryChart from '../components/CategoryChart.vue'
import TimelineChart from '../components/TimelineChart.vue'
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

const toast = inject('toast')

const loading = ref(true)
const fatalError = ref(null)

const filters = ref({
  start_date: '',
  end_date: '',
  domain: 'all'
})

const stats = ref({
  counts: {
    total_candidates: 0,
    screening: 0,
    talent_pool: 0,
    interview: 0,
    hired: 0,
    rejected: 0
  },
  trends: {
    total_candidates: '0%',
    screening: '0%',
    talent_pool: '0%',
    interview: '0%',
    hired: '0%',
    rejected: '0%'
  },
  scores: {
    average: 0,
    highest: 0,
    lowest: 0
  }
})

const funnel = ref([])
const skills = ref([])
const categories = ref([])
const timeline = ref([])

const domainOptions = [
  { value: 'general', label: 'General' },
  { value: 'it', label: 'IT' },
  { value: 'hr', label: 'HR' },
  { value: 'finance', label: 'Finance' },
  { value: 'creative', label: 'Creative & Marketing' },
  { value: 'sales', label: 'Sales & Business Development' },
  { value: 'legal', label: 'Legal' },
  { value: 'pr', label: 'PR & Corcom' },
  { value: 'ga', label: 'GA' },
  { value: 'cs', label: 'Customer Service' },
  { value: 'operational', label: 'Operational' }
]

const isEmpty = computed(() => {
  return !loading.value && stats.value.counts.total_candidates === 0
})

const fetchAnalyticsData = async () => {
  loading.value = true
  fatalError.value = null
  
  // Clean empty params
  const params = {}
  if (filters.value.start_date) params.start_date = filters.value.start_date
  if (filters.value.end_date) params.end_date = filters.value.end_date
  if (filters.value.domain && filters.value.domain !== 'all') params.domain = filters.value.domain
  
  try {
    const [statsRes, funnelRes, skillsRes, categoriesRes, timelineRes] = await Promise.all([
      axios.get(`${API_BASE_URL}/api/hr-dashboard/stats`, { params }),
      axios.get(`${API_BASE_URL}/api/hr-dashboard/funnel`, { params }),
      axios.get(`${API_BASE_URL}/api/hr-dashboard/skills`, { params }),
      axios.get(`${API_BASE_URL}/api/hr-dashboard/categories`, { params }),
      axios.get(`${API_BASE_URL}/api/hr-dashboard/timeline`, { params })
    ])
    
    stats.value = statsRes.data
    funnel.value = funnelRes.data
    skills.value = skillsRes.data
    categories.value = categoriesRes.data
    timeline.value = timelineRes.data
  } catch (error) {
    console.error(error)
    fatalError.value = {
      message: error.response?.data?.detail || 'Failed to retrieve recruitment statistics.'
    }
    toast.error('Failed to load dashboard analytics.')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    start_date: '',
    end_date: '',
    domain: 'all'
  }
  fetchAnalyticsData()
}

onMounted(() => {
  fetchAnalyticsData()
})

// Pie Chart computed data & options
const pieChartData = computed(() => {
  return {
    labels: ['Screening', 'Talent Pool', 'Interviews', 'Hired', 'Rejected'],
    datasets: [{
      data: [
        stats.value.counts.screening,
        stats.value.counts.talent_pool,
        stats.value.counts.interview,
        stats.value.counts.hired,
        stats.value.counts.rejected
      ],
      backgroundColor: [
        'rgba(34, 211, 238, 0.75)', // Cyan
        'rgba(139, 92, 246, 0.75)', // Purple
        'rgba(245, 158, 11, 0.75)',  // Amber
        'rgba(34, 197, 94, 0.75)',   // Green
        'rgba(239, 68, 68, 0.75)'    // Red
      ],
      borderColor: '#FFFFFF',
      borderWidth: 1.5
    }]
  }
})

const pieChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: {
        boxWidth: 12,
        padding: 15,
        font: { family: 'Inter', weight: '700', size: 10 },
        color: '#64748B'
      }
    }
  }
}
</script>

<style scoped>
.dashboard-analytics-container {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.dashboard-header {
  padding: 2.2rem 2.8rem;
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

.subtitle {
  color: var(--text-muted);
  margin: 0;
  font-size: 1rem;
}

/* Filters Panel */
.filters-panel {
  padding: 1.25rem 2rem;
  border-radius: 20px;
}

.filter-row {
  display: flex;
  align-items: flex-end;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  flex-grow: 1;
  min-width: 180px;
}

.filter-group label {
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-field {
  padding: 0.65rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(14, 165, 233, 0.22);
  background: rgba(255, 255, 255, 0.75);
  color: var(--text-soft);
  font-weight: 650;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
  background: white;
}

.btn-reset {
  min-height: 40px;
  padding: 0 1.25rem;
  border-radius: 12px;
  background: rgba(148, 163, 184, 0.12);
  color: var(--text-soft);
  border: 1px solid rgba(148, 163, 184, 0.22);
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  transition: all 0.2s ease;
}

.btn-reset:hover {
  background: rgba(148, 163, 184, 0.22);
}

.analytics-content {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

/* KPI Cards Layout */
.kpis-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1.5rem;
}

@media (max-width: 1120px) {
  .kpis-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 680px) {
  .kpis-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .kpis-grid {
    grid-template-columns: 1fr;
  }
}

/* Scores & Status distribution row */
.score-distribution-row {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 2rem;
}

.scores-summary-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.score-summary-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 1.5rem 2rem;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  transition: all 0.25s ease;
}

.score-summary-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-strong);
}

.score-details {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
}

.score-val {
  font-size: 1.45rem;
  font-weight: 950;
  color: var(--text-soft);
  line-height: 1.2;
}

.score-lbl {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.border-blue:hover { border-color: rgba(14, 165, 233, 0.45); }
.border-green:hover { border-color: rgba(34, 197, 94, 0.45); }
.border-red:hover { border-color: rgba(239, 68, 68, 0.45); }

.distribution-chart-card {
  padding: 1.75rem;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  min-height: 280px;
}

.chart-inner-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 850;
  color: var(--text-soft);
}

.pie-chart-wrapper {
  flex-grow: 1;
  position: relative;
  height: 100%;
  min-height: 220px;
}

/* Charts grid layout */
.charts-grid-layout {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
}

.chart-box {
  padding: 2.25rem;
  border-radius: var(--radius-lg);
  min-height: 380px;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
}

.full-width-chart {
  grid-column: span 2;
}

@media (max-width: 960px) {
  .score-distribution-row,
  .charts-grid-layout {
    grid-template-columns: 1fr;
  }
  .full-width-chart {
    grid-column: span 1;
  }
}

/* Error wrapper */
.error-wrapper,
.empty-wrapper {
  padding: 4rem 2rem;
  text-align: center;
  border-radius: var(--radius-lg);
}

.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
}

.error-icon,
.empty-icon {
  font-size: 3.5rem;
}

.error-msg {
  font-size: 1.1rem;
  color: var(--text-soft);
  font-weight: 600;
  max-width: 500px;
  line-height: 1.6;
}

.empty-state h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 850;
  color: var(--text-soft);
}

.empty-state p {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-muted);
  max-width: 520px;
  line-height: 1.6;
}

.btn-link-rank {
  text-decoration: none;
  font-size: 0.9rem;
}

/* Skeleton Loaders */
.skeleton-kpis-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.skeleton-card {
  height: 130px;
  border-radius: var(--radius-lg);
  position: relative;
  overflow: hidden;
}

.skeleton-scores-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.skeleton-score-card {
  height: 80px;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
}

.skeleton-charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.skeleton-chart-box {
  height: 320px;
  border-radius: var(--radius-lg);
  position: relative;
  overflow: hidden;
}

.loading-shimmer::after {
  content: '';
  position: absolute;
  top: 0; right: 0; bottom: 0; left: 0;
  transform: translateX(-100%);
  background-image: linear-gradient(
    90deg,
    rgba(255,255,255,0) 0%,
    rgba(255,255,255,0.3) 20%,
    rgba(255,255,255,0.5) 60%,
    rgba(255,255,255,0) 100%
  );
  animation: shimmer 2.2s infinite;
}

@keyframes shimmer {
  100% { transform: translateX(100%); }
}

@media (max-width: 1024px) {
  .skeleton-kpis-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .skeleton-scores-grid,
  .skeleton-charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
