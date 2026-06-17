<template>
  <div class="audit-table-wrap glass-panel">
    <div class="audit-toolbar">
      <input
        id="audit-search-input"
        v-model="searchQuery"
        type="text"
        placeholder="Search logs by action, email, or target..."
        class="input-field audit-search"
        @input="onSearch"
      />
      <span class="audit-count">{{ total }} entries</span>
    </div>

    <div v-if="loading" class="audit-loading">
      <div class="spinner-sm"></div>
      <span>Loading audit logs...</span>
    </div>

    <div v-else-if="!logs.length" class="audit-empty">
      <span>No audit log entries found.</span>
    </div>

    <div v-else class="audit-scroll">
      <table class="audit-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Admin</th>
            <th>Action</th>
            <th>Target</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(log, i) in logs" :key="i" class="audit-row">
            <td class="col-time">{{ formatTime(log.timestamp) }}</td>
            <td class="col-email">{{ log.admin_email }}</td>
            <td>
              <span class="action-badge" :class="actionClass(log.action)">
                {{ log.action }}
              </span>
            </td>
            <td class="col-target">{{ log.target || '—' }}</td>
            <td class="col-details">{{ log.details || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="total > limit" class="audit-pagination">
      <button class="btn-page" :disabled="skip === 0" @click="prevPage">← Prev</button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button class="btn-page" :disabled="skip + limit >= total" @click="nextPage">Next →</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const logs    = ref([])
const total   = ref(0)
const loading = ref(false)
const searchQuery = ref('')
const skip    = ref(0)
const limit   = ref(50)

let debounceTimer = null

const currentPage = computed(() => Math.floor(skip.value / limit.value) + 1)
const totalPages  = computed(() => Math.ceil(total.value / limit.value))

async function fetchLogs() {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const res = await axios.get(`${API_BASE_URL}/api/admin/audit-logs`, {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        keyword: searchQuery.value || undefined,
        skip: skip.value,
        limit: limit.value
      }
    })
    logs.value  = res.data.logs || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error('Failed to fetch audit logs:', e)
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    skip.value = 0
    fetchLogs()
  }, 350)
}

function prevPage() {
  skip.value = Math.max(0, skip.value - limit.value)
  fetchLogs()
}

function nextPage() {
  skip.value = skip.value + limit.value
  fetchLogs()
}

function formatTime(ts) {
  if (!ts) return '—'
  try {
    return new Date(ts).toLocaleString('id-ID', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    })
  } catch { return ts }
}

function actionClass(action) {
  if (!action) return ''
  if (action.includes('delete')) return 'action-red'
  if (action.includes('disable') || action.includes('update')) return 'action-amber'
  if (action.includes('login')) return 'action-blue'
  return 'action-gray'
}

// Expose fetchLogs so parent can call it
defineExpose({ fetchLogs })

// Auto-load on mount
fetchLogs()
</script>

<style scoped>
.audit-table-wrap {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.audit-toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.audit-search {
  flex: 1;
  max-width: 480px;
  padding: 0.65rem 1rem;
  font-size: 0.9rem;
}

.audit-count {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-muted);
  white-space: nowrap;
}

.audit-loading, .audit-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.spinner-sm {
  width: 22px;
  height: 22px;
  border: 3px solid rgba(14,165,233,0.15);
  border-top-color: #0EA5E9;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.audit-scroll {
  overflow-x: auto;
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.audit-table thead th {
  text-align: left;
  padding: 0.6rem 0.8rem;
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(14,116,144,0.1);
  white-space: nowrap;
}

.audit-row td {
  padding: 0.65rem 0.8rem;
  border-bottom: 1px solid rgba(14,116,144,0.06);
  color: var(--text-soft);
  vertical-align: middle;
}

.audit-row:hover td { background: rgba(14,165,233,0.04); }
.audit-row:last-child td { border-bottom: none; }

.col-time   { white-space: nowrap; color: var(--text-muted); font-size: 0.8rem; }
.col-email  { font-weight: 700; }
.col-target { font-family: monospace; font-size: 0.78rem; color: var(--text-muted); }
.col-details{ max-width: 240px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.action-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  border: 1px solid;
}

.action-red   { background:rgba(239,68,68,0.1);  border-color:rgba(239,68,68,0.3);  color:#DC2626; }
.action-amber { background:rgba(245,158,11,0.1); border-color:rgba(245,158,11,0.3); color:#B45309; }
.action-blue  { background:rgba(14,165,233,0.1); border-color:rgba(14,165,233,0.3); color:#0369A1; }
.action-gray  { background:rgba(100,116,139,0.1);border-color:rgba(100,116,139,0.2);color:#475569; }

.audit-pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-page {
  background: rgba(255,255,255,0.6);
  border: 1px solid var(--glass-border);
  padding: 0.4rem 0.9rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-page:hover:not(:disabled) { background: rgba(255,255,255,0.9); }
.btn-page:disabled { opacity: 0.4; cursor: not-allowed; }

.page-info { font-size: 0.82rem; color: var(--text-muted); font-weight: 700; }
</style>
