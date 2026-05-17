<template>
  <el-dialog
    v-model="visible"
    :title="tradeType === 'buy' ? '买入股票' : '卖出股票'"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="股票代码">
        <el-input v-model="form.stock_code" readonly />
      </el-form-item>

      <el-form-item label="股票名称">
        <el-input v-model="form.stock_name" readonly />
      </el-form-item>

      <el-form-item label="当前价格">
        <el-input v-model="form.unit_price" readonly>
          <template #append>元</template>
        </el-input>
      </el-form-item>

      <el-form-item label="交易数量" prop="quantity">
        <el-input-number
          v-model="form.quantity"
          :min="1"
          :max="maxQuantity"
          controls-position="right"
        />
      </el-form-item>

      <el-form-item label="券商" prop="broker_id">
        <el-select v-model="form.broker_id" placeholder="选择券商" style="width: 100%">
          <el-option
            v-for="broker in brokers"
            :key="broker.id"
            :label="`${broker.name} (万${broker.buy_commission_rate})`"
            :value="broker.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="交易依据" prop="trade_basis">
        <el-input
          v-model="form.trade_basis"
          type="textarea"
          :rows="2"
          placeholder="记录买入/卖出理由，便于复盘"
        />
      </el-form-item>

      <el-divider content-position="left">费用明细</el-divider>

      <el-form-item label="成交金额">
        <span class="fee-value">¥{{ formData.amount.toFixed(2) }}</span>
      </el-form-item>

      <el-form-item label="佣金">
        <span class="fee-value">¥{{ formData.commission.toFixed(2) }}</span>
      </el-form-item>

      <el-form-item v-if="tradeType === 'sell'" label="印花税">
        <span class="fee-value">¥{{ formData.stamp_tax.toFixed(2) }}</span>
      </el-form-item>

      <el-form-item label="费用合计">
        <span class="fee-value total-fee">¥{{ formData.total_fee.toFixed(2) }}</span>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确认{{ tradeType === 'buy' ? '买入' : '卖出' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getBrokers, calculateFee } from '../api'
import { useTradeStore } from '../store/trade'
import { usePortfolioStore } from '../store/portfolio'

const props = defineProps({
  modelValue: Boolean,
  tradeType: {
    type: String,
    default: 'buy'
  },
  stockCode: String,
  stockName: String,
  currentPrice: Number,
  assetType: {
    type: String,
    default: 'stock'
  },
  availableQuantity: {
    type: Number,
    default: 999999
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref()
const brokers = ref([])
const submitting = ref(false)
const form = ref({
  stock_code: '',
  stock_name: '',
  unit_price: 0,
  quantity: 100,
  broker_id: null,
  trade_basis: ''
})

const rules = {
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  broker_id: [{ required: true, message: '请选择券商', trigger: 'change' }],
  trade_basis: [{ required: true, message: '请填写交易依据', trigger: 'blur' }]
}

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const maxQuantity = computed(() => {
  return props.tradeType === 'sell' ? props.availableQuantity : 999999
})

const formData = ref({
  amount: 0,
  commission: 0,
  stamp_tax: 0,
  transfer_fee: 0,
  total_fee: 0
})

const tradeStore = useTradeStore()
const portfolioStore = usePortfolioStore()

const loadBrokers = async () => {
  try {
    const res = await getBrokers()
    if (res.code === 0) {
      brokers.value = res.data
      if (brokers.value.length > 0) {
        form.value.broker_id = brokers.value[0].id
      }
    }
  } catch (error) {
    console.error('加载券商失败:', error)
  }
}

const calculateTradeFee = async () => {
  if (!form.value.quantity || !form.value.unit_price || !form.value.broker_id) {
    return
  }

  try {
    const res = await calculateFee({
      quantity: form.value.quantity,
      unit_price: form.value.unit_price,
      trade_type: props.tradeType,
      broker_id: form.value.broker_id
    })

    if (res.code === 0) {
      formData.value = res.data
    }
  } catch (error) {
    console.error('计算费用失败:', error)
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true

  try {
    const data = {
      stock_code: form.value.stock_code,
      stock_name: form.value.stock_name,
      asset_type: props.assetType,
      quantity: form.value.quantity,
      unit_price: form.value.unit_price,
      broker_id: form.value.broker_id,
      trade_basis: form.value.trade_basis
    }

    const result = props.tradeType === 'buy'
      ? await tradeStore.executeBuy(data)
      : await tradeStore.executeSell(data)

    if (result.success) {
      ElMessage.success(result.data?.message || '交易成功')
      emit('success', result.data)
      handleClose()
      portfolioStore.refresh()
    } else {
      ElMessage.error(result.message || '交易失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
  formRef.value?.resetFields()
}

watch(() => props.modelValue, (val) => {
  if (val) {
    form.value.stock_code = props.stockCode
    form.value.stock_name = props.stockName
    form.value.unit_price = props.currentPrice
    loadBrokers()
  }
})

watch(() => [form.value.quantity, form.value.broker_id], () => {
  if (form.value.quantity && form.value.unit_price && form.value.broker_id) {
    calculateTradeFee()
  }
})
</script>

<style scoped>
.fee-value {
  font-weight: bold;
  color: #409eff;
}

.total-fee {
  color: #f56c6c;
  font-size: 16px;
}
</style>