<template>
  <div v-if="modelInfo" class="model-info-badge">
    <div class="badge-content" @click="toggleDetails">
      <span class="pulse-icon"></span>
      <span class="badge-text">Active Models Info</span>
    </div>
    
    <div v-if="showDetails" class="model-details-dropdown">
      <div class="detail-row">
        <span class="label">Bi-Encoder:</span>
        <span class="value">{{ modelInfo.bi_encoder }}</span>
      </div>
      <div class="detail-row">
        <span class="label">Cross-Encoder:</span>
        <span class="value">{{ modelInfo.cross_encoder }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const modelInfo = ref(null)
const showDetails = ref(false)

const toggleDetails = () => {
  showDetails.value = !showDetails.value
}

const fetchModelInfo = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/model-info`)
    modelInfo.value = res.data
  } catch (error) {
    console.error("Failed to fetch model info", error)
  }
}

onMounted(() => {
  fetchModelInfo()
})
</script>

<style scoped>
.model-info-badge {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.badge-content {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(3, 105, 161, 0.25);
  padding: 8px 16px;
  border-radius: 30px;
  cursor: pointer;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
  transition: all 0.3s ease;
}

.badge-content:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: translateY(-2px);
}

.pulse-icon {
  width: 10px;
  height: 10px;
  background-color: #22C55E;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
  animation: pulse 1.6s infinite;
}

.badge-text {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0369A1;
}

.model-details-dropdown {
  position: absolute;
  bottom: 50px;
  right: 0;
  width: 320px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(3, 105, 161, 0.2);
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  gap: 10px;
}

.label {
  font-weight: 700;
  color: #0C4A6E;
  min-width: 100px;
}

.value {
  color: #0369A1;
  word-break: break-all;
  text-align: right;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(34, 197, 94, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
  }
}
</style>