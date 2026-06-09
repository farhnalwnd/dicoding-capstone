<template>
  <div class="glass-panel view-container">
    <h2>Scrape LinkedIn Jobs</h2>
    <p class="subtitle">Scrape the latest job postings directly to the database.</p>

    <!-- Controls -->
    <div class="controls">
      <div class="form-group">
        <label>Keyword:</label>
        <input type="text" v-model="keyword" placeholder="e.g., Python Developer" class="input-field" />
      </div>

      <div class="form-group">
        <label>Location:</label>
        <input type="text" v-model="location" placeholder="e.g., Jakarta" class="input-field" />
      </div>

      <div class="form-group">
        <label>Time Range:</label>
        <select v-model="timeRange" class="input-field">
          <option value="1w">Past 1 Week</option>
          <option value="1m">Past 1 Month</option>
          <option value="2m">Past 2 Months</option>
          <option value="3m">Past 3 Months</option>
        </select>
      </div>
    </div>

    <div class="actions">
      <button @click="scrapeJobs" :disabled="loading || !keyword || !location" class="btn-primary">
        {{ loading ? 'Scraping...' : 'Scrape Jobs' }}
      </button>
      <button @click="clearDatabase" :disabled="loading" class="btn-danger">
        Clear Database
      </button>
    </div>

    <!-- Data Table -->
    <div class="results">
      <h3>Database Jobs ({{ totalItems }})</h3>
      <EasyDataTable
        :headers="headers"
        :items="items"
        :loading="loading"
        :rows-per-page="10"
        alternating
        border-cell
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const keyword = ref('')
const location = ref('')
const timeRange = ref('1w')
const loading = ref(false)
const items = ref([])
const totalItems = ref(0)

const headers = [
  { text: "Title", value: "title", sortable: true },
  { text: "Company", value: "company", sortable: true },
  { text: "Location", value: "location", sortable: true },
  { text: "Keyword", value: "keyword_searched" },
  { text: "Link", value: "url", sortable: false }
]

import { API_BASE_URL } from '../config/api'

const fetchJobs = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${API_BASE_URL}/api/jobs`)
    items.value = res.data.items
    totalItems.value = res.data.total
  } catch (error) {
    console.error("Failed to fetch jobs", error)
  } finally {
    loading.value = false
  }
}

const scrapeJobs = async () => {
  if (!keyword.value || !location.value) return
  loading.value = true
  try {
    const fd = new FormData()
    fd.append('keyword', keyword.value)
    fd.append('location', location.value)
    fd.append('time_range', timeRange.value)
    await axios.post(`${API_BASE_URL}/api/scrape-recommend`, fd)
    await fetchJobs()
  } catch (error) {
    console.error("Failed to scrape", error)
    alert("Failed to scrape jobs")
  } finally {
    loading.value = false
  }
}

const clearDatabase = async () => {
  if (!confirm("Are you sure you want to clear all jobs from the database?")) return
  loading.value = true
  try {
    await axios.delete(`${API_BASE_URL}/api/jobs/clear`)
    await fetchJobs()
  } catch (error) {
    console.error("Failed to clear database", error)
    alert("Failed to clear database")
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.btn-danger {
  background: linear-gradient(135deg, #DC2626 0%, #EF4444 52%, #F97316 100%);
  color: white;
  min-height: 48px;
  padding: 0.88rem 1.35rem;
  border: none;
  border-radius: 999px;
  font-size: 0.98rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 16px 34px rgba(239, 68, 68, 0.24);
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease, filter 0.2s ease;
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-2px);
  filter: saturate(1.08);
}

.btn-danger:disabled {
  cursor: not-allowed;
  opacity: 0.56;
  box-shadow: none;
}

@media (max-width: 520px) {
  .actions {
    flex-direction: column;
  }
}

/* Override vue3-easy-data-table styles to match theme */
:deep(.easy-data-table__header) {
  background-color: rgba(3, 105, 161, 0.1);
  color: #0C4A6E;
}

:deep(.easy-data-table__rows-hover) {
  background-color: rgba(255, 255, 255, 0.5);
}

:deep(.easy-data-table__rows-hover:hover) {
  background-color: rgba(255, 255, 255, 0.8);
}
</style>