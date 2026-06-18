<template>
  <div class="chart-container-inner">
    <h4 class="chart-inner-title">Top Job Domains</h4>
    <div class="chart-wrapper">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  categoriesData: {
    type: Array,
    required: true,
    default: () => []
  }
})

const chartData = computed(() => {
  const labels = props.categoriesData.map(d => d.category)
  const counts = props.categoriesData.map(d => d.count)
  
  return {
    labels: labels,
    datasets: [{
      label: 'Candidates',
      data: counts,
      backgroundColor: 'rgba(34, 211, 238, 0.72)', // Cyan theme
      borderColor: '#22D3EE',
      borderWidth: 1.5,
      borderRadius: 6,
      barThickness: 28
    }]
  }
})

const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleFont: { family: 'Inter', weight: '700' },
        bodyFont: { family: 'Inter' },
        callbacks: {
          label: (context) => ` Total: ${context.raw} candidates`
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#1E3A5F',
          font: { family: 'Inter', weight: '800', size: 10 }
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
