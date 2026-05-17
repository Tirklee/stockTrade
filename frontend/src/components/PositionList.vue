<template>
  <div class="position-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>持仓明细</span>
          <el-button type="primary" @click="refreshData">刷新</el-button>
        </div>
      </template>

      <el-table :data="positions" v-loading="loading" stripe border>
        <el-table-column prop="stock_code" label="代码" width="100" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="total_quantity" label="持股数" width="90" align="right" />
        <el-table-column prop="avg_cost" label="成本价" width="100" align="right">
          <template #default="{ row }">
            {{ row.avg_cost.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="现价" width="100" align="right">
          <template #default="{ row }">
            {{ row.current_price.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column label="市值" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.current_value) }}
          </template>
        </el-table-column>
        <el-table-column label="盈亏金额" width="120" align="right">
          <template #default="{ row }">
            <span :class="row.unrealized_pnl >= 0 ? 'positive' : 'negative'">
              {{ formatMoney(row.unrealized_pnl) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="盈亏比例" width="100" align="right">
          <template #default="{ row }">
            <span :class="row.unrealized_pnl_rate >= 0 ? 'positive' : 'negative'">
              {{ row.unrealized_pnl_rate.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleTrade(row, 'buy')">买入</el-button>
            <el-button type="danger" size="small" @click="handleTrade(row, 'sell')">卖出</el-button>
            <el-button type="info" size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && positions.length === 0" description="暂无持仓" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePortfolioStore } from '../store/portfolio'

const router = useRouter()
const portfolioStore = usePortfolioStore()

const positions = computed(() => portfolioStore.positions)
const loading = computed(() => portfolioStore.loading)

const formatMoney = (num) => {
  return typeof num === 'number' ? num.toFixed(2) : num
}

const refreshData = () => {
  portfolioStore.refresh()
}

const handleTrade = (row, type) => {
  router.push({ name: 'StockDetail', params: { code: row.stock_code }, query: { type } })
}

const viewDetail = (row) => {
  router.push({ name: 'StockDetail', params: { code: row.stock_code } })
}

onMounted(() => {
  portfolioStore.fetchPositions()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}
</style>