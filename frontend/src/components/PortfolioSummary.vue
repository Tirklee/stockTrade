<template>
  <div class="portfolio-summary">
    <el-row :gutter="20" class="summary-row">
      <el-col :span="4">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-label">总市值</div>
            <div class="summary-value">¥{{ formatNumber(summary.total_market_value) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-label">持仓成本</div>
            <div class="summary-value">¥{{ formatNumber(summary.total_cost) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-label">盈亏金额</div>
            <div :class="pnlClass">¥{{ formatNumber(summary.total_pnl) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-label">盈亏比例</div>
            <div :class="pnlClass">{{ formatNumber(summary.pnl_rate) }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-label">持仓股票</div>
            <div class="summary-value">{{ summary.stock_count }} 只</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-label">总资产</div>
            <div class="summary-value">¥{{ formatNumber(summary.total_market_value) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { usePortfolioStore } from '../store/portfolio'

const portfolioStore = usePortfolioStore()

const summary = computed(() => portfolioStore.summary)

const formatNumber = (num) => {
  return typeof num === 'number' ? num.toFixed(2) : num
}

const pnlClass = computed(() => {
  return portfolioStore.summary.total_pnl >= 0 ? 'positive' : 'negative'
})

onMounted(() => {
  portfolioStore.fetchSummary()
})
</script>

<style scoped>
.portfolio-summary {
  margin-bottom: 20px;
}

.summary-row {
  margin: 0 !important;
}

.summary-card {
  height: 120px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 18px;
  font-weight: bold;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}
</style>