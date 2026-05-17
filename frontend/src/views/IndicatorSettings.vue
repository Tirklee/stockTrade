<template>
  <div class="indicator-settings">
    <el-card>
      <template #header>
        <span>指标参数设置</span>
      </template>

      <el-form :model="form" label-width="120px">
        <el-divider content-position="left">均线参数</el-divider>

        <el-form-item label="MA5">
          <el-input-number v-model="form.ma5" :min="1" :max="30" />
          <span class="form-tip">日</span>
        </el-form-item>

        <el-form-item label="MA10">
          <el-input-number v-model="form.ma10" :min="1" :max="60" />
          <span class="form-tip">日</span>
        </el-form-item>

        <el-form-item label="MA20">
          <el-input-number v-model="form.ma20" :min="1" :max="120" />
          <span class="form-tip">日</span>
        </el-form-item>

        <el-form-item label="MA30">
          <el-input-number v-model="form.ma30" :min="1" :max="250" />
          <span class="form-tip">日</span>
        </el-form-item>

        <el-form-item label="MA60">
          <el-input-number v-model="form.ma60" :min="1" :max="365" />
          <span class="form-tip">日</span>
        </el-form-item>

        <el-divider content-position="left">MACD参数</el-divider>

        <el-form-item label="快线周期">
          <el-input-number v-model="form.macd_fast" :min="5" :max="20" />
        </el-form-item>

        <el-form-item label="慢线周期">
          <el-input-number v-model="form.macd_slow" :min="15" :max="40" />
        </el-form-item>

        <el-form-item label="信号线周期">
          <el-input-number v-model="form.macd_signal" :min="5" :max="15" />
        </el-form-item>

        <el-divider content-position="left">KDJ参数</el-divider>

        <el-form-item label="K值周期">
          <el-input-number v-model="form.kdj_n" :min="3" :max="20" />
        </el-form-item>

        <el-form-item label="D值周期">
          <el-input-number v-model="form.kdj_m1" :min="3" :max="20" />
        </el-form-item>

        <el-form-item label="J值">
          <el-input-number v-model="form.kdj_m2" :min="1" :max="5" />
        </el-form-item>

        <el-divider content-position="left">布林带参数</el-divider>

        <el-form-item label="周期">
          <el-input-number v-model="form.boll_period" :min="10" :max="50" />
        </el-form-item>

        <el-form-item label="标准差倍数">
          <el-input-number v-model="form.boll_std" :min="1" :max="4" :step="0.1" :precision="1" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSave">保存设置</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const form = reactive({
  // 均线
  ma5: 5,
  ma10: 10,
  ma20: 20,
  ma30: 30,
  ma60: 60,

  // MACD
  macd_fast: 12,
  macd_slow: 26,
  macd_signal: 9,

  // KDJ
  kdj_n: 9,
  kdj_m1: 3,
  kdj_m2: 3,

  // 布林带
  boll_period: 20,
  boll_std: 2
})

const defaultForm = { ...form }

const handleSave = () => {
  localStorage.setItem('indicator_settings', JSON.stringify(form))
  ElMessage.success('设置已保存')
}

const handleReset = () => {
  Object.assign(form, defaultForm)
  localStorage.removeItem('indicator_settings')
  ElMessage.info('已重置为默认设置')
}

onMounted(() => {
  const saved = localStorage.getItem('indicator_settings')
  if (saved) {
    try {
      Object.assign(form, JSON.parse(saved))
    } catch (e) {
      console.error('加载设置失败:', e)
    }
  }
})
</script>

<style scoped>
.form-tip {
  margin-left: 10px;
  color: #909399;
}
</style>