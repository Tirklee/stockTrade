<template>
  <div class="positions-page">
    <portfolio-summary />

    <el-card>
      <template #header>
        <div class="card-header">
          <span>持仓明细</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索股票代码或名称"
              style="width: 200px; margin-right: 10px"
              clearable
            />
            <el-button type="primary" @click="refreshData">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredPositions" v-loading="loading" stripe border>
        <el-table-column prop="stock_code" label="代码" width="100" fixed />
        <el-table-column prop="stock_name" label="名称" width="120" fixed />
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            {{ row.asset_type === 'fund' ? '基金' : '股票' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_quantity" label="持股数" width="90" align="right" sortable />
        <el-table-column prop="avg_cost" label="成本价" width="100" align="right" sortable>
          <template #default="{ row }">
            {{ row.avg_cost.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="现价" width="100" align="right">
          <template #default="{ row }">
            {{ row.current_price.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column label="市值" width="120" align="right" sortable>
          <template #default="{ row }">
            {{ formatMoney(row.current_value) }}
          </template>
        </el-table-column>
        <el-table-column label="盈亏金额" width="120" align="right" sortable>
          <template #default="{ row }">
            <span :class="getPnlClass(row.unrealized_pnl)">
              {{ formatMoney(row.unrealized_pnl) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="盈亏比例" width="100" align="right" sortable>
          <template #default="{ row }">
            <span :class="getPnlClass(row.unrealized_pnl_rate)">
              {{ row.unrealized_pnl_rate.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleTrade(row, 'buy')">买入</el-button>
            <el-button type="danger" size="small" @click="handleTrade(row, 'sell')">卖出</el-button>
            <el-button type="info" size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && positions.length === 0" description="暂无持仓" />

      <el-pagination
        v-if="portfolioStore.total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="portfolioStore.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px"
        @size-change="handlePageChange"
        @current-change="handlePageChange"
      >
        <template #first>
          <span class="page-btn" @click="goFirst">首页</span>
        </template>
        <template #last>
          <span class="page-btn" @click="goLast">末页</span>
        </template>
      </el-pagination>
    </el-card>

    <trade-dialog
      v-model="tradeDialogVisible"
      :trade-type="tradeType"
      :stock-code="selectedStock.stock_code"
      :stock-name="selectedStock.stock_name"
      :current-price="selectedStock.current_price"
      :asset-type="selectedStock.asset_type || 'stock'"
      :available-quantity="selectedStock.available_quantity"
      @success="handleTradeSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { usePortfolioStore } from '../store/portfolio'
import { getStockRealtime } from '../api'
import PortfolioSummary from '../components/PortfolioSummary.vue'
import TradeDialog from '../components/TradeDialog.vue'

const router = useRouter()
const portfolioStore = usePortfolioStore()

const searchKeyword = ref('')
const tradeDialogVisible = ref(false)
const tradeType = ref('buy')
const currentPage = ref(1)
const pageSize = ref(20)
const selectedStock = ref({
  stock_code: '',
  stock_name: '',
  current_price: 0,
  asset_type: 'stock',
  available_quantity: 999999
})

const positions = computed(() => portfolioStore.positions)
const loading = computed(() => portfolioStore.loading)

const handlePageChange = () => {
  portfolioStore.fetchPositions(currentPage.value, pageSize.value)
}

const goFirst = () => {
  currentPage.value = 1
  portfolioStore.fetchPositions(1, pageSize.value)
}

const goLast = () => {
  currentPage.value = Math.ceil(portfolioStore.total / pageSize.value)
  portfolioStore.fetchPositions(currentPage.value, pageSize.value)
}

watch(searchKeyword, () => {
  currentPage.value = 1
  portfolioStore.fetchPositions(1, pageSize.value)
})

const filteredPositions = computed(() => {
  if (!searchKeyword.value) return positions.value
  const keyword = searchKeyword.value.toLowerCase()
  return positions.value.filter(p =>
    p.stock_code.toLowerCase().includes(keyword) ||
    p.stock_name.toLowerCase().includes(keyword)
  )
})

const formatMoney = (num) => {
  if (num == null) return '--'
  return typeof num === 'number' ? num.toFixed(2) : num
}

const getPnlClass = (value) => {
  if (value > 0) return 'pnl-positive'
  if (value < 0) return 'pnl-negative'
  return ''
}

const refreshData = () => {
  portfolioStore.refresh()
  ElMessage.success('数据已刷新')
}

const handleTrade = async (row, type) => {
  tradeType.value = type
  selectedStock.value = {
    stock_code: row.stock_code,
    stock_name: row.stock_name,
    current_price: row.current_price,
    asset_type: row.asset_type || 'stock',
    available_quantity: row.available_quantity
  }

  try {
    const res = await getStockRealtime(row.stock_code)
    if (res.code === 0) {
      selectedStock.value.current_price = res.data.current_price || row.current_price
    }
  } catch (error) {
    console.error('获取行情失败:', error)
  }

  tradeDialogVisible.value = true
}

const viewDetail = (row) => {
  router.push({ name: 'StockDetail', params: { code: row.stock_code } })
}

const handleTradeSuccess = () => {
  portfolioStore.refresh()
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

.header-actions {
  display: flex;
  align-items: center;
}

.pnl-positive {
  color: #67c23a;
}

.pnl-negative {
  color: #f56c6c;
}

.page-btn {
  cursor: pointer;
  color: var(--el-color-primary);
}
</style>