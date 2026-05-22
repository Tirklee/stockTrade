<template>
  <div class="stock-detail">
    <el-page-header @back="goBack" content="股票详情" />

    <el-row :gutter="20" class="mt-20 main-content">
      <el-col :span="16">
        <el-card class="chart-card">
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

          <div class="chart-wrapper">
            <KLineChart
              ref="klineChart"
              :code="stockCode"
              :name="stockData.stock_name || stockCode"
            />
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
      :asset-type="stockData.asset_type || 'stock'"
      :available-quantity="positionData?.available_quantity || 999999"
      @success="handleTradeSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStockRealtime, getPosition, identifyStockType } from '../api'
import TradeDialog from '../components/TradeDialog.vue'
import KLineChart from '../components/KLineChart.vue'

const route = useRoute()
const router = useRouter()

const stockCode = computed(() => route.params.code)
const klineChart = ref(null)

const tradeDialogVisible = ref(false)
const tradeType = ref('buy')
const stockData = ref({})

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

const positionData = ref(null)

const loadPosition = async () => {
  try {
    const res = await getPosition(stockCode.value)
    if (res.code === 0) {
      positionData.value = res.data
    } else {
      positionData.value = null
    }
  } catch (error) {
    console.error('获取持仓失败:', error)
    positionData.value = null
  }
}

const loadRealtime = async () => {
  try {
    const res = await getStockRealtime(stockCode.value)
    if (res.code === 0) {
      stockData.value = res.data
    }
    const typeRes = await identifyStockType(stockCode.value)
    if (typeRes.code === 0) {
      stockData.value.asset_type = typeRes.data?.type || 'stock'
    }
  } catch (error) {
    console.error('获取行情失败:', error)
  }
}

// K线数据由子组件自行加载（使用模拟数据）
// 实际项目需对接后端API：/api/stocks/{code}/kline?period=...

const showTrade = (type) => {
  tradeType.value = type
  tradeDialogVisible.value = true
}

const handleTradeSuccess = () => {
  loadPosition()
  loadRealtime()
}

const goBack = () => {
  router.push({ name: 'Dashboard' })
}

let refreshTimer = null

onMounted(() => {
  loadRealtime()
  loadPosition()

  refreshTimer = setInterval(() => {
    loadRealtime()
  }, 30000)

  nextTick(() => {
    setTimeout(() => klineChart.value?.resizeCharts(), 100)
  })
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

watch(stockCode, () => {
  loadRealtime()
  loadPosition()
})

// 监听子组件 period/subIndicator 的变化来重新加载图表数据（如需动态获取）
</script>

<style scoped>
.stock-detail {
  padding: 8px;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.mt-20 {
  margin-top: 8px;
  flex: 1;
  min-height: 0;
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

.chart-tabs {
  margin-bottom: 8px;
}

.chart-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.chart-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-card :deep(.el-card__body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.chart-wrapper {
  flex: 1;
  min-height: 0;
  height: auto;
}

.indicator-selector {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
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
