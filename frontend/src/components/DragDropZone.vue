<template>
  <div
    class="drop-zone"
    :class="{ 'drop-zone--hover': isDragOver, 'drop-zone--has-files': selectedFiles.length > 0, 'drop-zone--error': errorMessage }"
    @dragenter.prevent="onDragEnter"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
    @click="openFilePicker"
    role="button"
    tabindex="0"
    @keydown.enter="openFilePicker"
    @keydown.space.prevent="openFilePicker"
    :aria-label="label"
  >
    <input
      ref="fileInputRef"
      type="file"
      :accept="accept"
      :multiple="multiple"
      class="drop-zone__input"
      @change="onFileInputChange"
      aria-hidden="true"
      tabindex="-1"
    />

    <!-- Empty state -->
    <div v-if="selectedFiles.length === 0" class="drop-zone__placeholder">
      <div class="drop-zone__icon" :class="{ 'drop-zone__icon--bounce': isDragOver }">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      </div>
      <div class="drop-zone__text">{{ label }}</div>
      <div class="drop-zone__hint">or click to browse</div>
      <div class="drop-zone__formats">{{ accept.replace(/\./g, '').toUpperCase() }} &middot; Max {{ maxSize }}MB</div>
    </div>

    <!-- Selected files -->
    <div v-else class="drop-zone__files" @click.stop>
      <div v-for="(file, idx) in selectedFiles" :key="file.name + idx" class="drop-zone__file-tag">
        <svg class="drop-zone__file-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
        <span class="drop-zone__file-name">{{ file.name }}</span>
        <span class="drop-zone__file-size">{{ formatSize(file.size) }}</span>
        <button
          class="drop-zone__file-remove"
          type="button"
          @click.stop="removeFile(idx)"
          :aria-label="'Remove ' + file.name"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
      <div class="drop-zone__change-hint">Click or drop to replace</div>
    </div>

    <!-- Error message -->
    <div v-if="errorMessage" class="drop-zone__error" role="alert">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="15" y1="9" x2="9" y2="15" />
        <line x1="9" y1="9" x2="15" y2="15" />
      </svg>
      <span>{{ errorMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  accept: {
    type: String,
    default: '.pdf,.doc,.docx'
  },
  multiple: {
    type: Boolean,
    default: false
  },
  maxSize: {
    type: Number,
    default: 8
  },
  label: {
    type: String,
    default: 'Drop your file here'
  }
})

const emit = defineEmits(['files-selected'])

const fileInputRef = ref(null)
const isDragOver = ref(false)
const selectedFiles = ref([])
const errorMessage = ref('')
let dragCounter = 0

function openFilePicker() {
  fileInputRef.value?.click()
}

function onDragEnter() {
  dragCounter++
  isDragOver.value = true
}

function onDragOver() {
  isDragOver.value = true
}

function onDragLeave() {
  dragCounter--
  if (dragCounter <= 0) {
    dragCounter = 0
    isDragOver.value = false
  }
}

function onDrop(e) {
  dragCounter = 0
  isDragOver.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  processFiles(files)
}

function onFileInputChange(e) {
  const files = Array.from(e.target.files || [])
  processFiles(files)
  // Reset input so same file can be re-selected
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function processFiles(files) {
  errorMessage.value = ''
  if (!files.length) return

  const maxBytes = props.maxSize * 1024 * 1024
  const acceptedExtensions = props.accept
    .split(',')
    .map(ext => ext.trim().toLowerCase())

  const validated = []

  for (const file of files) {
    // Check extension
    const fileName = (file.name || '').toLowerCase()
    const hasValidExt = acceptedExtensions.some(ext => fileName.endsWith(ext))
    if (!hasValidExt) {
      errorMessage.value = `"${file.name}" is not a supported file type. Accepted: ${props.accept}`
      return
    }

    // Check size
    if (file.size > maxBytes) {
      errorMessage.value = `"${file.name}" exceeds the ${props.maxSize}MB limit.`
      return
    }

    validated.push(file)

    if (!props.multiple) break
  }

  selectedFiles.value = validated
  emit('files-selected', validated)
}

function removeFile(idx) {
  selectedFiles.value.splice(idx, 1)
  if (selectedFiles.value.length === 0) {
    emit('files-selected', [])
  } else {
    emit('files-selected', [...selectedFiles.value])
  }
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.drop-zone {
  position: relative;
  border: 2px dashed var(--line, rgba(14, 116, 144, 0.22));
  border-radius: 20px;
  padding: 2rem 1.5rem;
  text-align: center;
  cursor: pointer;
  background: var(--surface, rgba(255, 255, 255, 0.72));
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.drop-zone:hover {
  border-color: rgba(14, 165, 233, 0.4);
  background: rgba(14, 165, 233, 0.04);
}

.drop-zone--hover {
  border-color: var(--secondary, #0EA5E9);
  background: rgba(14, 165, 233, 0.08);
  transform: scale(1.02);
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1), 0 12px 32px rgba(14, 165, 233, 0.12);
}

.drop-zone--error {
  border-color: rgba(239, 68, 68, 0.4);
}

.drop-zone--has-files {
  border-style: solid;
  border-color: rgba(34, 197, 94, 0.3);
  background: rgba(34, 197, 94, 0.04);
}

.drop-zone--has-files:hover {
  border-color: rgba(34, 197, 94, 0.5);
  background: rgba(34, 197, 94, 0.06);
}

[data-theme='dark'] .drop-zone {
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(148, 163, 184, 0.18);
}

[data-theme='dark'] .drop-zone:hover {
  border-color: rgba(56, 189, 248, 0.35);
  background: rgba(56, 189, 248, 0.06);
}

[data-theme='dark'] .drop-zone--hover {
  border-color: var(--secondary, #38BDF8);
  background: rgba(56, 189, 248, 0.1);
  box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.08), 0 12px 32px rgba(56, 189, 248, 0.08);
}

[data-theme='dark'] .drop-zone--has-files {
  border-color: rgba(34, 197, 94, 0.25);
  background: rgba(34, 197, 94, 0.06);
}

.drop-zone__input {
  display: none;
}

.drop-zone__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.drop-zone__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(99, 102, 241, 0.08));
  color: var(--secondary, #0EA5E9);
  margin-bottom: 0.4rem;
  transition: transform 0.2s ease, background 0.2s ease;
}

[data-theme='dark'] .drop-zone__icon {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(99, 102, 241, 0.1));
  color: #38BDF8;
}

.drop-zone__icon--bounce {
  animation: iconBounce 0.6s ease infinite alternate;
}

@keyframes iconBounce {
  from { transform: translateY(0); }
  to { transform: translateY(-6px); }
}

.drop-zone__text {
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--text, #0F172A);
}

[data-theme='dark'] .drop-zone__text {
  color: var(--text, #F1F5F9);
}

.drop-zone__hint {
  font-size: 0.85rem;
  color: var(--text-muted, #64748B);
  font-weight: 500;
}

.drop-zone__formats {
  font-size: 0.78rem;
  color: var(--text-muted, #64748B);
  opacity: 0.7;
  margin-top: 0.2rem;
  letter-spacing: 0.02em;
}

/* Selected files */
.drop-zone__files {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.drop-zone__file-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.85rem;
  border-radius: 12px;
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.2);
  max-width: 100%;
  transition: all 0.2s ease;
}

[data-theme='dark'] .drop-zone__file-tag {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.2);
}

.drop-zone__file-icon {
  flex-shrink: 0;
  color: #22C55E;
}

.drop-zone__file-name {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text, #0F172A);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

[data-theme='dark'] .drop-zone__file-name {
  color: var(--text, #F1F5F9);
}

.drop-zone__file-size {
  font-size: 0.78rem;
  color: var(--text-muted, #64748B);
  flex-shrink: 0;
}

.drop-zone__file-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  border: none;
  background: rgba(239, 68, 68, 0.08);
  color: #EF4444;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
  padding: 0;
}

.drop-zone__file-remove:hover {
  background: rgba(239, 68, 68, 0.16);
  transform: scale(1.1);
}

.drop-zone__change-hint {
  font-size: 0.78rem;
  color: var(--text-muted, #64748B);
  opacity: 0.7;
  margin-top: 0.15rem;
}

.drop-zone__error {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  justify-content: center;
  margin-top: 0.6rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: #EF4444;
}
</style>
