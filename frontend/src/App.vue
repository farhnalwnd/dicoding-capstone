<template>
  <div class="container">
    <h1>CV Summarizer & Job Matcher</h1>

    <div class="upload-section">
      <label class="upload-label">
        Upload CV (PDF/DOCX)
        <input type="file" accept=".pdf,.docx,.doc" @change="handleFileSelect" />
      </label>
      <div v-if="selectedFile" class="file-name">{{ selectedFile.name }}</div>
    </div>

    <div class="job-section">
      <textarea
        v-model="jobDescription"
        placeholder="Paste Job Description here..."
        rows="8"
      ></textarea>
    </div>

    <button @click="submit" :disabled="loading || !selectedFile || !jobDescription">
      {{ loading ? 'Processing...' : 'Analyze Match' }}
    </button>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="result" class="result">
      <div class="score">
        <h2>Match Score: {{ result.similarity_score }}%</h2>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: result.similarity_score + '%' }"></div>
        </div>
      </div>

      <div class="insights">
        <div v-if="result.insights.skills.length" class="insight-group">
          <h3>Skills</h3>
          <ul>
            <li v-for="skill in result.insights.skills" :key="skill">{{ skill }}</li>
          </ul>
        </div>
        <div v-if="result.insights.experience.length" class="insight-group">
          <h3>Experience</h3>
          <ul>
            <li v-for="exp in result.insights.experience" :key="exp">{{ exp }}</li>
          </ul>
        </div>
        <div v-if="result.insights.education.length" class="insight-group">
          <h3>Education</h3>
          <ul>
            <li v-for="edu in result.insights.education" :key="edu">{{ edu }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const selectedFile = ref(null)
const jobDescription = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)

const handleFileSelect = (e) => {
  selectedFile.value = e.target.files[0]
}

const submit = async () => {
  loading.value = true
  error.value = ''
  result.value = null

  const formData = new FormData()
  formData.append('cv', selectedFile.value)
  formData.append('job_description', jobDescription.value)

  try {
    const res = await axios.post('http://localhost:8000/api/match', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = res.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to process. Check backend.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.container { max-width: 700px; margin: 2rem auto; padding: 1rem; font-family: sans-serif; }
.upload-label { display: inline-block; padding: 1rem; border: 2px dashed #ccc; border-radius: 8px; cursor: pointer; text-align: center; width: 100%; box-sizing: border-box; }
.upload-label input { display: none; }
.file-name { margin-top: 0.5rem; color: #555; }
textarea { width: 100%; box-sizing: border-box; padding: 0.75rem; font-size: 1rem; border: 1px solid #ccc; border-radius: 6px; resize: vertical; }
button { margin-top: 1rem; padding: 0.75rem 1.5rem; font-size: 1rem; background: #42b883; color: white; border: none; border-radius: 6px; cursor: pointer; }
button:disabled { background: #ccc; cursor: not-allowed; }
.error { margin-top: 1rem; color: red; }
.result { margin-top: 2rem; }
.progress-bar { width: 100%; height: 24px; background: #eee; border-radius: 12px; overflow: hidden; }
.progress-fill { height: 100%; background: #42b883; transition: width 0.5s ease; }
.insights { display: flex; gap: 2rem; margin-top: 1.5rem; flex-wrap: wrap; }
.insight-group { flex: 1; min-width: 180px; }
.insight-group h3 { margin-bottom: 0.5rem; }
ul { list-style: none; padding: 0; }
li { background: #f0f0f0; padding: 0.3rem 0.6rem; margin-bottom: 0.3rem; border-radius: 4px; font-size: 0.9rem; }
</style>
