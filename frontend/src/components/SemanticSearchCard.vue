<template>
  <div class="glass-panel search-card">
    <div class="search-header">
      <div class="search-icon-wrapper">
        <span class="search-icon">🔍</span>
      </div>
      <div>
        <h3 class="search-title">Semantic Talent Search</h3>
        <p class="search-subtitle">Find the most relevant talent by typing job roles, skills, or requirements.</p>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="search-form">
      <div class="form-group">
        <label for="search-query">Search Position or Skills</label>
        <div class="input-wrapper">
          <input
            id="search-query"
            type="text"
            v-model="query"
            placeholder="e.g., Machine Learning Engineer or Python Backend Developer"
            class="input-field query-input"
            :disabled="loading"
            @input="clearError"
          />
        </div>
        <span v-if="queryError" class="inline-error">{{ queryError }}</span>
      </div>
      <button type="submit" :disabled="loading" class="btn-primary search-btn">
        <span v-if="loading" class="btn-spinner"></span>
        {{ loading ? 'Searching Candidates...' : 'Search Candidates' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['search'])
const query = ref('')
const queryError = ref('')

const clearError = () => {
  if (query.value.trim()) {
    queryError.value = ''
  }
}

const handleSubmit = () => {
  if (!query.value || !query.value.trim()) {
    queryError.value = 'Please enter a search query.'
    return
  }
  queryError.value = ''
  emit('search', query.value.trim())
}
</script>

<style scoped>
.search-card {
  padding: 2.2rem;
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-soft);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  margin-bottom: 2rem;
}

.search-card:hover {
  box-shadow: var(--shadow-strong);
  border-color: rgba(255, 255, 255, 0.9);
}

.search-header {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  margin-bottom: 1.8rem;
  border-bottom: 1px solid rgba(14, 116, 144, 0.08);
  padding-bottom: 1.2rem;
}

.search-icon-wrapper {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: rgba(14, 165, 233, 0.1);
  border: 1px solid rgba(14, 165, 233, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.03);
}

.search-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 850;
  color: var(--text);
}

.search-subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.88rem;
  color: var(--text-muted);
  font-weight: 500;
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.query-input {
  padding-left: 1.2rem;
  font-size: 1.02rem;
}

.search-btn {
  align-self: flex-start;
  min-width: 180px;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-left-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
  margin-right: 0.5rem;
}

.inline-error {
  color: #EF4444;
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 0.35rem;
  display: block;
  text-align: left;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .search-btn {
    width: 100%;
  }
}
</style>
