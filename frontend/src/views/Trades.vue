<template>
  <div class="trades-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交易记录</span>
          <div class="header-actions">
            <el-select v-model="filterTradeType" placeholder="交易类型" style="width: 120px; margin-right: 10px" clearable>
              <el-option label="全部" value="" />
              <el-option label="买入" value="buy" />
              <el-option label="卖出" value="sell" />
            </el-select>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px; margin-right: 10px"
            />
            <el-button type="primary" @click="loadTrades">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="trades" v-loading="loading" stripe border>
        <el-table-column prop="trade_time" label="交易时间" width="100" sortable>
          <template #default="{ row }">
            {{ formatDate(row.trade_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="stock_code" label="代码" width="100" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            {{ row.asset_type === 'fund' ? '基金' : '股票' }}
          </template>
        </el-table-column>
        <el-table-column label="方向" width="80">
          <template #default="{ row }">
            <el-tag :type="row.trade_type === 'buy' ? 'success' : 'danger'" size="small">
              {{ row.trade_type === 'buy' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" align="right" />
        <el-table-column prop="unit_price" label="单价" width="100" align="right">
          <template #default="{ row }">
            {{ row.unit_price.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column label="成交额" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="佣金" width="80" align="right">
          <template #default="{ row }">
            {{ row.commission.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="印花税" width="80" align="right">
          <template #default="{ row }">
            {{ (row.stamp_tax || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="费用合计" width="100" align="right">
          <template #default="{ row }">
            {{ row.total_fee.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="broker_name" label="券商" width="100" />
        <el-table-column prop="trade_basis" label="交易依据" min-width="150" show-overflow-tooltip />
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px"
        @size-change="loadTrades"
        @current-change="loadTrades"
      >
        <template #first>
          <span class="page-btn" @click="goFirst">首页</span>
        </template>
        <template #last>
          <span class="page-btn" @click="goLast">末页</span>
        </template>
      </el-pagination>

      <el-empty v-if="!loading && trades.length === 0" description="暂无交易记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getTrades } from '../api'

const trades = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterTradeType = ref('')
const dateRange = ref([])

const goFirst = () => {
  currentPage.value = 1
  loadTrades()
}

const goLast = () => {
  currentPage.value = Math.ceil(total.value / pageSize.value)
  loadTrades()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  return dateStr.split('T')[0]
}

const formatMoney = (num) => {
  if (num == null) return '--'
  return typeof num === 'number' ? num.toFixed(2) : num
}

const loadTrades = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }

    if (filterTradeType.value) {
      params.trade_type = filterTradeType.value
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }

    const res = await getTrades(params)
    if (res.code === 0) {
      trades.value = res.data.data || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载交易记录失败:', error)
  } finally {
    loading.value = false
  }
}

watch([filterTradeType, dateRange], () => {
  currentPage.value = 1
  loadTrades()
})

onMounted(() => {
  loadTrades()
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

.page-btn {
  cursor: pointer;
  color: var(--el-color-primary);
}
</style>