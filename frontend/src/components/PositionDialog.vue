<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑持仓' : '新增持仓'"
    width="450px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="股票代码" prop="stock_code">
        <el-input
          v-model="form.stock_code"
          placeholder="请输入股票代码"
          :readonly="isEdit"
        />
      </el-form-item>

      <el-form-item label="股票名称" prop="stock_name">
        <el-input v-model="form.stock_name" placeholder="请输入股票名称" />
      </el-form-item>

      <el-form-item label="资产类型" prop="asset_type">
        <el-select v-model="form.asset_type" style="width: 100%">
          <el-option label="股票" value="stock" />
          <el-option label="基金" value="fund" />
        </el-select>
      </el-form-item>

      <el-form-item label="持股数" prop="total_quantity">
        <el-input-number
          v-model="form.total_quantity"
          :min="0"
          controls-position="right"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="成本价" prop="avg_cost">
        <el-input-number
          v-model="form.avg_cost"
          :min="0"
          :precision="3"
          controls-position="right"
          style="width: 100%"
        >
          <template #append>元</template>
        </el-input-number>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确认{{ isEdit ? '修改' : '新增' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createPosition, updatePosition } from '../api'

const props = defineProps({
  modelValue: Boolean,
  position: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref()
const submitting = ref(false)

const form = ref({
  stock_code: '',
  stock_name: '',
  asset_type: 'stock',
  total_quantity: 0,
  avg_cost: 0
})

const rules = {
  stock_code: [{ required: true, message: '请输入股票代码', trigger: 'blur' }],
  stock_name: [{ required: true, message: '请输入股票名称', trigger: 'blur' }],
  total_quantity: [{ required: true, message: '请输入持股数', trigger: 'blur' }],
  avg_cost: [{ required: true, message: '请输入成本价', trigger: 'blur' }]
}

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.position)

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true

  try {
    let result
    if (isEdit.value) {
      result = await updatePosition(form.value.stock_code, {
        total_quantity: form.value.total_quantity,
        avg_cost: form.value.avg_cost
      })
    } else {
      result = await createPosition(form.value)
    }

    if (result.code === 0) {
      ElMessage.success(result.message || (isEdit.value ? '修改成功' : '新增成功'))
      emit('success', result.data)
      handleClose()
    } else {
      ElMessage.error(result.message || '操作失败')
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
    if (props.position) {
      form.value = {
        stock_code: props.position.stock_code,
        stock_name: props.position.stock_name,
        asset_type: props.position.asset_type || 'stock',
        total_quantity: props.position.total_quantity,
        avg_cost: props.position.avg_cost
      }
    } else {
      form.value = {
        stock_code: '',
        stock_name: '',
        asset_type: 'stock',
        total_quantity: 0,
        avg_cost: 0
      }
    }
  }
})
</script>