<template>
  <div class="um-container">
    <!-- Header -->
    <header class="um-header glass-panel">
      <div>
        <span class="um-badge">
          <span class="badge-dot"></span>
          User Management
        </span>
        <h2>Platform Users</h2>
        <p class="um-sub">View, edit roles, disable or delete platform users.</p>
      </div>
      <router-link to="/admin" class="btn-back">← Admin Dashboard</router-link>
    </header>

    <!-- Filters & Search -->
    <div class="um-filters glass-panel">
      <input
        id="user-search-input"
        v-model="search"
        type="text"
        placeholder="Search by name or email..."
        class="input-field filter-search"
        @input="onSearch"
      />

      <select id="role-filter" v-model="roleFilter" class="input-field filter-select" @change="fetchUsers">
        <option value="">All Roles</option>
        <option value="hr">HR</option>
        <option value="jobseeker">Job Seeker</option>
        <option value="admin">Admin</option>
      </select>

      <select id="status-filter" v-model="statusFilter" class="input-field filter-select" @change="fetchUsers">
        <option value="">All Status</option>
        <option value="active">Active</option>
        <option value="disabled">Disabled</option>
      </select>

      <span class="um-total">{{ total }} users</span>
    </div>

    <!-- Table -->
    <div class="um-table-wrap glass-panel">
      <div v-if="loading" class="um-loading">
        <div class="spinner-sm"></div>
        <span>Loading users...</span>
      </div>

      <div v-else-if="!users.length" class="um-empty">No users found.</div>

      <div v-else class="um-scroll">
        <table class="um-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Provider</th>
              <th>Created</th>
              <th>Last Login</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" class="um-row">
              <td class="col-name">{{ user.name }}</td>
              <td class="col-email">{{ user.email }}</td>
              <td>
                <span class="role-badge" :class="`role-${user.role}`">{{ roleLabel[user.role] || user.role }}</span>
              </td>
              <td class="col-provider">{{ user.provider }}</td>
              <td class="col-time">{{ formatDate(user.created_at) }}</td>
              <td class="col-time">{{ user.last_login ? formatDate(user.last_login) : '—' }}</td>
              <td>
                <span class="status-dot" :class="user.disabled ? 'dot-disabled' : 'dot-active'">
                  {{ user.disabled ? 'Disabled' : 'Active' }}
                </span>
              </td>
              <td>
                <div class="action-btns">
                  <button
                    class="btn-act btn-edit"
                    :id="`edit-role-${user.id}`"
                    @click="openEditModal(user)"
                    title="Edit Role"
                  >✏️</button>
                  <button
                    class="btn-act"
                    :class="user.disabled ? 'btn-enable' : 'btn-disable'"
                    :id="`toggle-${user.id}`"
                    @click="toggleDisable(user)"
                    :title="user.disabled ? 'Enable User' : 'Disable User'"
                  >{{ user.disabled ? '✅' : '🚫' }}</button>
                  <button
                    class="btn-act btn-delete"
                    :id="`delete-${user.id}`"
                    @click="confirmDelete(user)"
                    title="Delete User"
                  >🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="total > limit" class="um-pagination">
        <button class="btn-page" :disabled="skip === 0" @click="prevPage">← Prev</button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="btn-page" :disabled="skip + limit >= total" @click="nextPage">Next →</button>
      </div>
    </div>

    <!-- Edit Role Modal -->
    <div v-if="editModal.visible" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-box glass-panel">
        <h3>Edit User Role</h3>
        <p class="modal-email">{{ editModal.user?.email }}</p>

        <div class="form-group">
          <label>New Role</label>
          <select id="modal-role-select" v-model="editModal.newRole" class="input-field">
            <option value="hr">HR Recruiter</option>
            <option value="jobseeker">Job Seeker</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div class="modal-actions">
          <button class="btn-primary" @click="saveRole" :disabled="editModal.loading" id="save-role-btn">
            {{ editModal.loading ? 'Saving...' : 'Save Role' }}
          </button>
          <button class="btn-cancel" @click="closeEditModal">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteModal.visible" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-box glass-panel">
        <h3>Delete User</h3>
        <p>Are you sure you want to permanently delete <strong>{{ deleteModal.user?.email }}</strong>?</p>
        <p class="modal-warn">⚠️ This action cannot be undone.</p>

        <div class="modal-actions">
          <button class="btn-danger" @click="doDelete" :disabled="deleteModal.loading" id="confirm-delete-btn">
            {{ deleteModal.loading ? 'Deleting...' : 'Yes, Delete' }}
          </button>
          <button class="btn-cancel" @click="closeDeleteModal">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const toast = inject('toast')

const users  = ref([])
const total  = ref(0)
const loading = ref(false)
const search  = ref('')
const roleFilter   = ref('')
const statusFilter = ref('')
const skip  = ref(0)
const limit = ref(25)

const currentPage = computed(() => Math.floor(skip.value / limit.value) + 1)
const totalPages  = computed(() => Math.ceil(total.value / limit.value))

const roleLabel = {
  hr: 'HR',
  jobseeker: 'Job Seeker',
  admin: 'Admin'
}

let debounceTimer = null

async function fetchUsers() {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const res = await axios.get(`${API_BASE_URL}/api/admin/users`, {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        role:   roleFilter.value   || undefined,
        status: statusFilter.value || undefined,
        search: search.value       || undefined,
        skip:   skip.value,
        limit:  limit.value
      }
    })
    users.value = res.data.users || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
    toast?.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    skip.value = 0
    fetchUsers()
  }, 350)
}

function prevPage() { skip.value = Math.max(0, skip.value - limit.value); fetchUsers() }
function nextPage() { skip.value = skip.value + limit.value; fetchUsers() }

function formatDate(ts) {
  if (!ts) return '—'
  try {
    return new Date(ts).toLocaleDateString('id-ID', { year:'numeric', month:'short', day:'numeric' })
  } catch { return ts }
}

// ── Edit Role Modal ──────────────────────────────
const editModal = ref({ visible: false, user: null, newRole: '', loading: false })

function openEditModal(user) {
  editModal.value = { visible: true, user, newRole: user.role, loading: false }
}

function closeEditModal() { editModal.value.visible = false }

async function saveRole() {
  editModal.value.loading = true
  try {
    const token = localStorage.getItem('token') || ''
    await axios.patch(
      `${API_BASE_URL}/api/admin/users/${editModal.value.user.id}`,
      { role: editModal.value.newRole },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    toast?.success(`Role updated to ${editModal.value.newRole}`)
    closeEditModal()
    fetchUsers()
  } catch (e) {
    toast?.error(e?.response?.data?.detail || 'Failed to update role')
  } finally {
    editModal.value.loading = false
  }
}

// ── Toggle Disable ───────────────────────────────
async function toggleDisable(user) {
  try {
    const token = localStorage.getItem('token') || ''
    await axios.patch(
      `${API_BASE_URL}/api/admin/users/${user.id}`,
      { disabled: !user.disabled },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    toast?.success(user.disabled ? 'User enabled' : 'User disabled')
    fetchUsers()
  } catch (e) {
    toast?.error(e?.response?.data?.detail || 'Action failed')
  }
}

// ── Delete Modal ─────────────────────────────────
const deleteModal = ref({ visible: false, user: null, loading: false })

function confirmDelete(user) {
  deleteModal.value = { visible: true, user, loading: false }
}

function closeDeleteModal() { deleteModal.value.visible = false }

async function doDelete() {
  deleteModal.value.loading = true
  try {
    const token = localStorage.getItem('token') || ''
    await axios.delete(
      `${API_BASE_URL}/api/admin/users/${deleteModal.value.user.id}`,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    toast?.success('User deleted successfully')
    closeDeleteModal()
    fetchUsers()
  } catch (e) {
    toast?.error(e?.response?.data?.detail || 'Delete failed')
  } finally {
    deleteModal.value.loading = false
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.um-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.um-header {
  padding: 2rem 2.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.um-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.25);
  color: #B91C1C;
  margin-bottom: 0.5rem;
}

.badge-dot {
  width: 0.44rem; height: 0.44rem;
  border-radius: 50%;
  background: #EF4444;
  box-shadow: 0 0 0 4px rgba(239,68,68,0.2);
}

.um-sub { margin: 0; color: var(--text-muted); font-size: 0.9rem; }

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255,255,255,0.7);
  border: 1px solid var(--glass-border);
  padding: 0.65rem 1.2rem;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 700;
  text-decoration: none;
  color: var(--text-soft);
  flex-shrink: 0;
  transition: all 0.2s;
}
.btn-back:hover { background: rgba(255,255,255,0.95); }

/* Filters */
.um-filters {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  flex-wrap: wrap;
}

.filter-search { flex: 1; min-width: 220px; padding: 0.65rem 1rem; }
.filter-select { padding: 0.65rem 0.9rem; min-width: 140px; }
.um-total { font-size: 0.82rem; font-weight: 700; color: var(--text-muted); white-space: nowrap; margin-left: auto; }

/* Table wrap */
.um-table-wrap {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.um-loading, .um-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2.5rem;
  color: var(--text-muted);
}

.spinner-sm {
  width: 22px; height: 22px;
  border: 3px solid rgba(14,165,233,0.15);
  border-top-color: #0EA5E9;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.um-scroll { overflow-x: auto; }

.um-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.86rem;
  min-width: 860px;
}

.um-table thead th {
  text-align: left;
  padding: 0.65rem 0.85rem;
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(14,116,144,0.1);
  white-space: nowrap;
}

.um-row td {
  padding: 0.7rem 0.85rem;
  border-bottom: 1px solid rgba(14,116,144,0.06);
  color: var(--text-soft);
  vertical-align: middle;
}

.um-row:hover td { background: rgba(14,165,233,0.03); }
.um-row:last-child td { border-bottom: none; }

.col-name   { font-weight: 700; }
.col-email  { color: var(--text-muted); font-size: 0.83rem; }
.col-time   { white-space: nowrap; color: var(--text-muted); font-size: 0.8rem; }
.col-provider { text-transform: capitalize; color: var(--text-muted); font-size: 0.82rem; }

/* Role badge */
.role-badge {
  display: inline-block;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  border: 1px solid;
}

.role-hr        { background:rgba(14,165,233,0.1);  border-color:rgba(14,165,233,0.3);  color:#0369A1; }
.role-jobseeker { background:rgba(139,92,246,0.1);  border-color:rgba(139,92,246,0.3);  color:#6D28D9; }
.role-admin     { background:rgba(239,68,68,0.1);   border-color:rgba(239,68,68,0.3);   color:#DC2626; }

/* Status dot */
.status-dot {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  border: 1px solid;
}

.dot-active   { background:rgba(34,197,94,0.1);  border-color:rgba(34,197,94,0.25);  color:#15803D; }
.dot-disabled { background:rgba(100,116,139,0.1);border-color:rgba(100,116,139,0.2);color:#475569; }

/* Action buttons */
.action-btns { display: flex; align-items: center; gap: 0.4rem; }

.btn-act {
  width: 32px; height: 32px;
  border: 1px solid var(--glass-border);
  background: rgba(255,255,255,0.5);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.18s;
}
.btn-act:hover { transform: scale(1.1); }
.btn-delete:hover { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.3); }

/* Pagination */
.um-pagination {
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

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15,23,42,0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-box {
  width: 100%;
  max-width: 420px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  border-radius: 20px;
}

.modal-box h3 { margin: 0; font-size: 1.1rem; font-weight: 800; color: var(--text-soft); }
.modal-email  { margin: 0; font-size: 0.9rem; color: var(--text-muted); word-break: break-all; }
.modal-warn   { margin: 0; font-size: 0.88rem; color: #DC2626; font-weight: 700; }

.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-group label { font-size: 0.8rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; }

.modal-actions { display: flex; gap: 0.75rem; }

.btn-cancel {
  background: rgba(255,255,255,0.5);
  border: 1px solid var(--glass-border);
  padding: 0.65rem 1.2rem;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-cancel:hover { background: rgba(255,255,255,0.85); }

.btn-danger {
  background: linear-gradient(135deg, #EF4444, #DC2626);
  color: white;
  border: none;
  padding: 0.7rem 1.4rem;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(239,68,68,0.3);
}
.btn-danger:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(239,68,68,0.4); }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
