<template>
  <div class="dashboard-page">
    <portfolio-summary v-if="!simpleMode" />

    <el-row :gutter="20" class="mt-20">
      <el-col :span="simpleMode ? 24 : 16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速交易</span>
            </div>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form label-width="80px">
                <el-form-item label="股票代码">
                  <el-input v-model="stockCode" placeholder="请输入股票代码" />
                </el-form-item>
                <el-form-item label="股票名称">
                  <el-input v-model="stockName" placeholder="请输入股票名称" />
                </el-form-item>
              </el-form>
            </el-col>
            <el-col :span="12">
              <el-button type="primary" @click="quickBuy">快速买入</el-button>
              <el-button type="danger" @click="quickSell">快速卖出</el-button>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="simpleMode ? 24 : 8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
              <el-button type="primary" @click="toggleSimpleMode">
                {{ simpleMode ? '显示完整版' : '显示简化版' }}
              </el-button>
            </div>
          </template>

          <div v-if="simpleMode">
            <el-button type="primary" @click="quickBuy" style="width: 100%; margin-bottom: 10px;">快速买入</el-button>
            <el-button type="danger" @click="quickSell" style="width: 100%">快速卖出</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import PortfolioSummary from '../components/PortfolioSummary.vue'

const simpleMode = ref(false)
const stockCode = ref('')
const stockName = ref('')

const toggleSimpleMode = () => {
  simpleMode.value = !simpleMode.value
}

const quickBuy = () => {
  ElMessage.info('买入功能')
}

const quickSell = () => {
  ElMessage.info('卖出功能')
}
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
</style>