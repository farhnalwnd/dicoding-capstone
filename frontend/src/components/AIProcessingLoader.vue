<template>
  <div class="glass-panel loader-dashboard">
    <!-- Error State Overlay -->
    <transition name="fade">
      <div v-if="status === 'error'" class="error-screen">
        <div class="error-card-container">
          <div class="error-icon-ring">
            <span class="error-cross">❌</span>
          </div>
          <h3 class="error-title">Processing Failed</h3>
          <p class="error-message-text">{{ errorMessage || message || 'An unexpected error occurred during processing.' }}</p>
          <button @click="$emit('close')" class="btn-danger close-error-btn">
            Dismiss & Retry
          </button>
        </div>
      </div>
    </transition>

    <!-- Success Completion State Screen -->
    <transition name="fade">
      <div v-if="progress >= 100 && status !== 'error'" class="success-screen">
        <div class="success-badge-container">
          <div class="success-icon-ring">
            <span class="success-checkmark">✓</span>
          </div>
          <h3 class="success-title">Analysis Completed</h3>
          <p class="success-duration">
            Finished in {{ elapsedTime.toFixed(1) }}s
          </p>
        </div>
      </div>
    </transition>

    <!-- Header Section -->
    <div class="loader-header">
      <div class="header-icon-container">
        <span class="pulse-icon">⚡</span>
      </div>
      <div class="header-text-container">
        <h3 class="loader-title">AI Processing Dashboard</h3>
        <p class="loader-message">{{ message || 'Executing AI pipeline...' }}</p>
      </div>
    </div>

    <!-- Progress Section -->
    <div class="progress-section">
      <div class="progress-meta">
        <span class="progress-label">Real-Time Progress</span>
        <span class="progress-percentage">{{ Math.round(progress) }}%</span>
      </div>

      <!-- Linear CSS Progress Bar -->
      <div class="progress-bar-track">
        <div class="progress-bar-fill" :style="{ width: progress + '%' }"></div>
      </div>

      <!-- Monospace Visual Blocks Progress Bar -->
      <div class="progress-blocks-visual">
        <span class="blocks-text">{{ blockVisual }}</span>
      </div>
    </div>

    <!-- Dashboard Content Grid -->
    <div class="dashboard-body">
      <!-- Left Column: Timeline Steps -->
      <div class="timeline-column">
        <h4 class="column-title">Pipeline Progress</h4>
        <div class="timeline-steps">
          <div
            v-for="(step, idx) in steps"
            :key="step"
            class="timeline-step"
            :class="getStepClass(idx)"
          >
            <div class="step-status-marker">
              <span v-if="idx < currentStep" class="marker-completed">✓</span>
              <span v-else-if="idx === currentStep" class="marker-processing-spinner">⏳</span>
              <span v-else class="marker-pending">○</span>
            </div>
            <div class="step-info">
              <span class="step-name">{{ step }}</span>
              <span class="step-status-label">{{ getStepStatusLabel(idx) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Stats / Timer -->
      <div class="timer-column">
        <div class="timer-card">
          <span class="timer-label">Processing Time</span>
          <div class="timer-value" :class="{ 'timer-completed': progress >= 100 }">
            {{ formattedTime }}
          </div>
          <span class="timer-sub">
            {{ progress >= 100 ? `Completed in ${elapsedTime.toFixed(1)} seconds` : 'AI pipeline executing...' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  progress: {
    type: Number,
    default: 0
  },
  message: {
    type: String,
    default: ''
  },
  elapsedTime: {
    type: Number,
    default: 0
  },
  status: {
    type: String,
    default: 'processing'
  },
  errorMessage: {
    type: String,
    default: ''
  },
  steps: {
    type: Array,
    default: () => [
      'Upload CV',
      'Parse Resume',
      'Extract Skills',
      'Generate Embeddings',
      'Match CV & Job Description',
      'Generate Explainability',
      'Finalize Results'
    ]
  }
})

defineEmits(['close'])

// Compute step index automatically based on progress percentage and step thresholds
const currentStep = computed(() => {
  if (props.progress >= 100) return props.steps.length
  
  if (props.steps.length === 7) {
    if (props.progress >= 95) return 6
    if (props.progress >= 85) return 5
    if (props.progress >= 70) return 4
    if (props.progress >= 50) return 3
    if (props.progress >= 35) return 2
    if (props.progress >= 20) return 1
    return 0
  } else if (props.steps.length === 4) {
    const isSemanticSearch = props.steps.includes('Parsing Query')
    const isHrRanking = props.steps.includes('Ranking Candidates')
    const isHrClustering = props.steps.includes('Clustering Candidates')
    
    if (isSemanticSearch) {
      if (props.progress >= 85) return 3
      if (props.progress >= 60) return 2
      if (props.progress >= 35) return 1
      return 0
    } else if (isHrRanking) {
      if (props.progress >= 75) return 3
      if (props.progress >= 50) return 2
      if (props.progress >= 30) return 1
      return 0
    } else if (isHrClustering) {
      if (props.progress >= 85) return 3
      if (props.progress >= 60) return 2
      if (props.progress >= 30) return 1
      return 0
    }
  }
  
  // Fallback: linear mapping
  return Math.min(
    props.steps.length - 1,
    Math.floor((props.progress / 100) * props.steps.length)
  )
})

// Monospace blocks bar visual: e.g., ██████████░░░░░░░░
const blockVisual = computed(() => {
  const totalBlocks = 20
  const filledCount = Math.min(totalBlocks, Math.round((props.progress / 100) * totalBlocks))
  const emptyCount = Math.max(0, totalBlocks - filledCount)
  return '█'.repeat(filledCount) + '░'.repeat(emptyCount)
})

// Time formatter: MM:SS or Completed format
const formattedTime = computed(() => {
  if (props.progress >= 100) {
    return `${props.elapsedTime.toFixed(1)}s`
  }
  const mins = Math.floor(props.elapsedTime / 60)
  const secs = Math.floor(props.elapsedTime % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

// Step Classes for timeline highlights
const getStepClass = (idx) => {
  if (idx < currentStep.value) return 'step-completed'
  if (idx === currentStep.value) return 'step-processing'
  return 'step-pending'
}

const getStepStatusLabel = (idx) => {
  if (idx < currentStep.value) return 'Completed'
  if (idx === currentStep.value) return 'Processing'
  return 'Pending'
}
</script>

<style scoped>
.loader-dashboard {
  position: relative;
  overflow: hidden;
  padding: 2.5rem;
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-strong);
  margin-top: 2rem;
  margin-bottom: 2rem;
  animation: slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Success / Error Overlay Screen Styling */
.success-screen, .error-screen {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.success-badge-container, .error-card-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.2rem;
  max-width: 420px;
  padding: 2rem;
  animation: scaleUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes scaleUp {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.success-icon-ring, .error-icon-ring {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-icon-ring {
  background: rgba(34, 197, 94, 0.12);
  border: 2px solid var(--success);
  box-shadow: 0 10px 25px rgba(34, 197, 94, 0.24);
}

.error-icon-ring {
  background: rgba(239, 68, 68, 0.12);
  border: 2px solid var(--danger);
  box-shadow: 0 10px 25px rgba(239, 68, 68, 0.24);
}

.success-checkmark, .error-cross {
  font-size: 2.6rem;
  font-weight: bold;
}

.success-checkmark {
  color: var(--success);
}

.error-cross {
  color: var(--danger);
}

.success-title {
  margin: 0;
  font-size: 1.85rem;
  font-weight: 850;
  color: var(--text);
}

.error-title {
  margin: 0;
  font-size: 1.85rem;
  font-weight: 850;
  color: var(--text);
}

.success-duration {
  margin: 0;
  font-size: 1.05rem;
  color: var(--text-muted);
  font-weight: 700;
}

.error-message-text {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-muted);
  font-weight: 600;
  line-height: 1.6;
}

.close-error-btn {
  margin-top: 0.5rem;
  min-width: 160px;
}

/* Header Section styling */
.loader-header {
  display: flex;
  align-items: center;
  gap: 1.4rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 1.5rem;
  margin-bottom: 1.8rem;
}

.header-icon-container {
  width: 50px;
  height: 50px;
  border-radius: 16px;
  background: rgba(14, 165, 233, 0.1);
  border: 1px solid rgba(14, 165, 233, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.02);
}

.pulse-icon {
  display: inline-block;
  animation: pulseRotate 2s infinite ease-in-out;
}

@keyframes pulseRotate {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15) rotate(10deg); }
}

.loader-title {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 850;
  color: var(--text);
}

.loader-message {
  margin: 0.35rem 0 0;
  font-size: 0.95rem;
  color: var(--text-muted);
  font-weight: 600;
  min-height: 1.3rem;
}

/* Progress bar and numeric percentage */
.progress-section {
  background: rgba(255, 255, 255, 0.38);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.85rem;
}

.progress-label {
  font-size: 0.88rem;
  font-weight: 800;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.progress-percentage {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--primary-dark);
}

.progress-bar-track {
  width: 100%;
  height: 12px;
  background: rgba(14, 116, 144, 0.08);
  border-radius: 999px;
  overflow: hidden;
  position: relative;
  margin-bottom: 0.95rem;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--secondary) 0%, var(--indigo) 100%);
  transition: width 0.2s ease-out;
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
}

.progress-blocks-visual {
  font-family: var(--mono);
  font-size: 1.05rem;
  letter-spacing: 2px;
  display: flex;
  justify-content: center;
  color: var(--primary);
  background: rgba(14, 165, 233, 0.04);
  padding: 0.45rem 1rem;
  border-radius: 8px;
  border: 1px dashed rgba(14, 165, 233, 0.12);
  user-select: none;
}

.blocks-text {
  text-shadow: 0 0 2px rgba(14, 165, 233, 0.1);
}

/* Dashboard Body columns (Timeline & Timer) */
.dashboard-body {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 2rem;
}

.timeline-column {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.column-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  border-left: 3px solid var(--secondary);
  padding-left: 0.6rem;
}

.timeline-steps {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  padding-left: 0.2rem;
}

.timeline-step {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  padding: 0.85rem 1.1rem;
  border-radius: 16px;
  transition: all 0.25s ease;
  border: 1px solid transparent;
}

.timeline-step.step-completed {
  background: rgba(34, 197, 94, 0.05);
  border-color: rgba(34, 197, 94, 0.12);
}

.timeline-step.step-processing {
  background: rgba(14, 165, 233, 0.06);
  border-color: rgba(14, 165, 233, 0.2);
  box-shadow: var(--shadow-soft);
  transform: translateX(4px);
}

.timeline-step.step-pending {
  background: rgba(255, 255, 255, 0.15);
  opacity: 0.6;
}

.step-status-marker {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  font-weight: bold;
}

.step-completed .step-status-marker {
  background: rgba(34, 197, 94, 0.15);
  color: var(--success);
}

.step-processing .step-status-marker {
  background: rgba(14, 165, 233, 0.15);
  color: var(--primary);
  animation: spinnerRotate 2.5s infinite linear;
}

@keyframes spinnerRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.step-pending .step-status-marker {
  color: var(--text-muted);
  border: 1.5px dashed rgba(148, 163, 184, 0.4);
}

.step-info {
  display: flex;
  flex-direction: column;
}

.step-name {
  font-size: 0.94rem;
  font-weight: 750;
  color: var(--text);
}

.step-completed .step-name {
  color: #15803D;
  text-decoration: line-through;
  opacity: 0.85;
}

.step-processing .step-name {
  color: var(--primary-dark);
}

.step-status-label {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--text-muted);
}

.step-completed .step-status-label {
  color: #16A34A;
}

.step-processing .step-status-label {
  color: var(--secondary);
}

/* Right Column (Timer card) */
.timer-column {
  display: flex;
  align-items: flex-start;
}

.timer-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: var(--radius-lg);
  padding: 2.2rem 1.8rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.015);
  transition: all 0.3s ease;
}

.timer-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.55);
  box-shadow: 0 14px 38px rgba(15, 23, 42, 0.03);
}

.timer-label {
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.timer-value {
  font-family: var(--mono);
  font-size: 3.25rem;
  font-weight: 900;
  line-height: 1;
  color: var(--text);
  margin: 0.4rem 0;
}

.timer-value.timer-completed {
  color: var(--text);
}

.timer-sub {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 600;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive configurations */
@media (max-width: 768px) {
  .loader-dashboard {
    padding: 1.8rem 1.4rem;
  }
  
  .dashboard-body {
    grid-template-columns: 1fr;
    gap: 1.8rem;
  }
  
  .timer-card {
    padding: 1.5rem;
  }
  
  .timer-value {
    font-size: 2.6rem;
  }
  
  .timeline-step.step-processing {
    transform: none;
  }
}
</style>
