<template>
  <div class="glass-panel view-container">
    <h2>Detailed CV-JD Analysis</h2>
    <p class="subtitle">See exactly which skills you match and which you are missing.</p>
    
    <div class="form-group">
      <label>Upload CV (PDF/DOCX):</label>
      <input type="file" @change="handleFileSelect" class="input-field file-input" />
    </div>
    
    <div class="form-group">
      <label>Job Description:</label>
      <textarea v-model="jobDescription" placeholder="Paste the job requirements here..." class="input-field textarea" rows="6"></textarea>
    </div>

    <div class="form-group">
      <label>Domain:</label>
      <select v-model="domain" class="input-field">
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
    
    <button @click="matchDetailed" :disabled="loading || !selectedFile || !jobDescription" class="btn-primary">
      {{ loading ? 'Analyzing...' : 'Analyze Match' }}
    </button>
    
    <div v-if="detailedResult" class="results detailed-results">
      <div class="score-card">
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const selectedFile = ref(null)
const jobDescription = ref('')
const domain = ref('general')
const loading = ref(false)
const detailedResult = ref(null)

const handleFileSelect = (e) => { selectedFile.value = e.target.files[0] }

const matchDetailed = async () => {
  if (!selectedFile.value || !jobDescription.value) {
    alert("Please upload CV and provide Job Description")
    return
  }
  loading.value = true
  const fd = new FormData()
  fd.append('cv', selectedFile.value)
  fd.append('job_description', jobDescription.value)
  fd.append('domain', domain.value)
  try {
    const res = await axios.post(`${API_BASE_URL}/api/match-detailed`, fd)
    detailedResult.value = res.data
  } catch (error) {
    console.error(error)
    alert("Failed to analyze")
  }
  loading.value = false
}
</script>

<style scoped>
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
</style>
