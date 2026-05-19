<template>
  <div class="dashboard-page">
    <portfolio-summary v-if="!simpleMode" />

    <el-row :gutter="12" class="main-content" v-loading="loading">
      <!-- 左侧：指数K线图 -->
      <el-col :span="14">
        <el-tabs v-model="activeIndex" class="index-tabs">
          <el-tab-pane label="上证指数" name="sh000001" :lazy="false">
            <KLineChart ref="klineSh" code="sh000001" name="上证指数" />
          </el-tab-pane>
          <el-tab-pane label="深证成指" name="sz399001" :lazy="false">
            <KLineChart ref="klineSz" code="sz399001" name="深证成指" />
          </el-tab-pane>
          <el-tab-pane label="创业板指" name="sz399006" :lazy="false">
            <KLineChart ref="klineCy" code="sz399006" name="创业板指" />
          </el-tab-pane>
          <el-tab-pane label="科创50" name="sh000688" :lazy="false">
            <KLineChart ref="klineKc50" code="sh000688" name="科创50" />
          </el-tab-pane>
          <el-tab-pane label="北证50" name="bj899050" :lazy="false">
            <KLineChart ref="klineBz50" code="bj899050" name="北证50" />
          </el-tab-pane>
          <el-tab-pane label="科创综指" name="sh000695" :lazy="false">
            <KLineChart ref="klineKczz" code="sh000695" name="科创综指" />
          </el-tab-pane>
          <el-tab-pane label="中证500" name="sh000905" :lazy="false">
            <KLineChart ref="klineZz500" code="sh000905" name="中证500" />
          </el-tab-pane>
        </el-tabs>
      </el-col>

      <!-- 右侧：财经要闻 -->
      <el-col :span="10">
        <div class="news-panel">
          <div class="news-header">
            <h3>财经要闻</h3>
            <el-radio-group v-model="newsType" size="small" @change="fetchNews">
              <el-radio-button label="news">新闻</el-radio-button>
              <el-radio-button label="policy">政策</el-radio-button>
              <el-radio-button label="economic">经济数据</el-radio-button>
            </el-radio-group>
          </div>
          <div class="news-list" ref="newsListRef">
            <div v-if="newsList.length === 0 && !loading" class="news-empty">
              暂无数据
            </div>
            <div
              v-for="(item, index) in newsList"
              :key="index"
              class="news-item"
              @click="openNews(item.url)"
            >
              <div class="news-title">{{ item.title }}</div>
              <div class="news-meta">
                <span class="news-source" v-if="item.source">{{ item.source }}</span>
                <span class="news-date">{{ item.date }}</span>
              </div>
            </div>
            <div v-if="loading" class="news-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import PortfolioSummary from '../components/PortfolioSummary.vue'
import KLineChart from '../components/KLineChart.vue'
import { getFinancialNews } from '../api'

const simpleMode = ref(false)
const activeIndex = ref('sh000001')
const klineSh = ref(null)
const klineSz = ref(null)
const klineCy = ref(null)
const klineKc50 = ref(null)
const klineBz50 = ref(null)
const klineKczz = ref(null)
const klineZz500 = ref(null)
const newsType = ref('news')
const newsList = ref([])
const loading = ref(false)
const newsListRef = ref(null)

const resizeCharts = () => {
  klineSh.value?.resizeCharts?.()
  klineSz.value?.resizeCharts?.()
  klineCy.value?.resizeCharts?.()
  klineKc50.value?.resizeCharts?.()
  klineBz50.value?.resizeCharts?.()
  klineKczz.value?.resizeCharts?.()
  klineZz500.value?.resizeCharts?.()
}

const initCharts = () => {
  nextTick(() => {
    setTimeout(() => resizeCharts(), 100)
  })
}

const fetchNews = async () => {
  loading.value = true
  try {
    const res = await getFinancialNews({ type: newsType.value, page_size: 20 })
    if (res.code === 0) {
      newsList.value = res.data || []
    } else {
      newsList.value = []
    }
  } catch (error) {
    console.error('获取新闻失败:', error)
    newsList.value = []
  } finally {
    loading.value = false
  }
}

const openNews = (url) => {
  if (url && url !== '#') {
    window.open(url, '_blank')
  }
}

watch(activeIndex, () => {
  initCharts()
})

onMounted(() => {
  initCharts()
  fetchNews()
})
</script>

<style scoped>
.dashboard-page {
  padding: 8px;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.main-content {
  margin-top: 8px;
  flex: 1;
  min-height: 0;
}

.index-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.index-tabs :deep(.el-tabs__content) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.index-tabs :deep(.el-tab-pane) {
  height: 100%;
}

.news-panel {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.news-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.news-list {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
}

.news-item {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.news-item:hover {
  background: #f5f7fa;
  padding-left: 8px;
  border-radius: 4px;
}

.news-item:last-child {
  border-bottom: none;
}

.news-title {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.news-source {
  color: #409eff;
}

.news-empty {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}

.news-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #909399;
  padding: 20px 0;
}
</style>