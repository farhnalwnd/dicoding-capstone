<template>
  <div class="glass-panel view-container">
    <!-- API Error Banner -->
    <FloatingErrorBanner
      v-if="apiError"
      v-model="showErrorBanner"
      :message="apiError.message"
      :retry-function="fetchTalentPool"
    />

    <h2 class="view-title">👥 Talent Pool Management</h2>
    <p class="subtitle">Store, filter, and track promising candidate profiles for future recruitment needs.</p>

    <!-- Filters & Actions Header -->
    <div class="controls-panel sub-glass-card">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search by candidate name..." 
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
        <label for="sort-order">Sort:</label>
        <select id="sort-order" v-model="sortOrder" class="input-field select-input">
          <option value="score_desc">Match Score (High to Low)</option>
          <option value="score_asc">Match Score (Low to High)</option>
          <option value="newest">Newest Added</option>
        </select>
      </div>
    </div>

    <!-- Error State -->
    <ErrorState
      v-if="fatalError"
      :type="fatalError.type"
      :message="fatalError.message"
      :retry-function="fetchTalentPool"
    />

    <!-- Loading State (Skeleton Loading) -->
    <div v-else-if="loading" class="skeleton-grid">
      <div v-for="n in 3" :key="n" class="skeleton-card glass-panel loading-shimmer">
        <div class="skeleton-header">
          <div class="skeleton-left">
            <div class="skeleton-rank"></div>
            <div class="skeleton-name"></div>
          </div>
          <div class="skeleton-badge"></div>
        </div>
        <div class="skeleton-meta">
          <div class="skeleton-meta-line"></div>
          <div class="skeleton-meta-line"></div>
        </div>
        <div class="skeleton-bar-container">
          <div class="skeleton-bar-header"></div>
          <div class="skeleton-bar"></div>
        </div>
        <div class="skeleton-actions">
          <div class="skeleton-btn"></div>
          <div class="skeleton-btn"></div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredCandidates.length === 0" class="empty-state-panel glass-panel">
      <div class="empty-icon">📁</div>
      <p class="empty-text">No candidates found in the Talent Pool.</p>
      <p class="empty-subtext">
        {{ searchQuery || selectedPosition ? 'Try adjusting your search query or filters.' : 'Promising candidates moved from the Bulk CV Ranking dashboard will appear here.' }}
      </p>
    </div>

    <!-- Candidates List -->
    <div v-else class="candidates-list-wrapper">
      <div class="candidates-grid">
        <CandidateCard
          v-for="(candidate, index) in filteredCandidates"
          :key="candidate.id"
          :name="candidate.candidate_name"
          :score="candidate.match_score"
          :rank="sortOrder === 'score_desc' ? index + 1 : candidates.findIndex(c => c.id === candidate.id) + 1"
          :job-position="candidate.job_title"
          :date-added="candidate.created_at"
          :status="candidate.status"
          :show-actions="true"
          @move-to-interview="confirmMoveToInterview(candidate)"
          @remove="confirmRejectCandidate(candidate)"
        />
      </div>
    </div>

    <!-- Rejection/Removal Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="closeConfirmModal">
      <div class="modal-content glass-panel confirm-modal">
        <button class="close-btn" @click="closeConfirmModal">&times;</button>
        <h3 class="modal-title text-danger">⚠️ Confirm Candidate Removal</h3>
        <div class="modal-body-confirm">
          <p>Are you sure you want to remove <strong>{{ selectedCandidate?.candidate_name }}</strong> from the Talent Pool?</p>
          <p class="warning-subtext">This will update their status to <strong>rejected</strong>.</p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeConfirmModal" :disabled="actionLoading">Cancel</button>
          <button class="btn-confirm-reject" @click="rejectCandidate" :disabled="actionLoading">
            {{ actionLoading ? 'Removing...' : 'Yes, Remove Candidate' }}
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
import CandidateCard from '../components/CandidateCard.vue'
import ErrorState from '../components/ErrorState.vue'
import FloatingErrorBanner from '../components/FloatingErrorBanner.vue'

const toast = inject('toast')

const candidates = ref([])
const loading = ref(true)
const actionLoading = ref(false)
const searchQuery = ref('')
const selectedPosition = ref('')
const sortOrder = ref('score_desc')

// Error handlers
const apiError = ref(null)
const fatalError = ref(null)
const showErrorBanner = ref(false)

// Modal state
const showConfirmModal = ref(false)
const selectedCandidate = ref(null)

const fetchTalentPool = async () => {
  loading.value = true
  apiError.value = null
  fatalError.value = null
  showErrorBanner.value = false
  
  try {
    const res = await axios.get(`${API_BASE_URL}/api/talent-pool`)
    candidates.value = res.data || []
  } catch (error) {
    console.error(error)
    const isOffline = !navigator.onLine
    let errMsg = error.response?.data?.detail || 'Failed to fetch Talent Pool candidates.'
    
    if (isOffline) {
      errMsg = 'Connection lost. Please check your internet connection.'
      fatalError.value = { type: 'network', message: errMsg }
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
  fetchTalentPool()
})

// Unique list of job positions for filtering
const uniquePositions = computed(() => {
  const positions = candidates.value.map(c => c.job_title).filter(Boolean)
  return [...new Set(positions)]
})

// Search, Filter, and Sort candidates
const filteredCandidates = computed(() => {
  let list = [...candidates.value]

  // Filter by search query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter(c => c.candidate_name.toLowerCase().includes(q))
  }

  // Filter by position
  if (selectedPosition.value) {
    list = list.filter(c => c.job_title === selectedPosition.value)
  }

  // Sort
  if (sortOrder.value === 'score_desc') {
    list.sort((a, b) => {
      if (b.match_score !== a.match_score) {
        return b.match_score - a.match_score
      }
      return new Date(b.created_at) - new Date(a.created_at)
    })
  } else if (sortOrder.value === 'score_asc') {
    list.sort((a, b) => {
      if (a.match_score !== b.match_score) {
        return a.match_score - b.match_score
      }
      return new Date(b.created_at) - new Date(a.created_at)
    })
  } else if (sortOrder.value === 'newest') {
    list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }

  return list
})

// Action: Move to Interview
const confirmMoveToInterview = async (candidate) => {
  try {
    await axios.patch(`${API_BASE_URL}/api/candidates/${candidate.id}/status`, {
      status: 'interview'
    })
    toast.success(`${candidate.candidate_name} moved to Interview successfully.`)
    // Remove from local list since this page only lists talent_pool candidates
    candidates.value = candidates.value.filter(c => c.id !== candidate.id)
  } catch (error) {
    console.error(error)
    toast.error(error.response?.data?.detail || 'Failed to update candidate status.')
  }
}

// Action: Remove / Reject
const confirmRejectCandidate = (candidate) => {
  selectedCandidate.value = candidate
  showConfirmModal.value = true
}

const closeConfirmModal = () => {
  showConfirmModal.value = false
  selectedCandidate.value = null
}

const rejectCandidate = async () => {
  if (!selectedCandidate.value) return
  actionLoading.value = true
  
  try {
    const candidate = selectedCandidate.value
    await axios.patch(`${API_BASE_URL}/api/candidates/${candidate.id}/status`, {
      status: 'rejected'
    })
    toast.success(`${candidate.candidate_name} removed from Talent Pool.`)
    candidates.value = candidates.value.filter(c => c.id !== candidate.id)
    closeConfirmModal()
  } catch (error) {
    console.error(error)
    toast.error(error.response?.data?.detail || 'Failed to update candidate status.')
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

/* Candidates layout */
.candidates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.6rem;
}

/* Skeleton Loading Styling */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.6rem;
}

.skeleton-card {
  padding: 1.8rem;
  border-radius: var(--radius-lg);
  height: 290px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  position: relative;
  overflow: hidden;
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skeleton-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-grow: 1;
}

.skeleton-rank {
  width: 38px;
  height: 28px;
  border-radius: 8px;
  background: rgba(148, 163, 184, 0.15);
}

.skeleton-name {
  width: 50%;
  height: 20px;
  border-radius: 6px;
  background: rgba(148, 163, 184, 0.15);
}

.skeleton-badge {
  width: 65px;
  height: 48px;
  border-radius: 16px;
  background: rgba(148, 163, 184, 0.15);
}

.skeleton-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.6rem 0;
  border-top: 1px solid rgba(14, 116, 144, 0.05);
  border-bottom: 1px solid rgba(14, 116, 144, 0.05);
}

.skeleton-meta-line {
  width: 70%;
  height: 14px;
  border-radius: 4px;
  background: rgba(148, 163, 184, 0.12);
}

.skeleton-bar-container {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.skeleton-bar-header {
  width: 40%;
  height: 12px;
  border-radius: 3px;
  background: rgba(148, 163, 184, 0.12);
}

.skeleton-bar {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.12);
}

.skeleton-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: auto;
}

.skeleton-btn {
  flex: 1;
  height: 36px;
  border-radius: 12px;
  background: rgba(148, 163, 184, 0.15);
}

.loading-shimmer::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  transform: translateX(-100%);
  background-image: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.35) 20%,
    rgba(255, 255, 255, 0.5) 60%,
    rgba(255, 255, 255, 0) 100%
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

/* Empty State Styling */
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
  filter: drop-shadow(0 10px 20px rgba(14, 165, 233, 0.15));
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

/* Modal overlay & Confirm Modal styles */
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
  max-width: 480px;
  position: relative;
  padding: 2.2rem;
  border-radius: var(--radius-lg);
  animation: slideUp 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.confirm-modal {
  border: 1.5px solid rgba(239, 68, 68, 0.35);
  box-shadow: 0 24px 60px rgba(239, 68, 68, 0.15), var(--shadow-soft);
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
  margin: 0 0 1.25rem 0;
  font-size: 1.25rem;
  font-weight: 850;
}

.text-danger {
  color: #DC2626;
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.85rem;
}

.btn-cancel {
  padding: 0.65rem 1.25rem;
  border-radius: 12px;
  font-size: 0.88rem;
  font-weight: 700;
  background: rgba(148, 163, 184, 0.12);
  color: var(--text-soft);
  border: 1px solid rgba(148, 163, 184, 0.22);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: rgba(148, 163, 184, 0.22);
}

.btn-confirm-reject {
  padding: 0.65rem 1.25rem;
  border-radius: 12px;
  font-size: 0.88rem;
  font-weight: 700;
  background: #DC2626;
  color: white;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm-reject:hover {
  background: #B91C1C;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25);
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
