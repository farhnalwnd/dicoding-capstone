<template>
  <div class="glass-panel view-container">
    <!-- Section 2 — API Error Banner -->
    <FloatingErrorBanner
      v-if="apiError"
      v-model="showErrorBanner"
      :message="apiError.message"
      :retry-function="rankCVs"
    />

    <h2>Bulk CV Ranking Dashboard</h2>
    <p class="subtitle">Upload multiple candidate CVs and compare them against your job requirements using AI matching.</p>
    
    <!-- Section 1 — Ranking Input Card -->
    <div class="form-group-container sub-glass-card">
      <div class="form-group">
        <label for="cvs-upload">Upload Candidates (PDF/DOCX):</label>
        <input 
          id="cvs-upload"
          type="file" 
          multiple 
          @change="handleMultipleFileSelect" 
          class="input-field file-input" 
          :disabled="loading"
        />
        <span v-if="cvsError" class="inline-error">{{ cvsError }}</span>
        
        <!-- Beautiful Tag Display for Selected Files -->
        <div v-if="selectedFiles.length" class="file-tags-container" aria-label="Selected candidate files">
          <div v-for="(file, index) in selectedFiles" :key="file.name" class="file-tag">
            <span class="file-icon">📄</span>
            <span class="file-name" :title="file.name">{{ file.name }}</span>
            <button 
              type="button" 
              @click="removeFile(index)" 
              class="remove-tag-btn" 
              aria-label="Remove file"
              :disabled="loading"
            >&times;</button>
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <label for="job-desc">Job Description:</label>
        <textarea 
          id="job-desc"
          v-model="jobDescription" 
          placeholder="Paste the job requirements, qualifications, and role descriptions here..." 
          class="input-field textarea" 
          rows="6"
          :disabled="loading"
        ></textarea>
        <span v-if="jobDescError" class="inline-error">{{ jobDescError }}</span>
      </div>
      <div class="form-group">
        <label for="domain-select">Domain Filter:</label>
        <select id="domain-select" v-model="domain" class="input-field" :disabled="loading">
          <option v-for="option in domainOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <small class="helper-text">
          Selecting a specific domain optimizes the AI parser to weigh relevant industry skills.
        </small>
      </div>

      <button 
        @click="rankCVs" 
        :disabled="showLoader || loading" 
        class="btn-primary rank-btn"
      >
        <span>⚡</span>
        {{ loading ? 'Ranking Candidates...' : 'Rank Candidates' }}
      </button>
    </div>

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
      :retry-function="rankCVs"
    />

    <!-- Empty State -->
    <div v-else-if="!rankings.length" class="empty-state-panel glass-panel">
      <div class="empty-icon">📊</div>
      <p class="empty-text">No candidate ranking performed yet.</p>
      <p class="empty-subtext">Upload candidate CVs and rank them using AI to populate the recruitment leaderboard.</p>
    </div>

    <!-- Results Dashboard -->
    <div v-else class="results-dashboard">
      <!-- Section 2 — Ranking Summary -->
      <div class="summary-cards-row">
        <div class="mini-stat-card sub-glass-card">
          <div class="stat-icon-wrapper primary-bg">👥</div>
          <div class="stat-content">
            <span class="stat-label">Total Candidates</span>
            <span class="stat-number text-primary">{{ totalCandidates }}</span>
          </div>
        </div>

        <div class="mini-stat-card sub-glass-card">
          <div class="stat-icon-wrapper success-bg">🏆</div>
          <div class="stat-content">
            <span class="stat-label">Top Match Score</span>
            <span class="stat-number text-success">{{ topScore.toFixed(1) }}%</span>
          </div>
        </div>

        <div class="mini-stat-card sub-glass-card">
          <div class="stat-icon-wrapper info-bg">📈</div>
          <div class="stat-content">
            <span class="stat-label">Average Score</span>
            <span class="stat-number text-info">{{ averageScore }}%</span>
          </div>
        </div>
      </div>

      <!-- Main Dashboard Grid Layout -->
      <div class="dashboard-grid">
        <!-- Left Column: Best Match, Leaderboard, & Distribution Chart -->
        <div class="left-column">
          <!-- Section 5 — Best Candidate Highlight -->
          <div class="section-container" v-if="bestCandidate">
            <h3 class="section-title">🏆 Top Candidate</h3>
            <BestCandidateCard
              :name="bestCandidate.name"
              :score="bestCandidate.score"
              :semantic-score="bestCandidate.semantic_score"
              :skill-score="bestCandidate.domain_skill_score"
              :matched-count="bestCandidate.matched_skills_count"
              :missing-count="bestCandidate.missing_skills_count"
              :matched-skills="bestCandidate.matched_skills"
              :missing-skills="bestCandidate.missing_skills"
              :filename="bestCandidate.filename"
              :status="bestCandidate.status"
              style="cursor: pointer;"
              @click="openModal(bestCandidate)"
              @move-to-talent-pool="handleMoveToTalentPool(bestCandidate)"
              @move-to-interview="handleMoveToInterview(bestCandidate)"
            />
          </div>

          <!-- Section 3 — Leaderboard -->
          <div class="section-container">
            <LeaderboardCard :candidates="rankings" @select-candidate="openModal" />
          </div>

          <!-- Section 6 — Score Distribution Chart -->
          <div class="section-container sub-glass-card chart-card">
            <h3 class="chart-title">Candidate Score Distribution</h3>
            <div class="chart-wrapper">
              <canvas ref="chartCanvas" id="score-distribution-chart"></canvas>
            </div>
          </div>
        </div>

        <!-- Right Column: Candidate Ranking Cards List -->
        <div class="right-column">
          <h3 class="section-title">All Candidate Matches</h3>
          <div class="ranking-cards-list">
            <RankingCard
              v-for="r in rankings"
              :key="r.filename || r.name"
              :name="r.name"
              :score="r.score"
              :rank="r.rank"
              :semantic-score="r.semantic_score"
              :skill-score="r.domain_skill_score"
              :matched-count="r.matched_skills_count"
              :missing-count="r.missing_skills_count"
              :filename="r.filename"
              :status="r.status"
              style="cursor: pointer;"
              @click="openModal(r)"
              @move-to-talent-pool="handleMoveToTalentPool(r)"
              @move-to-interview="handleMoveToInterview(r)"
            />
          </div>
        </div>

      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="selectedCandidate" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content glass-panel">
        <button class="close-btn" @click="closeModal">&times;</button>
        <h3 class="modal-title">{{ selectedCandidate.name }}'s Details</h3>
        
        <div class="modal-body">
          <div class="chart-container">
            <h4>Candidate Competency Radar</h4>
            <div v-if="chartData" class="radar-wrapper">
              <Radar :data="chartData" :options="chartOptions" />
            </div>
            <div v-else class="empty-chart-fallback">
              <div class="fallback-icon">📊</div>
              <p class="fallback-title">No Skills to Analyze</p>
              <p class="fallback-text">
                Please provide a detailed job description containing specific skills to visualize the candidate's skill proficiency.
              </p>
            </div>
          </div>

          <div class="questions-container">
            <h4>Interview Questions</h4>
            <p class="subtitle" style="font-size:0.85rem;margin-bottom:1rem;">Generate tailored questions based on candidate's skills and gaps.</p>
            <button @click="generateQuestions" class="btn-primary" :disabled="loadingQuestions">
              {{ loadingQuestions ? 'Generating...' : 'Generate Questions' }}
            </button>
            
            <ul v-if="generatedQuestions.length" class="questions-list">
              <li v-for="(q, idx) in generatedQuestions" :key="idx" class="question-item">{{ q }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onUnmounted, nextTick, inject } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import { Chart, registerables } from 'chart.js'
import { Radar } from 'vue-chartjs'
import BestCandidateCard from '../components/BestCandidateCard.vue'
import LeaderboardCard from '../components/LeaderboardCard.vue'
import RankingCard from '../components/RankingCard.vue'
import AIProcessingLoader from '../components/AIProcessingLoader.vue'
import ErrorState from '../components/ErrorState.vue'
import FloatingErrorBanner from '../components/FloatingErrorBanner.vue'
import { validateFile } from '../utils/validation'

// Register Chart.js components
Chart.register(...registerables)

const toast = inject('toast')


const selectedFiles = ref([])
const jobDescription = ref('')
const domain = ref('general')
const loading = ref(false)

// SSE Loading State
const showLoader = ref(false)
const progress = ref(0)
const elapsedTime = ref(0)
const message = ref('')
const status = ref('processing')
const errorMessage = ref('')
const rankings = ref([])

// Validation states
const cvsError = ref('')
const jobDescError = ref('')

// Error Handlers
const apiError = ref(null)
const fatalError = ref(null)
const showErrorBanner = ref(false)

const chartCanvas = ref(null)
let chartInstance = null
let timerInterval = null
let eventSource = null

// Define 4 steps for HR Candidate Ranking
const steps = [
  'Parsing CVs',
  'Extracting Skills',
  'Embedding Generation',
  'Ranking Candidates'
]

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
  { value: 'cs', label: 'CS & Aftersales' },
  { value: 'operational', label: 'Operational' }
]

watch(jobDescription, () => {
  if (jobDescription.value.trim()) {
    jobDescError.value = ''
  }
})

// Calculated Summary Stats
const totalCandidates = computed(() => rankings.value.length)
const topScore = computed(() => rankings.value.length ? Math.max(...rankings.value.map(r => r.score)) : 0)
const averageScore = computed(() => {
  if (!rankings.value.length) return 0
  const total = rankings.value.reduce((sum, r) => sum + r.score, 0)
  return Math.round(total / rankings.value.length)
})

// Best Candidate (#1 Rank)
const bestCandidate = computed(() => {
  return rankings.value.find(r => r.rank === 1) || rankings.value[0] || null
})

const handleMultipleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  cvsError.value = ''
  for (let f of files) {
    const fileValidation = validateFile(f)
    if (!fileValidation.valid) {
      cvsError.value = fileValidation.error
      continue
    }
    if (!selectedFiles.value.some(existing => existing.name === f.name)) {
      selectedFiles.value.push(f)
    }
  }
  e.target.value = ''
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const handleLoaderClose = () => {
  showLoader.value = false
  loading.value = false
  if (eventSource) eventSource.close()
  clearInterval(timerInterval)
}

const rankCVs = async () => {

  cvsError.value = ''
  jobDescError.value = ''
  
  if (!selectedFiles.value.length) {
    cvsError.value = "Please upload at least one CV."
    return
  }
  if (!jobDescription.value.trim()) {
    jobDescError.value = "Please enter a Job Description."
    return
  }
  
  loading.value = true
  showLoader.value = true
  progress.value = 0
  elapsedTime.value = 0
  message.value = 'Uploading files and initializing job...'
  status.value = 'processing'
  errorMessage.value = ''
  rankings.value = []
  apiError.value = null
  fatalError.value = null
  showErrorBanner.value = false
  
  const fd = new FormData()
  for (let f of selectedFiles.value) {
    fd.append('cvs', f)
  }
  fd.append('job_description', jobDescription.value)
  fd.append('domain', domain.value)
  
  try {
    const startRes = await axios.post(`${API_BASE_URL}/api/hr/rank/start`, fd)
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
              rankings.value = (resultRes.data || []).map(r => ({
                ...r,
                status: r.status || 'screening'
              }))
              
              if (!rankings.value.length) {
                apiError.value = { message: 'No candidates were ranked.' }
                showErrorBanner.value = true
                toast.warning('No candidates were ranked.')
              } else {
                toast.success("Candidates ranked successfully.")
              }
              
              showLoader.value = false
              loading.value = false
            } catch (err) {
              console.error(err)
              status.value = 'error'
              errorMessage.value = err.message || 'Failed to fetch final candidate ranks.'
              apiError.value = err
              showErrorBanner.value = true
              toast.error(errorMessage.value)
            }
          }, 1000)
        } else if (data.status === 'error') {
          clearInterval(timerInterval)
          eventSource.close()
          status.value = 'error'
          errorMessage.value = data.message || 'Candidate ranking failed.'
          
          apiError.value = {
            message: data.message || 'Candidate ranking failed.'
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
    let errMsg = error.message || 'Failed to initialize bulk CV ranking task.'
    
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
// Chart.js Score Distribution instantiation

const updateChart = () => {
  if (!chartCanvas.value) return
  if (chartInstance) {
    chartInstance.destroy()
  }
  const ctx = chartCanvas.value.getContext('2d')
  
  // Sort rankings to display highest score first
  const sortedRankings = [...rankings.value].sort((a, b) => b.score - a.score)
  const labels = sortedRankings.map(r => r.name)
  const data = sortedRankings.map(r => r.score)
  
  // Custom score color mapping
  const backgroundColors = sortedRankings.map(r => {
    if (r.score >= 90) return 'rgba(34, 197, 94, 0.75)'
    if (r.score >= 75) return 'rgba(14, 165, 233, 0.75)'
    if (r.score >= 60) return 'rgba(245, 158, 11, 0.75)'
    return 'rgba(239, 68, 68, 0.75)'
  })
  const borderColors = sortedRankings.map(r => {
    if (r.score >= 90) return '#22C55E'
    if (r.score >= 75) return '#0EA5E9'
    if (r.score >= 60) return '#F59E0B'
    return '#EF4444'
  })

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Match Score (%)',
        data: data,
        backgroundColor: backgroundColors,
        borderColor: borderColors,
        borderWidth: 1.5,
        borderRadius: 8,
        barPercentage: 0.6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleFont: { family: 'Inter', weight: '700' },
          bodyFont: { family: 'Inter' },
          callbacks: {
            label: (context) => `Match Score: ${context.parsed.x.toFixed(1)}%`
          }
        }
      },
      scales: {
        x: {
          min: 0,
          max: 100,
          grid: {
            color: 'rgba(148, 163, 184, 0.08)'
          },
          ticks: {
            color: '#64748B',
            font: {
              family: 'Inter',
              weight: '700',
              size: 11
            }
          }
        },
        y: {
          grid: {
            display: false
          },
          ticks: {
            color: '#1E3A5F',
            font: {
              family: 'Inter',
              weight: '800',
              size: 11
            }
          }
        }
      }
    }
  })
}

// Watch rankings list and draw chart
watch(rankings, (newRankings) => {
  if (newRankings && newRankings.length) {
    nextTick(() => {
      updateChart()
    })
  }
}, { deep: true })

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})

// Modal State
const selectedCandidate = ref(null)
const chartData = ref(null)
const generatedQuestions = ref([])
const loadingQuestions = ref(false)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: {
        stepSize: 20,
        backdropColor: 'transparent',
      },
      grid: {
        color: 'rgba(3, 105, 161, 0.2)'
      },
      angleLines: {
        color: 'rgba(3, 105, 161, 0.2)'
      },
      pointLabels: {
        font: {
          family: "'Inter', sans-serif",
          size: 11
        },
        color: '#0369A1'
      }
    }
  },
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        font: {
          family: "'Inter', sans-serif"
        }
      }
    }
  }
}

const openModal = (candidate) => {
  selectedCandidate.value = candidate
  generatedQuestions.value = []
  
  // Build 6-dimension Competency Radar (always full, always insightful)
  const semanticMatch = candidate.semantic_score ?? 0
  const skillCoverage = candidate.domain_skill_score ?? 0
  const domainRelevance = candidate.domain_relevance ?? 0
  const experienceDepth = candidate.experience_depth ?? 0
  const skillBreadth = candidate.skill_breadth ?? 0
  const overallScore = candidate.score ?? 0

  chartData.value = {
    labels: [
      'Semantic Match',
      'Skill Coverage',
      'Domain Relevance',
      'Experience Depth',
      'Skill Breadth',
      'Overall Score'
    ],
    datasets: [
      {
        label: candidate.name || 'Candidate',
        backgroundColor: 'rgba(14, 165, 233, 0.2)',
        borderColor: 'rgba(14, 165, 233, 1)',
        pointBackgroundColor: 'rgba(14, 165, 233, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(14, 165, 233, 1)',
        data: [
          semanticMatch,
          skillCoverage,
          domainRelevance,
          experienceDepth,
          skillBreadth,
          overallScore
        ]
      }
    ]
  }
}

const closeModal = () => {
  selectedCandidate.value = null
}

const generateQuestions = async () => {
  if (!selectedCandidate.value) return
  
  loadingQuestions.value = true
  try {
    const reqData = {
      matched_skills: selectedCandidate.value.matched_skills || [],
      missing_skills: selectedCandidate.value.missing_skills || []
    }
    const res = await axios.post(`${API_BASE_URL}/api/hr/generate-questions`, reqData)
    generatedQuestions.value = res.data.questions
    toast.success("Interview questions generated successfully")
  } catch (error) {
    console.error(error)
    toast.error("Failed to generate questions")
  }
  loadingQuestions.value = false
}

const handleMoveToTalentPool = async (candidate) => {
  if (!candidate.id) {
    toast.error("Candidate ID not found. Cannot update status.")
    return
  }
  try {
    await axios.patch(`${API_BASE_URL}/api/candidates/${candidate.id}/status`, {
      status: 'talent_pool'
    })
    candidate.status = 'talent_pool'
    toast.success(`${candidate.name} moved to Talent Pool successfully.`)
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.detail || "Failed to move candidate to Talent Pool.")
  }
}

const handleMoveToInterview = async (candidate) => {
  if (!candidate.id) {
    toast.error("Candidate ID not found. Cannot update status.")
    return
  }
  try {
    await axios.patch(`${API_BASE_URL}/api/candidates/${candidate.id}/status`, {
      status: 'interview'
    })
    candidate.status = 'interview'
    toast.success(`${candidate.name} moved to Interview successfully.`)
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.detail || "Failed to move candidate to Interview.")
  }
}
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

.form-group-container {
  padding: 2.2rem;
  border-radius: var(--radius-lg);
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.42);
}

.sub-glass-card {
  border: 1px solid var(--glass-border);
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.02);
}

.file-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 0.95rem;
  padding: 0.8rem;
  background: rgba(255, 255, 255, 0.35);
  border: 1px solid rgba(14, 165, 233, 0.12);
  border-radius: 16px;
  min-height: 48px;
}

.file-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.2);
  color: var(--primary-dark);
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  max-width: 250px;
  box-shadow: 0 4px 10px rgba(14, 165, 233, 0.03);
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-tag-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.25rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  height: 100%;
  transition: color 0.18s ease;
}

.remove-tag-btn:hover {
  color: var(--danger);
}

.rank-btn {
  font-size: 1rem;
  min-width: 200px;
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
  gap: 1rem;
}

.empty-icon {
  font-size: 3.5rem;
  filter: drop-shadow(0 10px 20px rgba(3, 105, 161, 0.15));
}

.empty-text {
  font-size: 1.25rem;
  font-weight: 850;
  color: var(--text-soft);
  margin: 0;
}

.empty-subtext {
  font-size: 0.95rem;
  color: var(--text-muted);
  max-width: 450px;
  line-height: 1.6;
  margin: 0;
}

/* Summary Cards Area */
.summary-cards-row {
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
}

.stat-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.03);
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

.text-primary {
  color: var(--primary-dark);
}

.text-success {
  color: #16A34A;
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
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-number {
  font-size: 1.55rem;
  font-weight: 900;
  line-height: 1.2;
}

.filename-text,
.skill-count-text {
  display: block;
  margin-top: 0.25rem;
  color: #64748B;
  font-size: 0.6rem;
  font-weight: 500;
}


/* Dashboard Grid Properties */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 2rem;
  margin-top: 1rem;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-container {
  display: flex;
  flex-direction: column;
  gap: 0.95rem;
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 850;
  color: var(--text-soft);
}

.chart-card {
  padding: 2rem;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.chart-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 850;
  color: var(--text-soft);
}

.chart-wrapper {
  position: relative;
  width: 100%;
  height: 280px;
}

.ranking-cards-list {
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
}

/* Responsive design properties */
@media (max-width: 992px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .summary-cards-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

/* Modal Styles */
.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background-color: rgba(14, 165, 233, 0.05) !important;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 2rem;
  border-radius: 16px;
  animation: slideUp 0.3s ease;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  font-size: 2rem;
  background: none;
  border: none;
  color: #64748B;
  cursor: pointer;
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: #EF4444;
}

.modal-title {
  margin-top: 0;
  color: #0369A1;
  border-bottom: 2px solid rgba(3, 105, 161, 0.1);
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
}

.modal-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 768px) {
  .modal-body {
    grid-template-columns: 1fr;
  }
}

.chart-container, .questions-container {
  background: rgba(255, 255, 255, 0.5);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(14, 165, 233, 0.2);
}

.radar-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
}

.questions-container h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #0369A1;
}

.questions-list {
  margin-top: 1.5rem;
  padding-left: 0;
  list-style-type: none;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.question-item {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  font-size: 0.95rem;
  color: #334155;
  border-left: 4px solid #0EA5E9;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.empty-chart-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 300px;
  padding: 1.5rem;
}

.fallback-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  filter: drop-shadow(0 8px 16px rgba(14, 165, 233, 0.15));
}

.fallback-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-soft);
  margin: 0 0 0.5rem;
}

.fallback-text {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
  max-width: 280px;
}
</style>
