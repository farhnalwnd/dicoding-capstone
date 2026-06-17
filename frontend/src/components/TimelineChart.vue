<template>
  <div class="chart-container-inner">
    <h4 class="chart-inner-title">Recruitment Activity Timeline</h4>
    <div class="chart-wrapper">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

const props = defineProps({
  timelineData: {
    type: Array,
    required: true,
    default: () => []
  }
})

const chartData = computed(() => {
  // Sort by date ascending to make sure time series is ordered
  const sortedData = [...props.timelineData].sort((a, b) => new Date(a.date) - new Date(b.date))
  const dates = sortedData.map(d => d.date)
  
  const added = sortedData.map(d => d.added)
  const talentPool = sortedData.map(d => d.talent_pool)
  const interview = sortedData.map(d => d.interview)
  const hired = sortedData.map(d => d.hired)
  const rejected = sortedData.map(d => d.rejected)
  
  return {
    labels: dates,
    datasets: [
      {
        label: 'Candidates Added',
        data: added,
        borderColor: '#0EA5E9', // Blue
        backgroundColor: 'rgba(14, 165, 233, 0.15)',
        tension: 0.3,
        fill: false,
        pointRadius: 4
      },
      {
        label: 'Talent Pool',
        data: talentPool,
        borderColor: '#8B5CF6', // Purple
        backgroundColor: 'rgba(139, 92, 246, 0.15)',
        tension: 0.3,
        fill: false,
        pointRadius: 4
      },
      {
        label: 'Interviews',
        data: interview,
        borderColor: '#F59E0B', // Amber
        backgroundColor: 'rgba(245, 158, 11, 0.15)',
        tension: 0.3,
        fill: false,
        pointRadius: 4
      },
      {
        label: 'Hired',
        data: hired,
        borderColor: '#22C55E', // Green
        backgroundColor: 'rgba(34, 197, 94, 0.15)',
        tension: 0.3,
        fill: false,
        pointRadius: 4
      },
      {
        label: 'Rejected',
        data: rejected,
        borderColor: '#EF4444', // Red
        backgroundColor: 'rgba(239, 68, 68, 0.15)',
        tension: 0.3,
        fill: false,
        pointRadius: 4
      }
    ]
  }
})

const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 12,
          padding: 15,
          font: { family: 'Inter', weight: '700', size: 10 },
          color: '#64748B'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleFont: { family: 'Inter', weight: '700' },
        bodyFont: { family: 'Inter' },
        mode: 'index',
        intersect: false
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(148, 163, 184, 0.05)'
        },
        ticks: {
          color: '#64748B',
          font: { family: 'Inter', weight: '700', size: 9 }
        }
      },
      y: {
        grid: {
          color: 'rgba(148, 163, 184, 0.08)'
        },
        ticks: {
          color: '#64748B',
          font: { family: 'Inter', weight: '700', size: 10 },
          stepSize: 1
        }
      }
    }
  }
})
</script>

<style scoped>
.chart-container-inner {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.chart-inner-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 850;
  color: var(--text-soft);
}

.chart-wrapper {
  flex-grow: 1;
  position: relative;
  min-height: 240px;
}
</style>
