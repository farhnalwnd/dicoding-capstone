<template>
  <div class="glass-panel view-container">
    <!-- Section 2 — API Error Banner -->
    <FloatingErrorBanner
      v-if="apiError"
      v-model="showErrorBanner"
      :message="apiError.message"
      :retry-function="clusterCandidates"
    />

    <h2>HR Candidate Clustering Dashboard</h2>
    <p class="subtitle">Segment your candidate pool into distinct talent categories dynamically using AI representation clustering.</p>
    
    <!-- Section 1 — Upload Area (Input Card) -->
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
        <label for="num-clusters">Target Groups (Number of Clusters):</label>
        <select id="num-clusters" v-model="numClusters" class="input-field" :disabled="loading">
          <option :value="2">2 Groups</option>
          <option :value="3">3 Groups (Recommended)</option>
          <option :value="4">4 Groups</option>
          <option :value="5">5 Groups</option>
          <option :value="6">6 Groups</option>
        </select>
        <small class="helper-text">
          Choose how many talent groups you want to cluster candidates into.
        </small>
      </div>

      <button 
        @click="clusterCandidates" 
        :disabled="showLoader || loading" 
        class="btn-primary cluster-btn"
      >
        <span>⚡</span>
        {{ loading ? 'Generating Clusters...' : 'Cluster Candidates' }}
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
      :retry-function="clusterCandidates"
    />

    <!-- Section 8 — Empty State -->
    <div v-else-if="!clusters.length" class="empty-state-panel glass-panel">
      <div class="empty-icon">🧩</div>
      <p class="empty-text">No clustering results generated yet.</p>
      <p class="empty-subtext">Upload candidate CVs to discover talent groups automatically using AI clustering.</p>
    </div>

    <!-- Results Dashboard Layout -->
    <div v-else class="results-dashboard">
      <!-- Section 2 & 6 — Clustering Summary & Highlight Component -->
      <ClusterSummary
        :total-candidates="totalCandidates"
        :total-clusters="totalClusters"
        :largest-cluster-name="largestClusterName"
        :largest-cluster-size="largestClusterSize"
      />

      <!-- Section 5 — Cluster Visualization Charts -->
      <ClusterCharts :clusters="clusters" />

      <!-- Section 9 — Responsive Selection List and Detail View Row -->
      <div class="dashboard-grid">
        <!-- Left Column: Cluster overview card selection lists -->
        <div class="overview-section">
          <h3 class="section-title">Overview Groups</h3>
          <div class="cluster-cards-list">
            <ClusterCard
              v-for="c in clusters"
              :key="c.cluster_id"
              :cluster-id="c.cluster_id"
              :label="c.suggested_label"
              :count="c.candidates.length"
              :is-active="selectedClusterId === c.cluster_id"
              @select="selectCluster"
            />
          </div>
        </div>

        <!-- Right Column: Detail member list of selected cluster -->
        <div class="detail-section" v-if="activeCluster">
          <h3 class="section-title">Group Members</h3>
          <ClusterDetail
            :label="activeCluster.suggested_label"
            :candidates="activeCluster.candidates"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, inject } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import ClusterSummary from '../components/ClusterSummary.vue'
import ClusterCard from '../components/ClusterCard.vue'
import ClusterDetail from '../components/ClusterDetail.vue'
import ClusterCharts from '../components/ClusterCharts.vue'
import AIProcessingLoader from '../components/AIProcessingLoader.vue'
import ErrorState from '../components/ErrorState.vue'
import FloatingErrorBanner from '../components/FloatingErrorBanner.vue'
import { validateFile } from '../utils/validation'

const toast = inject('toast')

const selectedFiles = ref([])
const loading = ref(false)
const showLoader = ref(false)
const progress = ref(0)
const elapsedTime = ref(0)
const message = ref('')
const status = ref('processing')
const errorMessage = ref('')
const numClusters = ref(3)
const clusters = ref([])
const selectedClusterId = ref(0)

// Validation states
const cvsError = ref('')

// Error Handlers
const apiError = ref(null)
const fatalError = ref(null)
const showErrorBanner = ref(false)

let timerInterval = null
let eventSource = null

// Define 4 steps for Talent Clustering
const steps = [
  'Parsing CVs',
  'Generating Embeddings',
  'Clustering Candidates',
  'Building Clusters'
]

// Calculated summary stats
const totalCandidates = computed(() => {
  return clusters.value.reduce((sum, c) => sum + c.candidates.length, 0)
})

const totalClusters = computed(() => clusters.value.length)

// Compute Largest Cluster details
const largestCluster = computed(() => {
  if (!clusters.value.length) return null
  return [...clusters.value].sort((a, b) => b.candidates.length - a.candidates.length)[0]
})

const largestClusterName = computed(() => largestCluster.value ? largestCluster.value.suggested_label : '')
const largestClusterSize = computed(() => largestCluster.value ? largestCluster.value.candidates.length : 0)

// Active Cluster based on click selection
const activeCluster = computed(() => {
  return clusters.value.find(c => c.cluster_id === selectedClusterId.value) || clusters.value[0] || null
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

const selectCluster = (id) => {
  selectedClusterId.value = id
}

const handleLoaderClose = () => {
  showLoader.value = false
  loading.value = false
  if (eventSource) eventSource.close()
  clearInterval(timerInterval)
}

const clusterCandidates = async () => {
  cvsError.value = ''
  if (!selectedFiles.value.length) {
    cvsError.value = "Please upload at least one CV."
    return
  }
  
  loading.value = true
  showLoader.value = true
  progress.value = 0
  elapsedTime.value = 0
  message.value = 'Uploading files and initializing job...'
  status.value = 'processing'
  errorMessage.value = ''
  clusters.value = []
  apiError.value = null
  fatalError.value = null
  showErrorBanner.value = false
  
  const fd = new FormData()
  for (let f of selectedFiles.value) {
    fd.append('cvs', f)
  }
  fd.append('num_clusters', numClusters.value)
  
  try {
    const startRes = await axios.post(`${API_BASE_URL}/api/hr/cluster/start`, fd)
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
              clusters.value = resultRes.data || []
              
              if (!clusters.value.length) {
                apiError.value = { message: 'No candidate clusters were generated.' }
                showErrorBanner.value = true
                toast.warning('No candidate clusters were generated.')
              } else {
                selectedClusterId.value = clusters.value[0].cluster_id
                toast.success("Candidate clustering completed successfully.")
              }
              
              showLoader.value = false
              loading.value = false
            } catch (err) {
              console.error(err)
              status.value = 'error'
              errorMessage.value = err.message || 'Failed to fetch final clusters.'
              apiError.value = err
              showErrorBanner.value = true
              toast.error(errorMessage.value)
            }
          }, 1000)
        } else if (data.status === 'error') {
          clearInterval(timerInterval)
          eventSource.close()
          status.value = 'error'
          errorMessage.value = data.message || 'Candidate clustering failed.'
          
          apiError.value = {
            message: data.message || 'Candidate clustering failed.'
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
    let errMsg = error.message || 'Failed to initialize talent clustering task.'
    
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

// Reset active cluster when target groups length changes
watch(clusters, (newClusters) => {
  if (newClusters.length && !newClusters.some(c => c.cluster_id === selectedClusterId.value)) {
    selectedClusterId.value = newClusters[0].cluster_id
  }
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

.form-group-container {
  padding: 2.2rem;
  border-radius: 28px;
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

.cluster-btn {
  font-size: 1rem;
  min-width: 200px;
}

/* Empty State Dashboard style */
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

/* Results Dashboard and layout properties */
.results-dashboard {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2.2rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.overview-section,
.detail-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 850;
  color: var(--text-soft);
}

.cluster-cards-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.helper-text {
  display: block;
  margin-top: 0.35rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

@media (max-width: 992px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>
