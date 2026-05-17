<template>
  <div class="stock-detail">
    <el-page-header @back="goBack" content="股票详情" />

    <el-row :gutter="20" class="mt-20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <div class="stock-info">
                <span class="stock-name">{{ stockData.stock_name || stockCode }}</span>
                <span class="stock-code">{{ stockCode }}</span>
              </div>
              <div class="stock-price">
                <span class="price">{{ stockData.current_price?.toFixed(3) || '--' }}</span>
                <span class="change" :class="priceChangeClass">
                  {{ priceChangeText }}
                </span>
              </div>
            </div>
          </template>

          <div class="chart-container" ref="chartRef"></div>

          <div class="kline-tabs">
            <el-radio-group v-model="klinePeriod" size="small" @change="handlePeriodChange">
              <el-radio-button label="1min">1分钟</el-radio-button>
              <el-radio-button label="5min">5分钟</el-radio-button>
              <el-radio-button label="15min">15分钟</el-radio-button>
              <el-radio-button label="60min">60分钟</el-radio-button>
              <el-radio-button label="daily">日K</el-radio-button>
              <el-radio-button label="weekly">周K</el-radio-button>
              <el-radio-button label="monthly">月K</el-radio-button>
            </el-radio-group>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="info-card">
          <template #header>
            <span>行情信息</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="今开">
              {{ stockData.open_price?.toFixed(3) || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="昨收">
              {{ stockData.prev_close?.toFixed(3) || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="最高">
              {{ stockData.high_price?.toFixed(3) || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="最低">
              {{ stockData.low_price?.toFixed(3) || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="成交量">
              {{ formatVolume(stockData.volume) }}
            </el-descriptions-item>
            <el-descriptions-item label="成交额">
              {{ formatMoney(stockData.amount) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="position-card mt-20">
          <template #header>
            <span>持仓信息</span>
          </template>
          <el-descriptions v-if="positionData" :column="1" border size="small">
            <el-descriptions-item label="持股数">
              {{ positionData.total_quantity }}
            </el-descriptions-item>
            <el-descriptions-item label="成本价">
              {{ positionData.avg_cost?.toFixed(3) }}
            </el-descriptions-item>
            <el-descriptions-item label="市值">
              {{ formatMoney(positionData.current_value) }}
            </el-descriptions-item>
            <el-descriptions-item label="盈亏">
              <span :class="positionData.unrealized_pnl >= 0 ? 'positive' : 'negative'">
                {{ formatMoney(positionData.unrealized_pnl) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="盈亏比例">
              <span :class="positionData.unrealized_pnl_rate >= 0 ? 'positive' : 'negative'">
                {{ positionData.unrealized_pnl_rate?.toFixed(2) }}%
              </span>
            </el-descriptions-item>
          </el-descriptions>
          <el-empty v-else description="暂无持仓" />
        </el-card>

        <div class="trade-buttons mt-20">
          <el-button type="primary" size="large" style="width: 48%" @click="showTrade('buy')">
            买入
          </el-button>
          <el-button type="danger" size="large" style="width: 48%" @click="showTrade('sell')">
            卖出
          </el-button>
        </div>
      </el-col>
    </el-row>

    <trade-dialog
      v-model="tradeDialogVisible"
      :trade-type="tradeType"
      :stock-code="stockCode"
      :stock-name="stockData.stock_name"
      :current-price="stockData.current_price"
      :available-quantity="positionData?.available_quantity || 999999"
      @success="handleTradeSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStockRealtime, getStockKline, getPosition } from '../api'
import TradeDialog from '../components/TradeDialog.vue'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()

const stockCode = computed(() => route.params.code)
const chartRef = ref()
let chartInstance = null

const stockData = ref({})
const positionData = ref(null)
const klinePeriod = ref('daily')
const klineData = ref([])

const tradeDialogVisible = ref(false)
const tradeType = ref('buy')

const priceChangeClass = computed(() => {
  const change = stockData.value.change_pct
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return ''
})

const priceChangeText = computed(() => {
  const data = stockData.value
  if (!data.change_pct) return '--'
  const sign = data.change_pct >= 0 ? '+' : ''
  return `${sign}${data.change_pct.toFixed(2)}%`
})

const formatMoney = (num) => {
  if (!num) return '--'
  return `¥${num.toFixed(2)}`
}

const formatVolume = (num) => {
  if (!num) return '--'
  return (num / 10000).toFixed(2) + '万'
}

const loadRealtime = async () => {
  try {
    const res = await getStockRealtime(stockCode.value)
    if (res.code === 0) {
      stockData.value = res.data
    }
  } catch (error) {
    console.error('获取行情失败:', error)
  }
}

const loadKline = async () => {
  try {
    const res = await getStockKline(stockCode.value, { period: klinePeriod.value })
    if (res.code === 0) {
      klineData.value = res.data.data
      renderChart()
    }
  } catch (error) {
    console.error('获取K线失败:', error)
  }
}

const loadPosition = async () => {
  try {
    const res = await getPosition(stockCode.value)
    if (res.code === 0) {
      positionData.value = res.data
    }
  } catch {
    positionData.value = null
  }
}

const renderChart = () => {
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const dates = klineData.value.map(item => item[0])
  const data = klineData.value.map(item => ({
    date: item[0],
    open: parseFloat(item[1]),
    high: parseFloat(item[2]),
    low: parseFloat(item[3]),
    close: parseFloat(item[4]),
    volume: parseInt(item[5])
  }))

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'line' }
    },
    grid: [
      { left: '10%', right: '8%', top: '10%', height: '60%' },
      { left: '10%', right: '8%', top: '75%', height: '15%' }
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, boundaryGap: false },
      { type: 'category', data: dates, gridIndex: 1, boundaryGap: false }
    ],
    yAxis: [
      { scale: true, gridIndex: 0 },
      { scale: true, gridIndex: 1 }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: data.map(d => [d.open, d.close, d.low, d.high]),
        xAxisIndex: 0,
        yAxisIndex: 0
      },
      {
        name: '成交量',
        type: 'bar',
        data: data.map(d => d.volume),
        xAxisIndex: 1,
        yAxisIndex: 1
      }
    ]
  }

  chartInstance.setOption(option)
}

const handlePeriodChange = () => {
  loadKline()
}

const showTrade = (type) => {
  tradeType.value = type
  tradeDialogVisible.value = true
}

const handleTradeSuccess = () => {
  loadPosition()
}

const goBack = () => {
  router.push({ name: 'Dashboard' })
}

let refreshTimer = null

onMounted(() => {
  loadRealtime()
  loadKline()
  loadPosition()

  refreshTimer = setInterval(() => {
    loadRealtime()
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (chartInstance) {
    chartInstance.dispose()
  }
})

watch(stockCode, () => {
  loadRealtime()
  loadKline()
  loadPosition()
})
</script>

<style scoped>
.mt-20 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-info .stock-name {
  font-size: 18px;
  font-weight: bold;
  margin-right: 10px;
}

.stock-info .stock-code {
  color: #909399;
}

.stock-price .price {
  font-size: 24px;
  font-weight: bold;
  margin-right: 10px;
}

.chart-container {
  height: 400px;
  margin: 20px 0;
}

.kline-tabs {
  margin-top: 10px;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}

.trade-buttons {
  display: flex;
  justify-content: space-between;
}
</style>