<template>
  <div class="glass-panel view-container">
    <h2>Semantic Job Search</h2>
    <p class="subtitle">Upload your CV to search for matching jobs in the database semantically.</p>
    
    <div class="form-group">
      <label>Upload CV (PDF/DOCX):</label>
      <input type="file" @change="handleFileSelect" class="input-field file-input" />
    </div>
    
    <button @click="searchJobs" :disabled="loading || !selectedFile" class="btn-primary">
      {{ loading ? 'Searching Matching Jobs...' : 'Search Jobs' }}
    </button>
    
    <div v-if="results.length" class="results">
      <h3>Top Matches Based on your CV</h3>
      <div class="job-grid">
        <JobCard
          v-for="(job, index) in results"
          :key="job.url"
          :rank="index + 1"
          :title="job.title"
          :company="job.company"
          :location="job.location"
          :score="job.score"
          :url="job.url"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import JobCard from '../components/JobCard.vue'

const selectedFile = ref(null)
const loading = ref(false)
const results = ref([])

const handleFileSelect = (e) => { selectedFile.value = e.target.files[0] }

const searchJobs = async () => {
  if (!selectedFile.value) {
    alert("Please select a CV first")
    return
  }
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('cv', selectedFile.value)
    const res = await axios.post('http://localhost:8000/api/jobs/semantic-search', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    results.value = res.data
  } catch (error) {
    console.error(error)
    alert("Failed to search jobs")
  }
  loading.value = false
}
</script>

<style scoped>
.job-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-top: 1.5rem;
}

@media (min-width: 768px) {
  .job-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
