<template>
  <div class="chart-container-inner">
    <div class="chart-header-row">
      <h4 class="chart-inner-title">Recruitment Funnel</h4>
      <span class="funnel-metric" v-if="conversionRate > 0">
        Conversion Rate: <strong>{{ conversionRate }}%</strong>
      </span>
    </div>
    
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
  funnelData: {
    type: Array,
    required: true,
    default: () => []
  }
})

// Conversion rate is Hired / Applicants * 100
const conversionRate = computed(() => {
  const applicants = props.funnelData.find(d => d.stage === 'Applicants')?.count || 0
  const hired = props.funnelData.find(d => d.stage === 'Hired')?.count || 0
  if (applicants === 0) return 0
  return roundToDecimal((hired / applicants) * 100, 1)
})

function roundToDecimal(num, decimals) {
  return Number(Math.round(num + 'e' + decimals) + 'e-' + decimals)
}

const chartData = computed(() => {
  const stages = props.funnelData.map(d => d.stage)
  const counts = props.funnelData.map(d => d.count)
  
  // Custom funnel color gradient simulation
  const backgroundColors = [
    'rgba(14, 165, 233, 0.85)', // Applicants - Blue
    'rgba(34, 211, 238, 0.85)', // Screening - Cyan
    'rgba(139, 92, 246, 0.85)', // Talent Pool - Purple
    'rgba(245, 158, 11, 0.85)',  // Interview - Amber
    'rgba(34, 197, 94, 0.85)'   // Hired - Green
  ]
  const borderColors = [
    '#0EA5E9',
    '#22D3EE',
    '#8B5CF6',
    '#F59E0B',
    '#22C55E'
  ]

  return {
    labels: stages,
    datasets: [{
      label: 'Candidates',
      data: counts,
      backgroundColor: backgroundColors,
      borderColor: borderColors,
      borderWidth: 1.5,
      borderRadius: 10,
      barThickness: 24
    }]
  }
})

const chartOptions = computed(() => {
  return {
    indexAxis: 'y',
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
          label: (context) => {
            const index = context.dataIndex
            const pct = props.funnelData[index]?.percentage || 0
            return ` Candidates: ${context.raw} (${pct}% of applicants)`
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(148, 163, 184, 0.08)'
        },
        ticks: {
          color: '#64748B',
          font: { family: 'Inter', weight: '700', size: 10 }
        }
      },
      y: {
        grid: {
          display: false
        },
        ticks: {
          color: '#1E3A5F',
          font: { family: 'Inter', weight: '800', size: 11 }
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

.chart-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chart-inner-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 850;
  color: var(--text-soft);
}

.funnel-metric {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.funnel-metric strong {
  color: #16A34A;
  font-weight: 850;
}

.chart-wrapper {
  flex-grow: 1;
  position: relative;
  min-height: 240px;
}
</style>
