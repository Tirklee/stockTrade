<template>
  <div class="broker-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>券商管理</span>
          <el-button type="primary" @click="showAddDialog">添加券商</el-button>
        </div>
      </template>

      <el-table :data="brokers" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="券商名称" width="150" />
        <el-table-column prop="description" label="描述" min-width="150" />
        <el-table-column label="买入佣金" width="120" align="right">
          <template #default="{ row }">
            万{{ row.buy_commission_rate }}
          </template>
        </el-table-column>
        <el-table-column label="卖出佣金" width="120" align="right">
          <template #default="{ row }">
            万{{ row.sell_commission_rate }}
          </template>
        </el-table-column>
        <el-table-column label="最低佣金" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.buy_min_commission }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑券商' : '添加券商'"
      width="500px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="券商名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入券商名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="买入佣金率" prop="buy_commission_rate">
          <el-input-number v-model="form.buy_commission_rate" :min="0.1" :max="10" :precision="2" />
          <span class="form-tip">（万分之一，如：1.5 表示万1.5）</span>
        </el-form-item>
        <el-form-item label="卖出佣金率" prop="sell_commission_rate">
          <el-input-number v-model="form.sell_commission_rate" :min="0.1" :max="10" :precision="2" />
        </el-form-item>
        <el-form-item label="最低佣金(买)" prop="buy_min_commission">
          <el-input-number v-model="form.buy_min_commission" :min="0" :precision="2" />
          <span class="form-tip">（元）</span>
        </el-form-item>
        <el-form-item label="最低佣金(卖)" prop="sell_min_commission">
          <el-input-number v-model="form.sell_min_commission" :min="0" :precision="2" />
          <span class="form-tip">（元）</span>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBrokers } from '../api'
import request from '../utils/request'

const brokers = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref()
const editingId = ref(null)

const form = ref({
  name: '',
  description: '',
  buy_commission_rate: 2.5,
  sell_commission_rate: 2.5,
  buy_min_commission: 5.0,
  sell_min_commission: 5.0,
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入券商名称', trigger: 'blur' }],
  buy_commission_rate: [{ required: true, message: '请输入买入佣金率', trigger: 'blur' }],
  sell_commission_rate: [{ required: true, message: '请输入卖出佣金率', trigger: 'blur' }]
}

const loadBrokers = async () => {
  loading.value = true
  try {
    const res = await getBrokers()
    if (res.code === 0) {
      brokers.value = res.data
    }
  } catch (error) {
    console.error('加载券商列表失败:', error)
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  editingId.value = null
  form.value = {
    name: '',
    description: '',
    buy_commission_rate: 2.5,
    sell_commission_rate: 2.5,
    buy_min_commission: 5.0,
    sell_min_commission: 5.0,
    is_active: true
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    const method = isEdit.value ? 'put' : 'post'
    const url = isEdit.value ? `/brokers/${editingId.value}` : '/brokers'
    const res = await request[method](url, form.value)

    if (res.code === 0) {
      ElMessage.success(isEdit.value ? '修改成功' : '添加成功')
      dialogVisible.value = false
      loadBrokers()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除券商 "${row.name}" 吗？`, '提示', {
      type: 'warning'
    })

    await request.delete(`/brokers/${row.id}`)
    ElMessage.success('删除成功')
    loadBrokers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadBrokers()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}
</style>