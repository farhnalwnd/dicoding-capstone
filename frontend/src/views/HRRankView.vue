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
    
    <button @click="rankCVs" :disabled="loading || !selectedFiles.length || !jobDescription" class="btn-primary">
      {{ loading ? 'Ranking Candidates...' : 'Rank Candidates' }}
    </button>
    
    <div v-if="rankings.length" class="results">
      <h3>Candidate Rankings</h3>
      <div class="table-container">
        <table class="ranking-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Candidate Name</th>
              <th>Match Score</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rankings" :key="r.name" :class="getScoreClass(r.score)">
              <td class="rank-col">
                <span class="rank-badge" :class="getScoreClass(r.score)">#{{ r.rank }}</span>
              </td>
              <td class="name-col">{{ r.name }}</td>
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const selectedFiles = ref([])
const jobDescription = ref('')
const loading = ref(false)
const rankings = ref([])

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
  if (score >= 80) return 'score-high'
  if (score >= 40) return 'score-medium'
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
  try {
    const res = await axios.post('http://localhost:8000/api/hr/rank', fd)
    rankings.value = res.data
  } catch (error) {
    console.error(error)
    alert("Failed to rank candidates")
  }
  loading.value = false
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
</style>
