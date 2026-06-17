<template>
  <div class="glass-panel view-container">
    <!-- Section 2 — API Error Banner -->
    <FloatingErrorBanner
      v-if="apiError"
      v-model="showErrorBanner"
      :message="apiError.message"
      :retry-function="matchDetailed"
    />

    <h2>Detailed CV-JD Analysis</h2>
    <p class="subtitle">See exactly which skills you match and which you are missing.</p>
    
    <div class="form-group">
      <label for="cv-upload">Upload CV (PDF/DOCX):</label>
      <input id="cv-upload" type="file" @change="handleFileSelect" class="input-field file-input" :disabled="loading" />
      <span v-if="cvError" class="inline-error">{{ cvError }}</span>
    </div>
    
    <div class="form-group">
      <label for="job-desc-textarea">Job Description:</label>
      <textarea id="job-desc-textarea" v-model="jobDescription" placeholder="Paste the job requirements here..." class="input-field textarea" rows="6" :disabled="loading"></textarea>
      <span v-if="jobDescError" class="inline-error">{{ jobDescError }}</span>
    </div>

    <div class="form-group">
      <label for="domain-select">Domain:</label>
      <select id="domain-select" v-model="domain" class="input-field" :disabled="loading">
        <option value="general">General</option>
        <option value="it">IT</option>
        <option value="hr">HR</option>
        <option value="finance">Finance</option>
        <option value="creative">Creative & Marketing</option>
        <option value="sales">Sales & Business Development</option>
        <option value="legal">Legal</option>
        <option value="pr">PR & Corcom</option>
        <option value="ga">GA</option>
        <option value="cs">CS & Aftersales</option>
        <option value="operational">Operational</option>
      </select>
    </div>
    
    <button @click="matchDetailed" :disabled="loading || showLoader" class="btn-primary">
      {{ loading ? 'Analyzing...' : 'Analyze Match' }}
    </button>
    
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
      :retry-function="matchDetailed"
    />

    <!-- Empty State -->
    <div v-else-if="!detailedResult" class="empty-state-panel glass-panel">
      <div class="empty-icon">📄</div>
      <p>No analysis performed yet. Select your CV, paste the job description, and click "Analyze Match" above to start.</p>
    </div>

    <!-- Results Container -->
    <div v-else class="results detailed-results">
      <!-- Candidate Name Header -->
      <div v-if="detailedResult.candidate_name" class="candidate-name-header sub-glass-card">
        <span class="candidate-icon">👤</span>
        <div class="candidate-info">
          <span class="candidate-label">Candidate</span>
          <h3 class="candidate-name-value">{{ detailedResult.candidate_name }}</h3>
        </div>
      </div>

      <!-- Render ExplainabilityCard if reasoning is available -->
      <ExplainabilityCard
        v-if="detailedResult.reasoning"
        :match-score="detailedResult.match_score !== undefined ? detailedResult.match_score : detailedResult.similarity_score"
        :recommendation="detailedResult.recommendation"
        :matched-skills="detailedResult.matched_skills"
        :missing-skills="detailedResult.missing_skills"
        :skill-coverage-ratio="detailedResult.skill_coverage_ratio"
        :reasoning="detailedResult.reasoning"
        :domain="detailedResult.domain"
      />

      <!-- Fallback to original layout if reasoning is not available -->
      <div v-else>
        <div class="score-card" :class="getScoreClass(detailedResult.similarity_score)">
          <h3>Match Score</h3>
          <div class="score-value">{{ detailedResult.similarity_score }}%</div>
        </div>
        
        <div class="skills-grid">
          <div class="skills-card matched">
            <h4>✓ Matched Skills</h4>
            <div class="tags">
              <span v-for="skill in detailedResult.matched_skills" :key="skill" class="skill-tag skill-tag-success">{{ skill }}</span>
              <span v-if="!detailedResult.matched_skills.length" class="empty-state">No specific skills matched.</span>
            </div>
          </div>
          
          <div class="skills-card missing">
            <h4>× Missing Skills</h4>
            <div class="tags">
              <span v-for="skill in detailedResult.missing_skills" :key="skill" class="skill-tag skill-tag-danger">{{ skill }}</span>
              <span v-if="!detailedResult.missing_skills.length" class="empty-state">No missing skills!</span>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Resume Advisor CTA -->
      <div class="advisor-cta-panel glass-panel">
        <div class="advisor-cta-icon">🤖</div>
        <div class="advisor-cta-text">
          <h4>Get AI-Powered Career Recommendations</h4>
          <p>Use your analysis results to generate a personalized learning roadmap, resume tips, and career insights.</p>
        </div>
        <router-link to="/resume-advisor" id="open-advisor-btn" class="btn-advisor-cta">
          Open AI Resume Advisor →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import ExplainabilityCard from '../components/ExplainabilityCard.vue'
import AIProcessingLoader from '../components/AIProcessingLoader.vue'
import ErrorState from '../components/ErrorState.vue'
import FloatingErrorBanner from '../components/FloatingErrorBanner.vue'
import { validateFile } from '../utils/validation'

const toast = inject('toast')
const router = useRouter()

const selectedFile = ref(null)
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
const detailedResult = ref(null)

// Validation Errors
const cvError = ref('')
const jobDescError = ref('')

// Error Handlers
const apiError = ref(null)
const fatalError = ref(null)
const showErrorBanner = ref(false)

let timerInterval = null
let eventSource = null

// Define 7 steps for Detailed CV-JD Analysis
const steps = [
  'Upload CV',
  'Parse Resume',
  'Extract Skills',
  'Generate Embeddings',
  'Match CV & Job Description',
  'Generate Explainability',
  'Finalize Results'
]

watch(jobDescription, () => {
  if (jobDescription.value.trim()) {
    jobDescError.value = ''
  }
})

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  cvError.value = ''
  if (!file) return

  const fileValidation = validateFile(file)
  if (!fileValidation.valid) {
    cvError.value = fileValidation.error
    e.target.value = ''
    selectedFile.value = null
    return
  }
  selectedFile.value = file
}


const getScoreClass = (score) => {
  if (score < 30) return 'score-danger'
  if (score < 50) return 'score-warning'
  return 'score-success'
}

const handleLoaderClose = () => {
  showLoader.value = false
  loading.value = false
  if (eventSource) eventSource.close()
  clearInterval(timerInterval)
}

const matchDetailed = async () => {
  cvError.value = ''
  jobDescError.value = ''
  
  if (!selectedFile.value) {
    cvError.value = "Please upload a CV file."
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
  detailedResult.value = null
  apiError.value = null
  fatalError.value = null
  showErrorBanner.value = false
  
  const fd = new FormData()
  fd.append('cv', selectedFile.value)
  fd.append('job_description', jobDescription.value)
  fd.append('domain', domain.value)
  
  try {
    const startRes = await axios.post(`${API_BASE_URL}/api/match-detailed/start`, fd)
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
              detailedResult.value = resultRes.data
              
              if (!detailedResult.value) {
                apiError.value = { message: 'No analysis results found.' }
                showErrorBanner.value = true
                toast.warning('No analysis results found.')
              } else {
                toast.success("Analysis completed successfully.")
                // Save result to localStorage for Resume Advisor
                try {
                  const advisorData = {
                    match_score: resultRes.data.match_score ?? resultRes.data.similarity_score ?? 0,
                    matched_skills: resultRes.data.matched_skills || [],
                    missing_skills: resultRes.data.missing_skills || [],
                    recommendation: resultRes.data.recommendation || 'N/A',
                    job_description: jobDescription.value || ''
                  }
                  localStorage.setItem('advisor_analysis', JSON.stringify(advisorData))
                } catch (e) {
                  console.warn('Could not save advisor data to localStorage:', e)
                }
              }
              
              showLoader.value = false
              loading.value = false
            } catch (err) {
              console.error(err)
              status.value = 'error'
              errorMessage.value = err.message || 'Failed to fetch final match outputs.'
              apiError.value = err
              showErrorBanner.value = true
              toast.error(errorMessage.value)
            }
          }, 1000)
        } else if (data.status === 'error') {
          clearInterval(timerInterval)
          eventSource.close()
          status.value = 'error'
          errorMessage.value = data.message || 'Analysis processing failed.'
          
          apiError.value = {
            message: data.message || 'The AI service encountered an unexpected issue.'
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
    let errMsg = error.message || 'Failed to initialize match detailed analysis task.'
    
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
.inline-error {
  color: #EF4444;
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 0.35rem;
  display: block;
  text-align: left;
}

.skill-tag {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.9rem;
  border: 2px solid;
  transition: all 0.3s ease;
  cursor: default;
}

.skill-tag-success {
  background-color: rgba(34, 197, 94, 0.1);
  border-color: #22C55E;
  color: #16A34A;
}

.skill-tag-success:hover {
  background-color: rgba(34, 197, 94, 0.2);
  border-color: #16A34A;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.skill-tag-danger {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: #EF4444;
  color: #DC2626;
}

.skill-tag-danger:hover {
  background-color: rgba(239, 68, 68, 0.2);
  border-color: #DC2626;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.empty-state {
  color: #999;
  font-style: italic;
}

.score-card {
  max-width: 220px;
  margin: 0 auto 2rem;
  padding: 1.2rem;
  text-align: center;
  border-radius: 20px;
  box-shadow: var(--shadow-strong);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.score-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 28px 80px rgba(15, 23, 42, 0.22);
}

.score-card h3 {
  margin: 0 0 0.4rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  font-weight: 700;
  opacity: 0.9;
}

.score-value {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
}

.score-danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%);
  border: 2px solid var(--danger);
}

.score-danger h3 {
  color: #DC2626;
}

.score-danger .score-value {
  color: var(--text);
}

.score-warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(234, 179, 8, 0.1) 100%);
  border: 2px solid var(--warning);
}

.score-warning h3 {
  color: #D97706;
}

.score-warning .score-value {
  color: var(--text);
}

.score-success {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(22, 163, 74, 0.1) 100%);
  border: 2px solid var(--success);
}

.score-success h3 {
  color: #16A34A;
}

.score-success .score-value {
  color: var(--text);
}
.empty-state-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3.5rem 2rem;
  margin-top: 2rem;
  text-align: center;
  gap: 1rem;
}

.empty-icon {
  font-size: 2.8rem;
  filter: drop-shadow(0 8px 16px rgba(15, 23, 42, 0.08));
}

.empty-state-panel p {
  color: var(--text-muted);
  font-size: 0.98rem;
  max-width: 460px;
  line-height: 1.6;
  margin: 0;
}

/* Resume Advisor CTA */
.advisor-cta-panel {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  margin-top: 2rem;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(99, 102, 241, 0.06) 100%);
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.advisor-cta-icon {
  font-size: 2.2rem;
  flex-shrink: 0;
  filter: drop-shadow(0 4px 10px rgba(139, 92, 246, 0.3));
}

.advisor-cta-text h4 {
  margin: 0 0 0.3rem;
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-soft);
}

.advisor-cta-text p {
  margin: 0;
  font-size: 0.88rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.btn-advisor-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: linear-gradient(135deg, #7C3AED, #6366F1);
  color: white;
  padding: 0.7rem 1.4rem;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
  margin-left: auto;
}

.btn-advisor-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(124, 58, 237, 0.4);
}

@media (max-width: 640px) {
  .advisor-cta-panel {
    flex-direction: column;
    text-align: center;
  }
  .btn-advisor-cta {
    margin-left: 0;
  }
}

/* Candidate Name Header */
.candidate-name-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  border-left: 4px solid var(--primary);
}

.candidate-icon {
  font-size: 2rem;
}

.candidate-info {
  display: flex;
  flex-direction: column;
}

.candidate-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.6;
  color: var(--text-secondary, #94a3b8);
}

.candidate-name-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary, #f1f5f9);
  margin: 0;
}

</style>
