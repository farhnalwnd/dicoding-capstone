<template>
  <div class="glass-panel view-container">
    <h2>Bulk CV Ranking</h2>
    <p class="subtitle">Upload multiple CVs to rank candidates against a job description.</p>
    
    <div class="form-group">
      <label>Upload Candidates (PDF/DOCX):</label>
      <input type="file" multiple @change="handleMultipleFileSelect" class="input-field file-input" />
      
      <!-- Select2 style tag-like display for selected files -->
      <div v-if="selectedFiles.length" class="file-tags-container">
        <div v-for="(file, index) in selectedFiles" :key="file.name" class="file-tag">
          <span class="file-name">{{ file.name }}</span>
          <button type="button" @click="removeFile(index)" class="remove-tag-btn">&times;</button>
        </div>
      </div>
    </div>
    
    <div class="form-group">
      <label>Job Description:</label>
      <textarea v-model="jobDescription" placeholder="Paste the job requirements here..." class="input-field textarea" rows="6"></textarea>
    </div>

    <div class="form-group">
      <label>Domain:</label>
      <select v-model="domain" class="input-field">
        <option v-for="option in domainOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      <small class="helper-text">
        Pilih domain agar sistem memakai skill list yang sesuai saat menghitung ranking kandidat.
      </small>
    </div>

    <button @click="rankCVs" :disabled="loading || !selectedFiles.length || !jobDescription" class="btn-primary">
      {{ loading ? 'Ranking Candidates...' : 'Rank Candidates' }}
    </button>
    
    <div v-if="rankings.length" class="results">
      <div class="results-header">
        <h3>Candidate Rankings</h3>
        <span class="domain-badge">Domain: {{ selectedDomainLabel }}</span>
      </div>
      <div class="table-container">
        <table class="ranking-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Candidate Name</th>
              <th>Semantic</th>
              <th>Domain Skills</th>
              <th>Final Score</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rankings" :key="r.filename || r.name" :class="[getScoreClass(r.score), 'clickable-row']" @click="openModal(r)">
              <td class="rank-col">
                <span class="rank-badge" :class="getScoreClass(r.score)">#{{ r.rank }}</span>
              </td>
              <td class="name-col">
                <div>{{ r.name }}</div>
                <small v-if="r.filename" class="filename-text">{{ r.filename }}</small>
              </td>
              <td class="metric-col">{{ r.semantic_score ?? '-' }}%</td>
              <td class="metric-col">
                <span>{{ r.domain_skill_score ?? '-' }}%</span>
                <small v-if="r.matched_skills_count !== undefined" class="skill-count-text">
                  {{ r.matched_skills_count }} match / {{ r.missing_skills_count }} miss
                </small>
              </td>
              <td class="score-col">
                <div class="score-bar-container">
                  <div class="score-bar" :class="getScoreClass(r.score)" :style="{ width: r.score + '%' }"></div>
                  <span class="score-text" :class="getScoreClass(r.score)">{{ r.score }}%</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="selectedCandidate" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content glass-panel">
        <button class="close-btn" @click="closeModal">&times;</button>
        <h3 class="modal-title">{{ selectedCandidate.name }}'s Details</h3>
        
        <div class="modal-body">
          <div class="chart-container" v-if="chartData">
            <h4>Domain Skills Analysis</h4>
            <div class="radar-wrapper">
              <Radar :data="chartData" :options="chartOptions" />
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
import { computed, ref } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

const selectedFiles = ref([])
const jobDescription = ref('')
const domain = ref('general')
const loading = ref(false)
const rankings = ref([])

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

const selectedDomainLabel = computed(() => {
  return domainOptions.find(option => option.value === domain.value)?.label || 'General'
})

const handleMultipleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  // Merge unique files
  for (let f of files) {
    if (!selectedFiles.value.some(existing => existing.name === f.name)) {
      selectedFiles.value.push(f)
    }
  }
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const getScoreClass = (score) => {
  if (score >= 55) return 'score-high'
  if (score >= 30) return 'score-medium'
  return 'score-low'
}

const rankCVs = async () => {
  if (!selectedFiles.value.length || !jobDescription.value) {
    alert("Please upload at least one CV and provide Job Description")
    return
  }
  loading.value = true
  const fd = new FormData()
  for (let f of selectedFiles.value) {
    fd.append('cvs', f)
  }
  fd.append('job_description', jobDescription.value)
  fd.append('domain', domain.value)
  try {
    const res = await axios.post(`${API_BASE_URL}/api/hr/rank`, fd)
    rankings.value = res.data
  } catch (error) {
    console.error(error)
    alert("Failed to rank candidates")
  }
  loading.value = false
}

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
  
  if (candidate.skill_scores && Object.keys(candidate.skill_scores).length > 0) {
    // Ambil top 8 skills untuk ditampilkan agar tidak terlalu padat
    const sortedSkills = Object.entries(candidate.skill_scores)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      
    chartData.value = {
      labels: sortedSkills.map(s => s[0]),
      datasets: [
        {
          label: 'Proficiency (%)',
          backgroundColor: 'rgba(14, 165, 233, 0.2)',
          borderColor: 'rgba(14, 165, 233, 1)',
          pointBackgroundColor: 'rgba(14, 165, 233, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(14, 165, 233, 1)',
          data: sortedSkills.map(s => s[1])
        }
      ]
    }
  } else {
    chartData.value = null
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
  } catch (error) {
    console.error(error)
    alert("Failed to generate questions")
  }
  loadingQuestions.value = false
}

</script>

<style scoped>
.file-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(3, 105, 161, 0.2);
  border-radius: 8px;
  min-height: 42px;
}

.file-tag {
  display: inline-flex;
  align-items: center;
  background: var(--primary);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
}

.file-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-tag-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.1rem;
  margin-left: 0.5rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  height: 100%;
}

.remove-tag-btn:hover {
  color: #EF4444;
}

/* Beautiful Ranking Table Styles */
.table-container {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(3, 105, 161, 0.2);
  overflow: hidden;
  margin-top: 1.5rem;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.ranking-table th {
  background: rgba(3, 105, 161, 0.1);
  color: #0369A1;
  padding: 1rem;
  font-weight: 700;
  font-size: 0.95rem;
  border-bottom: 2px solid rgba(3, 105, 161, 0.15);
}

.ranking-table td {
  padding: 1.2rem 1rem;
  border-bottom: 1px solid rgba(3, 105, 161, 0.1);
  transition: all 0.2s ease;
  vertical-align: middle;
}

.ranking-table tbody tr {
  transition: all 0.3s ease;
}

.ranking-table tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.8);
  transform: scale(1.01);
  box-shadow: 0 4px 12px rgba(3, 105, 161, 0.08);
}

.rank-col {
  width: 80px;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.85rem;
}

.rank-badge.score-high {
  background-color: rgba(34, 197, 94, 0.15);
  color: #16A34A;
  border: 1.5px solid #22C55E;
}

.rank-badge.score-medium {
  background-color: rgba(234, 179, 8, 0.15);
  color: #CA8A04;
  border: 1.5px solid #EAB308;
}

.rank-badge.score-low {
  background-color: rgba(239, 68, 68, 0.15);
  color: #DC2626;
  border: 1.5px solid #EF4444;
}

.name-col {
  font-weight: 600;
  color: #0C4A6E;
  font-size: 1rem;
}

.score-col {
  min-width: 250px;
}

.score-bar-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(3, 105, 161, 0.05);
  border-radius: 9999px;
  padding: 0.25rem 0.5rem 0.25rem 0.25rem;
  border: 1px solid rgba(3, 105, 161, 0.1);
}

.score-bar {
  height: 12px;
  border-radius: 9999px;
  transition: width 1s ease-in-out;
}

.score-bar.score-high {
  background: linear-gradient(90deg, #4ADE80 0%, #22C55E 100%);
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
}

.score-bar.score-medium {
  background: linear-gradient(90deg, #FDE047 0%, #EAB308 100%);
  box-shadow: 0 0 8px rgba(234, 179, 8, 0.4);
}

.score-bar.score-low {
  background: linear-gradient(90deg, #F87171 0%, #EF4444 100%);
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
}

.score-text {
  font-weight: 700;
  font-size: 0.9rem;
  min-width: 45px;
}

.score-text.score-high {
  color: #16A34A;
}

.score-text.score-medium {
  color: #CA8A04;
}

.score-text.score-low {
  color: #DC2626;
}

.helper-text {
  display: block;
  margin-top: 0.35rem;
  color: #64748B;
  font-size: 0.85rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.domain-badge {
  background: rgba(3, 105, 161, 0.1);
  color: #0369A1;
  border: 1px solid rgba(3, 105, 161, 0.2);
  border-radius: 9999px;
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
  font-weight: 700;
}

.filename-text,
.skill-count-text {
  display: block;
  margin-top: 0.25rem;
  color: #64748B;
  font-size: 0.6rem;
  font-weight: 500;
}

.metric-col {
  color: #0C4A6E;
  font-weight: 700;
  min-width: 120px;
}

@media (max-width: 768px) {
  .table-container {
    overflow-x: auto;
  }

  .ranking-table {
    min-width: 760px;
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
</style>
