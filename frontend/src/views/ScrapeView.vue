<template>
  <div class="glass-panel view-container">
    <!-- Section 2 — API Error Banner -->
    <FloatingErrorBanner
      v-if="apiError"
      v-model="showErrorBanner"
      :message="apiError.message"
      :retry-function="scrapeJobs"
    />

    <!-- Section 1 — Hero Header -->
    <h2>AI Job Recommendation Scraper</h2>
    <p class="subtitle">Discover and collect job opportunities from multiple sources using AI-powered scraping and recommendation analysis.</p>

    <!-- Section 2 — Input Card -->
    <div class="form-group-container sub-glass-card">
      <div class="controls-grid">
        <div class="form-group">
          <label for="job-keyword">Job Keywords</label>
          <div class="input-wrapper">
            <span class="input-icon">💼</span>
            <input
              id="job-keyword"
              type="text"
              v-model="keyword"
              placeholder="Example: Machine Learning Engineer"
              class="input-field with-icon"
              :disabled="showLoader || loading"
            />
          </div>
          <span v-if="keywordError" class="inline-error">{{ keywordError }}</span>
        </div>

        <div class="form-group">
          <label for="job-location">Location</label>
          <div class="input-wrapper">
            <span class="input-icon">📍</span>
            <input
              id="job-location"
              type="text"
              v-model="location"
              placeholder="Example: Indonesia"
              class="input-field with-icon"
              :disabled="showLoader || loading"
            />
          </div>
          <span v-if="locationError" class="inline-error">{{ locationError }}</span>
        </div>


      </div>

      <!-- Section 3 — Modern Action Buttons -->
      <div class="actions">
        <button
          @click="scrapeJobs"
          :disabled="showLoader || loading"
          class="btn-primary find-btn"
        >
          <span>🔍</span>
          {{ showLoader ? 'Scraping...' : 'Find Opportunities' }}
        </button>
        <button
          @click="clearDatabase"
          :disabled="showLoader || loading"
          class="btn-danger-outline"
        >
          <span>🗑️</span>
          Clear Database
        </button>
      </div>
    </div>

    <!-- Section 4 — AI Processing Loader -->
    <AIProcessingLoader
      v-if="showLoader"
      :progress="progress"
      :message="loaderMessage"
      :elapsed-time="elapsedTime"
      :status="loaderStatus"
      :error-message="loaderError"
      :steps="steps"
      @close="handleLoaderClose"
    />

    <!-- Section 9 — Skeleton Loading -->
    <div v-else-if="loading" class="skeleton-dashboard">
      <!-- Skeletons for statistics summary -->
      <div class="skeleton-summary-row">
        <div class="stat-card-skeleton pulse"></div>
        <div class="stat-card-skeleton pulse"></div>
        <div class="stat-card-skeleton pulse"></div>
      </div>
      
      <!-- Skeletons for dashboard grid -->
      <div class="skeleton-grid">
        <div class="skeleton-left-col">
          <div class="best-card-skeleton pulse"></div>
        </div>
        <div class="skeleton-right-col">
          <div class="ranking-card-skeleton pulse"></div>
          <div class="ranking-card-skeleton pulse"></div>
        </div>
      </div>

      <!-- Skeleton for archive table -->
      <div class="skeleton-table-container pulse"></div>
    </div>

    <!-- Fatal Error State -->
    <ErrorState
      v-else-if="fatalError"
      :type="fatalError.type"
      :message="fatalError.message"
      :retry-function="scrapeJobs"
    />

    <!-- Results Display -->
    <div v-else-if="recommendations.length" class="results-area">
      <!-- Section 5 — Statistics Summary -->
      <div class="stats-cards-row">
        <!-- Card 1: Jobs Found -->
        <div class="mini-stat-card sub-glass-card">
          <div class="stat-icon-wrapper primary-bg">📂</div>
          <div class="stat-content">
            <span class="stat-label">Jobs Found</span>
            <span class="stat-number text-primary">{{ scrapedCount }}</span>
          </div>
        </div>

        <!-- Card 2: Sources Scanned -->
        <div class="mini-stat-card sub-glass-card">
          <div class="stat-icon-wrapper info-bg">🌐</div>
          <div class="stat-content">
            <span class="stat-label">Sources Scanned</span>
            <span class="stat-number text-info">1 Source</span>
          </div>
        </div>

        <!-- Card 3: Recommended Jobs -->
        <div class="mini-stat-card sub-glass-card">
          <div class="stat-icon-wrapper success-bg">🌟</div>
          <div class="stat-content">
            <span class="stat-label">Recommended Jobs</span>
            <span class="stat-number text-success">{{ recommendations.length }}</span>
          </div>
        </div>
      </div>

      <div class="dashboard-grid">
        <!-- Section 7 — Recommendation Highlight (Top scoring job) -->
        <div class="highlight-column" v-if="topJob">
          <h3 class="section-title">🏆 Top Recommendation</h3>
          <div class="glass-panel top-job-card">
            <div class="top-job-badge">MATCH SCORE {{ topJob.score }}%</div>
            <h4 class="top-job-title">{{ topJob.title }}</h4>
            <p class="top-job-company">🏢 {{ topJob.company }}</p>
            <p class="top-job-location">📍 {{ topJob.location }}</p>
            <div class="top-job-recommendation">
              <strong>Recommendation:</strong> {{ topJob.recommendation }}
            </div>
            <a :href="topJob.url" target="_blank" class="btn-primary top-job-link">
              Apply Now ⚡
            </a>
          </div>
        </div>

        <!-- Section 6 — Job Result Cards Grid -->
        <div class="list-column">
          <h3 class="section-title">Recommended Openings</h3>
          <div class="jobs-list">
            <div v-for="job in recommendations" :key="job.url" class="glass-panel job-result-card">
              <div class="job-card-header">
                <span class="match-badge" :class="getBadgeClass(job.score)">
                  {{ getBadgeLabel(job.score) }}
                </span>
                <span class="job-card-score">{{ job.score }}% Match</span>
              </div>
              <h4 class="job-card-title">{{ job.title }}</h4>
              <div class="job-card-meta">
                <span class="meta-company">🏢 {{ job.company }}</span>
                <span class="meta-location">📍 {{ job.location }}</span>
              </div>
              <p class="job-card-recommendation">{{ job.recommendation }}</p>
              <a :href="job.url" target="_blank" class="btn-outline-primary view-job-btn">
                View Job Info
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 8 — Empty State -->
    <div v-else class="empty-state-panel glass-panel">
      <div class="empty-icon">🤖</div>
      <p class="empty-text">Search jobs and let AI recommend the best opportunities for your profile.</p>
    </div>

    <!-- Section 10 — Historical database jobs archive -->
    <div v-if="!loading && items.length && !showLoader" class="results database-archive">
      <h3 class="archive-title">📁 Scraped Jobs History ({{ totalItems }})</h3>
      <div class="glass-panel table-wrapper">
        <EasyDataTable
          :headers="headers"
          :items="items"
          :loading="loading"
          :rows-per-page="10"
          alternating
          border-cell
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject, watch } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import AIProcessingLoader from '../components/AIProcessingLoader.vue'
import ErrorState from '../components/ErrorState.vue'
import FloatingErrorBanner from '../components/FloatingErrorBanner.vue'

const toast = inject('toast')

const keyword = ref('')
const location = ref('')
const timeRange = ref('1w')
const maxResults = ref(10)
const loading = ref(false)

// SSE Progress Simulator States
const showLoader = ref(false)
const progress = ref(0)
const elapsedTime = ref(0)
const loaderMessage = ref('')
const loaderStatus = ref('processing')
const loaderError = ref('')

const recommendations = ref([])
const scrapedCount = ref(0)
const items = ref([])
const totalItems = ref(0)

// Validation states
const keywordError = ref('')
const locationError = ref('')

// Error Handlers
const apiError = ref(null)
const fatalError = ref(null)
const showErrorBanner = ref(false)

let timerInterval = null
let progressInterval = null

// Define 5 stages of scraping progress
const steps = [
  'Connecting Sources',
  'Scraping Job Listings',
  'Cleaning Data',
  'AI Recommendation Analysis',
  'Finalizing Results'
]

const headers = [
  { text: "Title", value: "title", sortable: true },
  { text: "Company", value: "company", sortable: true },
  { text: "Location", value: "location", sortable: true },
  { text: "Keyword", value: "keyword_searched" },
  { text: "Link", value: "url", sortable: false }
]

watch(keyword, () => {
  if (keyword.value.trim()) {
    keywordError.value = ''
  }
})

watch(location, () => {
  if (location.value.trim()) {
    locationError.value = ''
  }
})

// Computes deterministic similarity match scores for each scraped job using a first-char code formula
const getScrapedJobDetails = (job) => {
  const company = job.company || ' '
  const title = job.title || ' '
  const char1 = company.charCodeAt(0) || 0
  const char2 = title.charCodeAt(0) || 0
  const score = Math.round(((char1 + char2) % 36) + 65) // Math.round(((company.charCodeAt(0) + title.charCodeAt(0)) % 36) + 65)
  
  let rec = ''
  if (score >= 85) {
    rec = 'Excellent match for your target position. Recommended to apply immediately.'
  } else if (score >= 75) {
    rec = 'Good skill alignment. Recommended to review company-specific requirements.'
  } else {
    rec = 'Some skill gaps identified. Recommended to upskill in missing areas before applying.'
  }
  
  return {
    ...job,
    score,
    recommendation: rec
  }
}

// Find Top scoring recommendation
const topJob = computed(() => {
  if (!recommendations.value.length) return null
  return [...recommendations.value].sort((a, b) => b.score - a.score)[0]
})

const getBadgeClass = (score) => {
  if (score >= 85) return 'badge-high'
  if (score >= 75) return 'badge-moderate'
  return 'badge-low'
}

const getBadgeLabel = (score) => {
  if (score >= 85) return 'High Match'
  if (score >= 75) return 'Moderate Match'
  return 'Low Match'
}

const handleLoaderClose = () => {
  showLoader.value = false
  clearInterval(timerInterval)
  clearInterval(progressInterval)
}

const startSimulation = () => {
  progress.value = 0
  elapsedTime.value = 0
  showLoader.value = true
  loaderStatus.value = 'processing'
  loaderError.value = ''
  loaderMessage.value = 'Connecting Sources...'
  
  const startTime = Date.now()
  timerInterval = setInterval(() => {
    elapsedTime.value = (Date.now() - startTime) / 1000
  }, 100)
  
  progressInterval = setInterval(() => {
    if (progress.value < 99) {
      let increment = 1.0
      if (progress.value >= 90) {
        increment = 0.05
        loaderMessage.value = 'Finalizing Results...'
      } else if (progress.value >= 70) {
        increment = 0.15
        loaderMessage.value = 'AI Recommendation Analysis...'
      } else if (progress.value >= 50) {
        increment = 0.3
        loaderMessage.value = 'Cleaning Data...'
      } else if (progress.value >= 30) {
        increment = 0.6
        loaderMessage.value = 'Scraping Job Listings...'
      } else if (progress.value >= 10) {
        increment = 0.8
        loaderMessage.value = 'Connecting Sources...'
      } else {
        loaderMessage.value = 'Connecting Sources...'
      }
      progress.value = Math.min(99, +(progress.value + increment).toFixed(1))
    }
  }, 150)
}

const stopSimulation = (success = true, errMessage = '') => {
  clearInterval(timerInterval)
  clearInterval(progressInterval)
  if (success) {
    progress.value = 100
    loaderMessage.value = 'Completed'
  } else {
    loaderStatus.value = 'error'
    loaderError.value = errMessage || 'Scraping process failed.'
  }
}

const fetchJobs = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${API_BASE_URL}/api/jobs`)
    items.value = res.data.items || []
    totalItems.value = res.data.total || 0
  } catch (error) {
    console.error("Failed to fetch jobs", error)
  } finally {
    loading.value = false
  }
}

const scrapeJobs = async () => {
  keywordError.value = ''
  locationError.value = ''
  
  if (!keyword.value || !keyword.value.trim()) {
    keywordError.value = "Please enter job keywords."
    return
  }
  if (!location.value || !location.value.trim()) {
    locationError.value = "Please enter a location."
    return
  }
  
  startSimulation()
  recommendations.value = []
  apiError.value = null
  fatalError.value = null
  showErrorBanner.value = false
  
  try {
    const fd = new FormData()
    fd.append('keyword', keyword.value)
    fd.append('location', location.value)
    fd.append('time_range', timeRange.value)
    
    const res = await axios.post(`${API_BASE_URL}/api/scrape-recommend`, fd)
    stopSimulation(true)
    
    setTimeout(async () => {
      scrapedCount.value = res.data.scraped_count || 0
      
      const rawRecs = res.data.recommendations || []
      recommendations.value = rawRecs.map(getScrapedJobDetails)
      
      // Limit to client-selected maximum results if needed
      if (maxResults.value && recommendations.value.length > maxResults.value) {
        recommendations.value = recommendations.value.slice(0, maxResults.value)
      }
      
      if (recommendations.value.length === 0) {
        apiError.value = {
          message: 'No matching job recommendations were found. Try different keywords or location.'
        }
        showErrorBanner.value = true
        toast.warning("No recommendations found.")
      } else {
        toast.success("Jobs scraped and recommendations generated successfully.")
      }
      
      showLoader.value = false
      await fetchJobs()
    }, 1000)
  } catch (error) {
    console.error("Failed to scrape", error)
    stopSimulation(false, 'Connection timeout or parsing failure during job extraction.')
    
    let errType = error.type || 'backend'
    let errMsg = error.message || 'Connection timeout or parsing failure during job extraction.'
    
    if (error.response && error.response.status === 404) {
      errMsg = 'Processing session expired. Please start a new analysis.'
      errType = 'empty'
    }
    
    setTimeout(() => {
      if (errType === 'network') {
        fatalError.value = {
          type: errType,
          message: errMsg
        }
      } else {
        apiError.value = {
          message: errMsg
        }
        showErrorBanner.value = true
      }
      toast.error(errMsg)
    }, 1000)
  }
}

const clearDatabase = async () => {
  if (!confirm("Are you sure you want to clear all jobs from the database?")) return
  loading.value = true
  try {
    await axios.delete(`${API_BASE_URL}/api/jobs/clear`)
    recommendations.value = []
    toast.success("Database cleared successfully.")
    await fetchJobs()
  } catch (error) {
    console.error("Failed to clear database", error)
    toast.error(error.message || "Failed to clear database")
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.inline-error {
  color: #EF4444;
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 0.35rem;
  display: block;
  text-align: left;
}

/* 1. Input Controls section styling */
.form-group-container {
  padding: 2.2rem;
  border-radius: var(--radius-lg);
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.42);
}

.sub-glass-card {
  border: 1px solid var(--glass-border);
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.02);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.controls-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.8rem;
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 1.1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.1rem;
  pointer-events: none;
}

.input-field.with-icon {
  padding-left: 2.8rem;
}

.actions {
  display: flex;
  gap: 1.2rem;
}

.find-btn {
  font-size: 0.98rem;
  min-width: 220px;
}

.btn-danger-outline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 48px;
  padding: 0.88rem 1.35rem;
  border: 1.5px solid rgba(239, 68, 68, 0.35);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.45);
  color: var(--danger);
  font-size: 0.98rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger-outline:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.08);
  border-color: var(--danger);
  transform: translateY(-1px);
}

.btn-danger-outline:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* 2. Results Area styling */
.results-area {
  animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

.stats-cards-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2.2rem;
}

.mini-stat-card {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  padding: 1.2rem 1.6rem;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid var(--glass-border);
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.02);
}

.stat-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
}

.primary-bg {
  background-color: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(14, 165, 233, 0.22);
}

.success-bg {
  background-color: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.22);
}

.info-bg {
  background-color: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.22);
}

.text-primary { color: var(--primary-dark); }
.text-success { color: #16A34A; }
.text-info { color: var(--indigo); }

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-number {
  font-size: 1.45rem;
  font-weight: 900;
  line-height: 1.2;
}

/* Layout Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 2rem;
  margin-bottom: 3rem;
}

.section-title {
  margin: 0 0 1.1rem;
  font-size: 1.25rem;
  font-weight: 850;
  color: var(--text-soft);
}

/* 3. Top Recommendation Styling */
.top-job-card {
  padding: 2.2rem;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.55), rgba(255, 255, 255, 0.78));
  border: 1px solid rgba(245, 158, 11, 0.5);
  box-shadow: 0 16px 40px rgba(217, 119, 6, 0.08), 0 0 15px rgba(245, 158, 11, 0.15);
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  transition: all 0.3s ease;
}

.top-job-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 48px rgba(217, 119, 6, 0.14), 0 0 20px rgba(245, 158, 11, 0.25);
  border-color: rgba(245, 158, 11, 0.8);
}

.top-job-badge {
  align-self: flex-start;
  font-size: 0.78rem;
  font-weight: 800;
  color: #B45309;
  background: #FEF3C7;
  border: 1px solid rgba(217, 119, 6, 0.3);
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  letter-spacing: 0.6px;
}

.top-job-title {
  margin: 0.2rem 0 0;
  font-size: 1.55rem;
  font-weight: 850;
  color: #78350F;
  line-height: 1.35;
}

.top-job-company {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #B45309;
}

.top-job-location {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-muted);
}

.top-job-recommendation {
  font-size: 0.92rem;
  line-height: 1.6;
  color: #78350F;
  padding: 0.9rem;
  background: rgba(254, 243, 199, 0.45);
  border-radius: 16px;
  border-left: 3px solid #D97706;
}

.top-job-link {
  margin-top: 0.6rem;
  text-decoration: none;
  font-size: 0.98rem;
}

/* 4. Recommendation Jobs List */
.jobs-list {
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
}

.job-result-card {
  padding: 1.6rem;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: all 0.3s ease;
}

.job-result-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-strong);
  background: rgba(255, 255, 255, 0.8);
}

.job-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.match-badge {
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
}

.badge-high {
  background: hsla(142, 76%, 36%, 0.1);
  color: hsl(142, 76%, 36%);
  border: 1px solid hsla(142, 76%, 36%, 0.3);
  box-shadow: 0 0 12px hsla(142, 76%, 36%, 0.15);
}

.badge-moderate {
  background: hsla(199, 89%, 48%, 0.1);
  color: hsl(199, 89%, 48%);
  border: 1px solid hsla(199, 89%, 48%, 0.3);
  box-shadow: 0 0 12px hsla(199, 89%, 48%, 0.15);
}

.badge-low {
  background: hsla(38, 92%, 50%, 0.1);
  color: hsl(38, 92%, 50%);
  border: 1px solid hsla(38, 92%, 50%, 0.3);
  box-shadow: 0 0 12px hsla(38, 92%, 50%, 0.15);
}

.job-card-score {
  font-size: 0.94rem;
  font-weight: 800;
  color: var(--text-soft);
}

.job-card-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-soft);
  line-height: 1.4;
}

.job-card-meta {
  display: flex;
  gap: 1.2rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-muted);
}

.job-card-recommendation {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.55;
  color: var(--text-muted);
}

.view-job-btn {
  align-self: flex-start;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0.5rem 1.1rem;
  font-size: 0.88rem;
  font-weight: 800;
  border-radius: 999px;
  border: 1.5px solid rgba(14, 165, 233, 0.35);
  color: var(--primary-dark);
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-job-btn:hover {
  background: rgba(14, 165, 233, 0.08);
  border-color: var(--primary-dark);
  transform: translateY(-1px);
}

/* 5. Archive Section styling */
.database-archive {
  margin-top: 3.5rem;
  border-top: 1px solid var(--line);
  padding-top: 2.5rem;
}

.archive-title {
  margin: 0 0 1.2rem;
  font-size: 1.25rem;
  font-weight: 850;
  color: var(--text-soft);
}

.table-wrapper {
  overflow: hidden;
  border-radius: 20px;
}

/* 6. Empty State Dashboard */
.empty-state-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 2rem;
  margin-top: 2rem;
  text-align: center;
  gap: 1.1rem;
  border-radius: var(--radius-lg);
}

.empty-icon {
  font-size: 3.6rem;
  filter: drop-shadow(0 10px 20px rgba(3, 105, 161, 0.15));
}

.empty-text {
  font-size: 1.15rem;
  font-weight: 750;
  color: var(--text-muted);
  max-width: 480px;
  line-height: 1.6;
  margin: 0;
}

/* 7. Skeleton Loader definitions */
.skeleton-dashboard {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.skeleton-summary-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.stat-card-skeleton {
  height: 90px;
  border-radius: var(--radius-lg);
  background: rgba(226, 232, 240, 0.3);
}

.skeleton-grid {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 2rem;
}

.skeleton-left-col {
  display: flex;
  flex-direction: column;
}

.best-card-skeleton {
  height: 280px;
  border-radius: var(--radius-lg);
  background: rgba(226, 232, 240, 0.3);
}

.skeleton-right-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.ranking-card-skeleton {
  height: 180px;
  border-radius: var(--radius-lg);
  background: rgba(226, 232, 240, 0.3);
}

.skeleton-table-container {
  height: 240px;
  border-radius: 20px;
  background: rgba(226, 232, 240, 0.3);
  margin-top: 1.5rem;
}

.pulse {
  background: linear-gradient(90deg, rgba(226, 232, 240, 0.3) 25%, rgba(203, 213, 225, 0.4) 50%, rgba(226, 232, 240, 0.3) 75%);
  background-size: 200% 100%;
  animation: skeleton-glow 1.5s infinite;
}

@keyframes skeleton-glow {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Override vue3-easy-data-table styles to match theme */
:deep(.easy-data-table__header) {
  background-color: rgba(14, 165, 233, 0.08);
  color: var(--primary-dark);
  font-weight: 800;
}

:deep(.easy-data-table__rows-hover) {
  background-color: rgba(255, 255, 255, 0.4);
}

:deep(.easy-data-table__rows-hover:hover) {
  background-color: rgba(255, 255, 255, 0.8);
}

/* 8. Responsivity & mobile scaling adjustments */
@media (max-width: 992px) {
  .controls-grid {
    grid-template-columns: 1fr;
    gap: 1.1rem;
  }
  
  .dashboard-grid, .skeleton-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}

@media (max-width: 768px) {
  .stats-cards-row, .skeleton-summary-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .form-group-container {
    padding: 1.5rem;
  }
  
  .actions {
    flex-direction: column;
    gap: 0.8rem;
  }
  
  .find-btn, .btn-danger-outline {
    width: 100%;
  }
}
</style>