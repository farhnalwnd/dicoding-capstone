<template>
  <div class="view-wrapper">
    <!-- Section 2 — API Error Banner -->
    <FloatingErrorBanner
      v-if="apiError"
      v-model="showErrorBanner"
      :message="apiError.message"
      :retry-function="retrySearch"
    />

    <h2 class="view-title">🔍 Semantic Talent Search</h2>
    <p class="subtitle">Search for the best-fitting candidates semantically using AI-powered matching.</p>
    
    <!-- Section 1 — Search Area -->
    <SemanticSearchCard :loading="showLoader || loading" @search="handleSearch" />

    <!-- AI Processing Dashboard Loader -->
    <AIProcessingLoader
      v-if="showLoader"
      :progress="progress"
      :message="message"
      :elapsed-time="elapsedTime"
      :status="status"
      :error-message="errorMessage"
      :steps="steps"
      @close="handleLoaderClose"
    />

    <!-- Fatal Error State -->
    <ErrorState
      v-else-if="fatalError"
      :type="fatalError.type"
      :message="fatalError.message"
      :retry-function="retrySearch"
    />

    <!-- Results Area -->
    <div v-else-if="results.length" class="results-area">
      <!-- Section 2 — Search Statistics -->
      <div class="stats-cards-row">
        <!-- Candidates Found -->
        <div class="mini-stat-card sub-glass-card">
          <div class="stat-icon-wrapper primary-bg">
            <span class="stat-icon text-primary">👥</span>
          </div>
          <div class="stat-content">
            <span class="stat-label">Candidates Found</span>
            <span class="stat-number text-primary">{{ stats.found }}</span>
          </div>
        </div>

        <!-- Top Match -->
        <div class="mini-stat-card sub-glass-card">
          <div class="stat-icon-wrapper success-bg">
            <span class="stat-icon text-success">🏆</span>
          </div>
          <div class="stat-content">
            <span class="stat-label">Top Match</span>
            <span class="stat-number text-success">{{ stats.top }}%</span>
          </div>
        </div>

        <!-- Average Match -->
        <div class="mini-stat-card sub-glass-card">
          <div class="stat-icon-wrapper info-bg">
            <span class="stat-icon text-info">📊</span>
          </div>
          <div class="stat-content">
            <span class="stat-label">Average Match</span>
            <span class="stat-number text-info">{{ stats.average }}%</span>
          </div>
        </div>
      </div>

      <!-- Section 3 & 4 — Candidate Cards & Ranking Grid -->
      <div class="candidate-results-section">
        <h3 class="results-title">Ranked Candidates</h3>
        <div class="candidates-grid">
          <CandidateCard
            v-for="(candidate, index) in results"
            :key="candidate.candidate_name"
            :name="candidate.candidate_name"
            :score="candidate.similarity_score"
            :skills="candidate.skills"
            :rank="index + 1"
          />
        </div>
      </div>
    </div>

    <!-- Section 6 — Empty State -->
    <div v-else class="empty-state-panel glass-panel">
      <div class="empty-icon">🤖</div>
      <p class="empty-text">Start searching for candidates using AI semantic matching.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import SemanticSearchCard from '../components/SemanticSearchCard.vue'
import CandidateCard from '../components/CandidateCard.vue'
import AIProcessingLoader from '../components/AIProcessingLoader.vue'
import ErrorState from '../components/ErrorState.vue'
import FloatingErrorBanner from '../components/FloatingErrorBanner.vue'

const toast = inject('toast')

const loading = ref(false)
const showLoader = ref(false)
const progress = ref(0)
const elapsedTime = ref(0)
const message = ref('')
const status = ref('processing')
const errorMessage = ref('')
const results = ref([])
const lastQuery = ref('')

// Error Handlers
const apiError = ref(null)
const fatalError = ref(null)
const showErrorBanner = ref(false)

let timerInterval = null
let eventSource = null

// Define 4 steps for Semantic Talent Search
const steps = [
  'Parsing Query',
  'Generating Embedding',
  'Semantic Search',
  'Ranking Results'
]

// Compute stats dynamically from the results
const stats = computed(() => {
  if (!results.value.length) {
    return { found: 0, top: 0, average: 0 }
  }
  const found = results.value.length
  const top = results.value[0].similarity_score
  const total = results.value.reduce((acc, c) => acc + c.similarity_score, 0)
  const average = Math.round(total / found)
  return { found, top, average }
})

const handleLoaderClose = () => {
  showLoader.value = false
  loading.value = false
  if (eventSource) eventSource.close()
  clearInterval(timerInterval)
}

const retrySearch = () => {
  if (lastQuery.value) {
    handleSearch(lastQuery.value)
  }
}

const handleSearch = async (query) => {
  lastQuery.value = query
  loading.value = true
  showLoader.value = true
  progress.value = 0
  elapsedTime.value = 0
  message.value = 'Initializing search job...'
  status.value = 'processing'
  errorMessage.value = ''
  results.value = []
  apiError.value = null
  fatalError.value = null
  showErrorBanner.value = false
  
  try {
    const startRes = await axios.post(`${API_BASE_URL}/api/jobs/semantic-search/start`, { query })
    const jobId = startRes.data.job_id
    
    // Start elapsed timer
    const startTime = Date.now()
    timerInterval = setInterval(() => {
      elapsedTime.value = (Date.now() - startTime) / 1000
    }, 100)
    
    const token = localStorage.getItem('token') || ''
    eventSource = new EventSource(`${API_BASE_URL}/api/progress/${jobId}?token=${encodeURIComponent(token)}`)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        progress.value = data.progress
        message.value = data.message
        status.value = data.status
        
        if (data.status === 'completed') {
          clearInterval(timerInterval)
          eventSource.close()
          
          setTimeout(async () => {
            try {
              const resultRes = await axios.get(`${API_BASE_URL}/api/result/${jobId}`)
              results.value = resultRes.data.results || []
              
              if (results.value.length === 0) {
                apiError.value = {
                  message: 'No matching candidates were found. Try different keywords or criteria.'
                }
                showErrorBanner.value = true
                toast.warning("No matching candidates were found.")
              } else {
                toast.success("Semantic search completed successfully.")
              }
              
              showLoader.value = false
              loading.value = false
            } catch (err) {
              console.error(err)
              status.value = 'error'
              errorMessage.value = err.message || 'Failed to fetch search results.'
              apiError.value = err
              showErrorBanner.value = true
              toast.error(errorMessage.value)
            }
          }, 1000)
        } else if (data.status === 'error') {
          clearInterval(timerInterval)
          eventSource.close()
          status.value = 'error'
          errorMessage.value = data.message || 'Semantic search processing failed.'
          
          apiError.value = {
            message: data.message || 'Semantic search processing failed.'
          }
          showErrorBanner.value = true
          toast.error(apiError.value.message)
        }
      } catch (e) {
        console.error("Failed to parse SSE payload", e)
      }
    }
    
    eventSource.onerror = () => {
      clearInterval(timerInterval)
      eventSource.close()
      status.value = 'error'
      
      const isOffline = !navigator.onLine
      let errMsg = 'Connection lost while receiving progress updates.'
      let errType = 'network'
      
      if (!isOffline) {
        errMsg = 'AI processing service is currently unavailable.'
        errType = 'backend'
      }
      
      errorMessage.value = errMsg
      fatalError.value = {
        type: errType,
        message: errMsg
      }
      toast.error(errMsg)
    }
    
  } catch (error) {
    console.error(error)
    loading.value = false
    showLoader.value = false
    
    let errType = error.type || 'backend'
    let errMsg = error.message || 'Failed to initialize semantic search task.'
    
    if (error.response && error.response.status === 404) {
      errMsg = 'Processing session expired. Please start a new analysis.'
      errType = 'empty'
    }
    
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
  }
}
</script>

<style scoped>
.view-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

.view-title {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-weight: 800;
  font-size: clamp(1.65rem, 3vw, 2.25rem);
  color: var(--text);
}

.subtitle {
  color: var(--text-muted);
  font-size: 1.03rem;
  margin: 0 0 2.4rem;
  line-height: 1.7;
}

.results-area {
  animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 2. Stats Row Layout */
.stats-cards-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.mini-stat-card {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  padding: 1.1rem 1.4rem;
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.015);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.mini-stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 36px rgba(15, 23, 42, 0.035);
  background: rgba(255, 255, 255, 0.55);
}

.stat-icon-wrapper {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.03);
}

.primary-bg {
  background-color: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(14, 165, 233, 0.25);
}

.success-bg {
  background-color: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.info-bg {
  background-color: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.text-info {
  color: var(--indigo);
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

/* Candidate Results Grid */
.candidate-results-section {
  margin-top: 2.2rem;
}

.results-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-soft);
  margin-bottom: 1.2rem;
}

.candidates-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

/* Empty State Styling */
.empty-state-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4.5rem 2rem;
  margin-top: 2rem;
  text-align: center;
  gap: 1.2rem;
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
}

.empty-icon {
  font-size: 3.2rem;
  filter: drop-shadow(0 8px 16px rgba(15, 23, 42, 0.08));
}

.empty-text {
  color: var(--text-muted);
  font-size: 1.05rem;
  font-weight: 600;
  max-width: 480px;
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 768px) {
  .stats-cards-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .candidates-grid {
    grid-template-columns: 1fr;
    gap: 1.2rem;
  }
}
</style>
