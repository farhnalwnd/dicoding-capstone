<template>
  <div class="glass-panel view-container">
    <h2>HR Clustering Dashboard</h2>
    <p class="subtitle">Automatically group your candidates into talent clusters.</p>
    
    <div class="form-group">
      <label>Upload Candidates (PDF/DOCX):</label>
      <input type="file" multiple @change="handleMultipleFileSelect" class="input-field file-input" />
    </div>
    
    <button @click="clusterCandidates" :disabled="loading" class="btn-primary">
      {{ loading ? 'Clustering...' : 'Cluster Candidates' }}
    </button>
    
    <div v-if="clusters.length" class="results detailed-results">
      <div class="skills-grid" style="grid-template-columns: 1fr;">
        <div v-for="cluster in clusters" :key="cluster.cluster_id" class="skills-card">
          <h4>{{ cluster.suggested_label }}</h4>
          <ul>
            <li v-for="name in cluster.candidates" :key="name">{{ name }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const selectedFiles = ref([])
const loading = ref(false)
const clusters = ref([])

const handleMultipleFileSelect = (e) => { selectedFiles.value = Array.from(e.target.files) }

import { API_BASE_URL } from '../config/api'

const clusterCandidates = async () => {
  if (!selectedFiles.value.length) {
    alert("Please upload CVs first")
    return
  }
  loading.value = true
  const fd = new FormData()
  for (let f of selectedFiles.value) fd.append('cvs', f)
  try {
    const res = await axios.post(`${API_BASE_URL}/api/hr/cluster`, fd)
    clusters.value = res.data
  } catch (error) {
    console.error(error)
    alert("Failed to cluster")
  }
  loading.value = false
}
</script>
