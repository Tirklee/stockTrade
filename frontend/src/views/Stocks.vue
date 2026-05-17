<template>
  <div class="stocks-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>股票搜索</span>
        </div>
      </template>

      <el-autocomplete
        v-model="searchKeyword"
        :fetch-suggestions="handleSearch"
        placeholder="输入股票代码或名称搜索"
        style="width: 100%; margin-bottom: 20px"
        clearable
        :trigger-on-focus="false"
        @select="handleSelect"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #default="{ item }">
          <div class="stock-result">
            <div class="stock-info">
              <span class="stock-code">{{ item.stock_code }}</span>
              <span class="stock-name">{{ item.stock_name }}</span>
              <el-tag size="small" :type="getTypeTag(item.type)">{{ getTypeLabel(item.type) }}</el-tag>
            </div>
          </div>
        </template>
      </el-autocomplete>

      <el-empty v-if="!selectedStock" description="请输入股票代码或名称进行搜索" />

      <div v-if="selectedStock" class="stock-detail">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="股票代码">{{ selectedStock.stock_code }}</el-descriptions-item>
          <el-descriptions-item label="股票名称">{{ selectedStock.stock_name }}</el-descriptions-item>
          <el-descriptions-item label="资产类型">{{ selectedStock.asset_type === 'fund' ? '基金' : '股票' }}</el-descriptions-item>
          <el-descriptions-item label="当前价格">
            <span :class="priceClass">{{ formatPrice(selectedStock.current_price) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="涨跌幅">
            <span :class="getPnlClass(selectedStock.change_pct)">
              {{ formatChange(selectedStock.change_pct) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="今开">{{ selectedStock.open_price }}</el-descriptions-item>
          <el-descriptions-item label="最高">{{ selectedStock.high_price }}</el-descriptions-item>
          <el-descriptions-item label="最低">{{ selectedStock.low_price }}</el-descriptions-item>
          <el-descriptions-item label="成交量">{{ formatVolume(selectedStock.volume) }}</el-descriptions-item>
        </el-descriptions>

        <div class="stock-actions">
          <el-button type="primary" size="large" @click="handleTrade('buy')">买入</el-button>
          <el-button type="danger" size="large" @click="handleTrade('sell')">卖出</el-button>
          <el-button type="info" size="large" @click="viewDetail">查看详情</el-button>
        </div>
      </div>
    </el-card>

    <trade-dialog
      v-model="tradeDialogVisible"
      :trade-type="tradeType"
      :stock-code="selectedStock?.stock_code || ''"
      :stock-name="selectedStock?.stock_name || ''"
      :current-price="selectedStock?.current_price || 0"
      @success="handleTradeSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { searchStocks, getStockRealtime, identifyStockType } from '../api'
import TradeDialog from '../components/TradeDialog.vue'

const router = useRouter()

const searchKeyword = ref('')
const selectedStock = ref(null)
const tradeDialogVisible = ref(false)
const tradeType = ref('buy')

const priceClass = computed(() => {
  if (!selectedStock.value) return ''
  const change = selectedStock.value.change_pct
  if (change > 0) return 'price-up'
  if (change < 0) return 'price-down'
  return ''
})

const getPnlClass = (value) => {
  if (value > 0) return 'pnl-positive'
  if (value < 0) return 'pnl-negative'
  return ''
}

const getTypeTag = (type) => {
  const typeMap = { stock: '', fund: 'success', bond: 'warning', index: 'info' }
  return typeMap[type] || ''
}

const getTypeLabel = (type) => {
  const labelMap = { stock: '股票', fund: '基金', bond: '债券', index: '指数' }
  return labelMap[type] || type
}

const formatPrice = (price) => price != null ? price.toFixed(3) : '--'

const formatChange = (change) => {
  if (change == null) return '--'
  return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`
}

const formatVolume = (volume) => {
  if (!volume) return '--'
  if (volume >= 100000000) return `${(volume / 100000000).toFixed(2)}亿`
  if (volume >= 10000) return `${(volume / 10000).toFixed(2)}万`
  return volume.toString()
}

const handleSearch = async (query, cb) => {
  if (!query || query.length < 1) { cb([]); return }
  try {
    const res = await searchStocks(query)
    if (res.code === 0) cb(res.data)
  } catch (error) {
    console.error('搜索失败:', error)
    cb([])
  }
}

const handleSelect = async (item) => {
  selectedStock.value = { stock_code: item.stock_code, stock_name: item.stock_name }
  try {
    const [realtimeRes, typeRes] = await Promise.all([
      getStockRealtime(item.stock_code),
      identifyStockType(item.stock_code)
    ])
    if (realtimeRes.code === 0) {
      selectedStock.value = {
        ...selectedStock.value,
        ...realtimeRes.data,
        asset_type: typeRes.data?.type || 'stock'
      }
    }
  } catch (error) {
    console.error('获取股票信息失败:', error)
  }
}

const handleTrade = (type) => {
  tradeType.value = type
  tradeDialogVisible.value = true
}

const viewDetail = () => {
  if (selectedStock.value) {
    router.push({ name: 'StockDetail', params: { code: selectedStock.value.stock_code } })
  }
}

const handleTradeSuccess = () => {}
</script>

<style scoped>
.stock-result { padding: 4px 0; }
.stock-info { display: flex; align-items: center; gap: 10px; }
.stock-code { font-weight: bold; color: #409eff; }
.stock-name { color: #606266; }
.stock-detail { margin-top: 20px; }
.stock-actions { margin-top: 20px; display: flex; gap: 10px; }
.price-up { color: #f56c6c; }
.price-down { color: #67c23a; }
.pnl-positive { color: #67c23a; }
.pnl-negative { color: #f56c6c; }
</style>