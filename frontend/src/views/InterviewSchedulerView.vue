<template>
  <div class="glass-panel view-container">
    <!-- API Error Banner -->
    <FloatingErrorBanner
      v-if="apiError"
      v-model="showErrorBanner"
      :message="apiError.message"
      :retry-function="fetchInterviews"
    />

    <h2 class="view-title">📅 AI Interview Scheduler</h2>
    <p class="subtitle">Manage interview queues, generate tailored screening questions, and schedule video meetings.</p>

    <!-- Mini Dashboard Stats for Interviews -->
    <div class="stats-row" v-if="!loading && !fatalError && interviews.length > 0">
      <div class="mini-stat-card sub-glass-card">
        <div class="stat-icon-wrapper info-bg">⏳</div>
        <div class="stat-content">
          <span class="stat-label">Pending Schedule</span>
          <span class="stat-number text-info">{{ pendingCount }}</span>
        </div>
      </div>
      <div class="mini-stat-card sub-glass-card">
        <div class="stat-icon-wrapper success-bg">📆</div>
        <div class="stat-content">
          <span class="stat-label">Scheduled Interviews</span>
          <span class="stat-number text-success">{{ scheduledCount }}</span>
        </div>
      </div>
      <div class="mini-stat-card sub-glass-card">
        <div class="stat-icon-wrapper primary-bg">👥</div>
        <div class="stat-content">
          <span class="stat-label">Total in Queue</span>
          <span class="stat-number text-primary">{{ interviews.length }}</span>
        </div>
      </div>
    </div>

    <!-- Controls Panel -->
    <div class="controls-panel sub-glass-card">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search candidate by name..." 
          class="input-field search-input"
        />
      </div>

      <div class="filter-group">
        <label for="position-filter">Position:</label>
        <select id="position-filter" v-model="selectedPosition" class="input-field select-input">
          <option value="">All Positions</option>
          <option v-for="pos in uniquePositions" :key="pos" :value="pos">{{ pos }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="status-filter">Status:</label>
        <select id="status-filter" v-model="selectedStatus" class="input-field select-input">
          <option value="">All Statuses</option>
          <option value="pending">Pending Schedule</option>
          <option value="scheduled">Scheduled</option>
        </select>
      </div>
    </div>

    <!-- Error State -->
    <ErrorState
      v-if="fatalError"
      :type="fatalError.type"
      :message="fatalError.message"
      :retry-function="fetchInterviews"
    />

    <!-- Loading State (Skeleton cards) -->
    <div v-else-if="loading" class="skeleton-grid">
      <div v-for="n in 3" :key="n" class="skeleton-card glass-panel loading-shimmer">
        <div class="skeleton-header">
          <div class="skeleton-name"></div>
          <div class="skeleton-badge"></div>
        </div>
        <div class="skeleton-body-line"></div>
        <div class="skeleton-body-line short"></div>
        <div class="skeleton-actions">
          <div class="skeleton-btn"></div>
          <div class="skeleton-btn"></div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredInterviews.length === 0" class="empty-state-panel glass-panel">
      <div class="empty-icon">📅</div>
      <p class="empty-text">No interviews in the queue.</p>
      <p class="empty-subtext">
        {{ searchQuery || selectedPosition || selectedStatus ? 'Try adjusting your filters or search keywords.' : 'Move candidates to Interview on the Bulk CV Ranking or Talent Pool page to populate this list.' }}
      </p>
    </div>

    <!-- Interviews Queue List -->
    <div v-else class="interviews-container">
      <div class="interviews-grid">
        <div 
          v-for="candidate in filteredInterviews" 
          :key="candidate.id" 
          class="interview-card glass-panel"
          :class="{ 'border-scheduled': candidate.interview_status === 'scheduled' }"
        >
          <!-- Badge status -->
          <div class="card-top-row">
            <div class="candidate-header">
              <h3 class="candidate-name">{{ candidate.candidate_name }}</h3>
              <span class="job-title">💼 {{ candidate.job_title }}</span>
            </div>
            
            <div class="status-badge-container">
              <span class="status-pill" :class="candidate.interview_status">
                {{ candidate.interview_status === 'scheduled' ? 'Scheduled' : 'Pending Schedule' }}
              </span>
            </div>
          </div>

          <!-- Schedule details -->
          <div class="schedule-details sub-glass-card" v-if="candidate.interview_status === 'scheduled'">
            <div class="schedule-row">
              <span class="icon">📅</span>
              <span><strong>Date:</strong> {{ candidate.interview_date }}</span>
            </div>
            <div class="schedule-row">
              <span class="icon">⏰</span>
              <span><strong>Time:</strong> {{ candidate.interview_time }}</span>
            </div>
            <div class="schedule-row meeting-link-row">
              <span class="icon">🔗</span>
              <span>
                <strong>Meeting Link:</strong> 
                <a :href="candidate.meeting_link" target="_blank" class="meeting-link">{{ candidate.meeting_link }}</a>
              </span>
            </div>
          </div>
          <div class="schedule-details no-schedule" v-else>
            <span class="icon">⏳</span> No interview scheduled yet.
          </div>

          <!-- Match Score -->
          <div class="score-row">
            <span class="score-label">Match Score:</span>
            <span class="score-number">{{ candidate.match_score.toFixed(1) }}%</span>
          </div>

          <!-- Actions Footer -->
          <div class="card-footer">
            <button 
              type="button" 
              class="btn-footer btn-schedule"
              @click="openScheduleModal(candidate)"
            >
              📅 {{ candidate.interview_status === 'scheduled' ? 'Reschedule' : 'Schedule' }}
            </button>
            
            <button 
              type="button" 
              class="btn-footer btn-ai-q"
              @click="loadCandidateQuestions(candidate)"
            >
              🧠 AI Questions
            </button>

            <button 
              type="button" 
              class="btn-footer btn-hire"
              @click="confirmDecision(candidate, 'hired')"
            >
              🎉 Hire
            </button>

            <button 
              type="button" 
              class="btn-footer btn-reject"
              @click="confirmDecision(candidate, 'rejected')"
            >
              ❌ Reject
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedule Dialog Modal -->
    <div v-if="showScheduleModal" class="modal-overlay" @click.self="closeScheduleModal">
      <div class="modal-content glass-panel form-modal">
        <button class="close-btn" @click="closeScheduleModal">&times;</button>
        <h3 class="modal-title">📅 Schedule Interview</h3>
        <p class="modal-subtitle">Schedule video interview for <strong>{{ selectedCandidate?.candidate_name }}</strong></p>
        
        <form @submit.prevent="scheduleInterview" class="modal-form">
          <div class="form-group">
            <label for="interview-date">Date:</label>
            <input 
              id="interview-date"
              type="date" 
              v-model="scheduleForm.date" 
              class="input-field" 
              required
            />
          </div>
          <div class="form-group">
            <label for="interview-time">Time:</label>
            <input 
              id="interview-time"
              type="time" 
              v-model="scheduleForm.time" 
              class="input-field" 
              required
            />
          </div>
          <div class="form-group">
            <label for="meet-link">Video Meeting Link:</label>
            <input 
              id="meet-link"
              type="url" 
              v-model="scheduleForm.meeting_link" 
              placeholder="https://meet.google.com/..." 
              class="input-field" 
              required
            />
          </div>
          <div class="modal-footer-btns">
            <button type="button" class="btn-cancel" @click="closeScheduleModal" :disabled="actionLoading">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="actionLoading">
              {{ actionLoading ? 'Scheduling...' : 'Save Schedule' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- AI Questions Modal -->
    <div v-if="showQuestionsModal" class="modal-overlay" @click.self="closeQuestionsModal">
      <div class="modal-content glass-panel questions-modal">
        <button class="close-btn" @click="closeQuestionsModal">&times;</button>
        <h3 class="modal-title">🧠 AI Tailored Interview Questions</h3>
        <p class="modal-subtitle">Generated questions based on <strong>{{ selectedCandidate?.candidate_name }}</strong>'s CV and skill matches.</p>
        
        <div v-if="loadingQuestions" class="loading-questions-state">
          <div class="spinner"></div>
          <p>Generating questions using AI...</p>
        </div>
        <div v-else class="questions-list-container">
          <ul class="questions-list">
            <li v-for="(q, idx) in generatedQuestions" :key="idx" class="question-item">
              <span class="q-number">Q{{ idx + 1 }}</span>
              <p class="q-text">{{ q }}</p>
            </li>
          </ul>
        </div>
        <div class="modal-footer-btns">
          <button class="btn-primary" @click="closeQuestionsModal">Done</button>
        </div>
      </div>
    </div>

    <!-- Decision Confirmation Modal (Hire / Reject) -->
    <div v-if="showDecisionModal" class="modal-overlay" @click.self="closeDecisionModal">
      <div class="modal-content glass-panel decision-modal" :class="decisionType === 'hired' ? 'hired-theme' : 'rejected-theme'">
        <button class="close-btn" @click="closeDecisionModal">&times;</button>
        <h3 class="modal-title" :class="decisionType === 'hired' ? 'text-success' : 'text-danger'">
          {{ decisionType === 'hired' ? '🎉 Confirm Hire Decision' : '⚠️ Confirm Candidate Rejection' }}
        </h3>
        <div class="modal-body-confirm">
          <p>Are you sure you want to mark <strong>{{ selectedCandidate?.candidate_name }}</strong> as <strong>{{ decisionType === 'hired' ? 'Hired' : 'Rejected' }}</strong>?</p>
          <p class="warning-subtext">This will update their workflow pipeline status.</p>
        </div>
        <div class="modal-footer-btns">
          <button class="btn-cancel" @click="closeDecisionModal" :disabled="actionLoading">Cancel</button>
          <button 
            type="button"
            class="btn-decision" 
            :class="decisionType === 'hired' ? 'btn-confirm-hired' : 'btn-confirm-reject'" 
            @click="submitDecision" 
            :disabled="actionLoading"
          >
            {{ actionLoading ? 'Processing...' : (decisionType === 'hired' ? 'Yes, Hire Candidate' : 'Yes, Reject Candidate') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import ErrorState from '../components/ErrorState.vue'
import FloatingErrorBanner from '../components/FloatingErrorBanner.vue'

const toast = inject('toast')

const interviews = ref([])
const loading = ref(true)
const actionLoading = ref(false)
const searchQuery = ref('')
const selectedPosition = ref('')
const selectedStatus = ref('')

// Error handlers
const apiError = ref(null)
const fatalError = ref(null)
const showErrorBanner = ref(false)

// Modals states
const showScheduleModal = ref(false)
const showQuestionsModal = ref(false)
const showDecisionModal = ref(false)
const selectedCandidate = ref(null)

const scheduleForm = ref({
  date: '',
  time: '',
  meeting_link: ''
})

const loadingQuestions = ref(false)
const generatedQuestions = ref([])
const decisionType = ref('')

const fetchInterviews = async () => {
  loading.value = true
  apiError.value = null
  fatalError.value = null
  showErrorBanner.value = false
  
  try {
    const res = await axios.get(`${API_BASE_URL}/api/interviews`)
    interviews.value = res.data || []
  } catch (error) {
    console.error(error)
    const isOffline = !navigator.onLine
    let errMsg = error.response?.data?.detail || 'Failed to fetch interview queue.'
    if (isOffline) {
      fatalError.value = { type: 'network', message: 'Connection lost. Please check your network connection.' }
    } else {
      apiError.value = { message: errMsg }
      showErrorBanner.value = true
    }
    toast.error(errMsg)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchInterviews()
})

// Stats counts
const pendingCount = computed(() => interviews.value.filter(c => c.interview_status === 'pending').length)
const scheduledCount = computed(() => interviews.value.filter(c => c.interview_status === 'scheduled').length)

// Unique list of positions for filter
const uniquePositions = computed(() => {
  const positions = interviews.value.map(c => c.job_title).filter(Boolean)
  return [...new Set(positions)]
})

// Search, Filter
const filteredInterviews = computed(() => {
  let list = [...interviews.value]
  
  // Search
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter(c => c.candidate_name.toLowerCase().includes(q))
  }
  
  // Position filter
  if (selectedPosition.value) {
    list = list.filter(c => c.job_title === selectedPosition.value)
  }
  
  // Status filter
  if (selectedStatus.value) {
    list = list.filter(c => c.interview_status === selectedStatus.value)
  }
  
  return list
})

// Schedule dialog helpers
const openScheduleModal = (candidate) => {
  selectedCandidate.value = candidate
  scheduleForm.value = {
    date: candidate.interview_date || '',
    time: candidate.interview_time || '',
    meeting_link: candidate.meeting_link || ''
  }
  showScheduleModal.value = true
}

const closeScheduleModal = () => {
  showScheduleModal.value = false
  selectedCandidate.value = null
}

const scheduleInterview = async () => {
  if (!selectedCandidate.value) return
  actionLoading.value = true
  
  try {
    const candidate = selectedCandidate.value
    await axios.post(`${API_BASE_URL}/api/candidates/${candidate.id}/schedule`, scheduleForm.value)
    toast.success(`Interview for ${candidate.candidate_name} scheduled successfully.`)
    
    // Update locally
    const found = interviews.value.find(c => c.id === candidate.id)
    if (found) {
      found.interview_status = 'scheduled'
      found.interview_date = scheduleForm.value.date
      found.interview_time = scheduleForm.value.time
      found.meeting_link = scheduleForm.value.meeting_link
    }
    closeScheduleModal()
  } catch (error) {
    console.error(error)
    toast.error(error.response?.data?.detail || 'Failed to schedule interview.')
  } finally {
    actionLoading.value = false
  }
}

// AI Questions helpers
const loadCandidateQuestions = async (candidate) => {
  selectedCandidate.value = candidate
  showQuestionsModal.value = true
  loadingQuestions.value = true
  generatedQuestions.value = []
  
  try {
    const res = await axios.post(`${API_BASE_URL}/api/candidates/${candidate.id}/generate-questions`)
    generatedQuestions.value = res.data.questions || []
    toast.success("AI interview questions generated")
  } catch (error) {
    console.error(error)
    toast.error("Failed to generate AI interview questions")
    closeQuestionsModal()
  } finally {
    loadingQuestions.value = false
  }
}

const closeQuestionsModal = () => {
  showQuestionsModal.value = false
  selectedCandidate.value = null
  generatedQuestions.value = []
}

// Decisions helpers
const confirmDecision = (candidate, type) => {
  selectedCandidate.value = candidate
  decisionType.value = type
  showDecisionModal.value = true
}

const closeDecisionModal = () => {
  showDecisionModal.value = false
  selectedCandidate.value = null
  decisionType.value = ''
}

const submitDecision = async () => {
  if (!selectedCandidate.value) return
  actionLoading.value = true
  
  try {
    const candidate = selectedCandidate.value
    await axios.patch(`${API_BASE_URL}/api/candidates/${candidate.id}/status`, {
      status: decisionType.value
    })
    toast.success(`${candidate.candidate_name} marked as ${decisionType.value === 'hired' ? 'Hired' : 'Rejected'}.`)
    interviews.value = interviews.value.filter(c => c.id !== candidate.id)
    closeDecisionModal()
  } catch (error) {
    console.error(error)
    toast.error(error.response?.data?.detail || 'Failed to submit final decision.')
  } finally {
    actionLoading.value = false
  }
}
</script>

<style scoped>
.view-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 2.2rem 2.8rem;
}

.view-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.85rem;
  font-weight: 850;
  color: var(--primary-dark);
}

.subtitle {
  color: var(--text-muted);
  font-size: 1rem;
  margin: 0 0 2.2rem 0;
}

/* Stats cards layout */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
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
  font-size: 1.55rem;
  font-weight: 900;
  line-height: 1.2;
}

/* Controls layout */
.controls-panel {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.25rem 2rem;
  border-radius: var(--radius-lg);
  margin-bottom: 2.2rem;
  flex-wrap: wrap;
}

.search-box {
  flex-grow: 1;
  min-width: 280px;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1.1rem;
  font-size: 1rem;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding-left: 2.8rem !important;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.filter-group label {
  font-size: 0.88rem;
  font-weight: 800;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.select-input {
  min-width: 180px;
}

.input-field {
  padding: 0.65rem 1rem;
  border-radius: 14px;
  border: 1px solid rgba(14, 165, 233, 0.22);
  background: rgba(255, 255, 255, 0.65);
  color: var(--text-soft);
  font-weight: 600;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
  background: white;
}

/* Interviews Queue layout */
.interviews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.6rem;
}

.interview-card {
  padding: 1.8rem;
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  transition: all 0.3s ease;
  position: relative;
}

.interview-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-strong);
  border-color: rgba(255, 255, 255, 0.85);
}

.border-scheduled {
  border-color: rgba(34, 197, 94, 0.3);
  box-shadow: 0 10px 30px rgba(34, 197, 94, 0.05), var(--shadow-soft);
}

.card-top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.candidate-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.candidate-name {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 850;
  color: var(--text-soft);
}

.job-title {
  font-size: 0.82rem;
  color: var(--text-muted);
  font-weight: 600;
}

.status-badge-container {
  flex-shrink: 0;
}

.status-pill {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid;
}

.status-pill.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #D97706;
  border-color: rgba(245, 158, 11, 0.2);
}

.status-pill.scheduled {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border-color: rgba(16, 185, 129, 0.2);
}

/* Schedule detail row */
.schedule-details {
  padding: 0.95rem;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.schedule-row {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.85rem;
  color: var(--text-soft);
}

.meeting-link-row {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meeting-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 700;
  word-break: break-all;
}

.meeting-link:hover {
  text-decoration: underline;
}

.no-schedule {
  background: rgba(148, 163, 184, 0.08);
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
  justify-content: center;
}

.score-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(14, 116, 144, 0.06);
  padding-top: 0.75rem;
  font-size: 0.85rem;
}

.score-label {
  color: var(--text-muted);
  font-weight: 600;
}

.score-number {
  font-weight: 850;
  color: var(--primary-dark);
}

/* Actions footer */
.card-footer {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.55rem;
  margin-top: auto;
}

.btn-footer {
  padding: 0.55rem 0.45rem;
  border-radius: 10px;
  font-size: 0.76rem;
  font-weight: 800;
  cursor: pointer;
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
}

.btn-schedule {
  background: rgba(14, 165, 233, 0.1);
  color: #0284C7;
  border-color: rgba(14, 165, 233, 0.2);
}
.btn-schedule:hover {
  background: #0284C7;
  color: white;
}

.btn-ai-q {
  background: rgba(139, 92, 246, 0.1);
  color: #7C3AED;
  border-color: rgba(139, 92, 246, 0.2);
}
.btn-ai-q:hover {
  background: #7C3AED;
  color: white;
}

.btn-hire {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border-color: rgba(16, 185, 129, 0.2);
}
.btn-hire:hover {
  background: #059669;
  color: white;
}

.btn-reject {
  background: rgba(239, 68, 68, 0.1);
  color: #DC2626;
  border-color: rgba(239, 68, 68, 0.2);
}
.btn-reject:hover {
  background: #DC2626;
  color: white;
}

/* Modals layout */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  width: 90%;
  max-width: 500px;
  position: relative;
  padding: 2rem;
  border-radius: var(--radius-lg);
  animation: slideUp 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.form-modal, .questions-modal {
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-strong);
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
}

.close-btn:hover {
  color: #EF4444;
}

.modal-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
  font-weight: 850;
  color: var(--primary-dark);
}

.modal-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.form-group label {
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--text-soft);
  text-transform: uppercase;
}

.modal-footer-btns {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.btn-cancel {
  padding: 0.6rem 1.2rem;
  border-radius: 12px;
  font-size: 0.88rem;
  font-weight: 700;
  background: rgba(148, 163, 184, 0.12);
  color: var(--text-soft);
  border: 1px solid rgba(148, 163, 184, 0.22);
  cursor: pointer;
}

.btn-cancel:hover { background: rgba(148, 163, 184, 0.22); }

.btn-primary {
  padding: 0.6rem 1.2rem;
  border-radius: 12px;
  font-size: 0.88rem;
  font-weight: 700;
  background: var(--primary);
  color: white;
  border: 1px solid transparent;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(2, 132, 199, 0.2);
}
.btn-primary:hover {
  background: var(--primary-dark);
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
}

/* AI Questions list design */
.loading-questions-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 1rem;
  color: var(--text-muted);
  font-weight: 600;
}

.spinner {
  width: 38px;
  height: 38px;
  border: 4px solid rgba(2, 132, 199, 0.15);
  border-left-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s infinite linear;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.questions-list-container {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 1.5rem;
  padding-right: 0.5rem;
}

.questions-list {
  padding-left: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.question-item {
  background: rgba(255, 255, 255, 0.6);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid rgba(14, 165, 233, 0.12);
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
}

.q-number {
  background: var(--primary-soft);
  color: var(--primary-dark);
  font-weight: 850;
  font-size: 0.72rem;
  padding: 0.2rem 0.45rem;
  border-radius: 6px;
  flex-shrink: 0;
}

.q-text {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--text-soft);
}

/* Decision theme colors */
.decision-modal.hired-theme {
  border: 1.5px solid rgba(16, 185, 129, 0.35);
  box-shadow: 0 24px 60px rgba(16, 185, 129, 0.15), var(--shadow-strong);
}

.decision-modal.rejected-theme {
  border: 1.5px solid rgba(239, 68, 68, 0.35);
  box-shadow: 0 24px 60px rgba(239, 68, 68, 0.15), var(--shadow-strong);
}

.modal-body-confirm {
  font-size: 0.98rem;
  line-height: 1.6;
  color: var(--text-soft);
  margin-bottom: 1.8rem;
}

.warning-subtext {
  color: var(--text-muted);
  font-size: 0.88rem;
  margin-top: 0.5rem;
}

.btn-decision {
  padding: 0.65rem 1.25rem;
  border-radius: 12px;
  font-size: 0.88rem;
  font-weight: 700;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm-hired {
  background: #10B981;
  color: white;
}
.btn-confirm-hired:hover {
  background: #059669;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.btn-confirm-reject {
  background: #DC2626;
  color: white;
}
.btn-confirm-reject:hover {
  background: #B91C1C;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25);
}

/* Skeleton loader layout */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.6rem;
}

.skeleton-card {
  padding: 1.8rem;
  border-radius: var(--radius-lg);
  height: 250px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
  overflow: hidden;
}

.skeleton-title {
  width: 60%;
  height: 20px;
  border-radius: 4px;
  background: rgba(148, 163, 184, 0.15);
}

.skeleton-body-line {
  width: 90%;
  height: 14px;
  border-radius: 3px;
  background: rgba(148, 163, 184, 0.12);
}

.skeleton-body-line.short {
  width: 50%;
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
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  100% { transform: translateX(100%); }
}

/* Empty State layout */
.empty-state-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 2rem;
  text-align: center;
  gap: 1rem;
}

.empty-icon {
  font-size: 3.8rem;
  filter: drop-shadow(0 10px 20px rgba(99, 102, 241, 0.15));
}

.empty-text {
  font-size: 1.35rem;
  font-weight: 850;
  color: var(--text-soft);
  margin: 0;
}

.empty-subtext {
  font-size: 0.95rem;
  color: var(--text-muted);
  max-width: 480px;
  line-height: 1.6;
  margin: 0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(15px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .controls-panel {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-group {
    justify-content: space-between;
  }
  .select-input {
    flex-grow: 1;
  }
  .view-container {
    padding: 1.5rem 1.2rem;
  }
}
</style>
