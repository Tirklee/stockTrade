<template>
  <el-config-provider :locale="zhCn">
    <el-container class="app-container">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
        <div class="logo">
          <div v-if="!isCollapse">股票交易管理</div>
          <span v-else class="logo-icon">股</span>
        </div>

        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/">
            <el-icon><Odometer /></el-icon>
            <template #title>总览</template>
          </el-menu-item>

          <el-menu-item index="/positions">
            <el-icon><Box /></el-icon>
            <template #title>持仓管理</template>
          </el-menu-item>

          <el-menu-item index="/stocks">
            <el-icon><Search /></el-icon>
            <template #title>股票搜索</template>
          </el-menu-item>

          <el-menu-item index="/trades">
            <el-icon><List /></el-icon>
            <template #title>交易记录</template>
          </el-menu-item>

          <el-sub-menu index="/settings">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>设置</span>
            </template>
            <el-menu-item index="/settings/brokers">
              <el-icon><OfficeBuilding /></el-icon>
              <template #title>券商管理</template>
            </el-menu-item>
            <el-menu-item index="/settings/indicators">
              <el-icon><DataLine /></el-icon>
              <template #title>指标设置</template>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>

        <!-- 折叠按钮 -->
        <div class="collapse-btn" @click="toggleCollapse">
          <el-icon v-if="isCollapse"><DArrowRight /></el-icon>
          <el-icon v-else><DArrowLeft /></el-icon>
        </div>
      </el-aside>

      <el-container>
        <!-- 顶部导航 -->
        <el-header class="header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentRouteName">{{ currentRouteName }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-button :icon="Refresh" circle @click="refreshData" :loading="refreshing" />
            <el-button :icon="FullScreen" circle @click="toggleFullScreen" />
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-avatar :size="32" icon="UserFilled" />
                <span class="username">用户</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 主内容区 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Odometer, Box, Search, List, Setting, OfficeBuilding,
  DataLine, DArrowLeft, DArrowRight, Refresh, FullScreen
} from '@element-plus/icons-vue'
import { usePortfolioStore } from './store/portfolio'

const route = useRoute()
const portfolioStore = usePortfolioStore()

const isCollapse = ref(false)
const refreshing = ref(false)

const activeMenu = computed(() => route.path)

const currentRouteName = computed(() => {
  const routeNames = {
    '/': '',
    '/positions': '持仓管理',
    '/stocks': '股票搜索',
    '/trades': '交易记录',
    '/settings/brokers': '券商管理',
    '/settings/indicators': '指标设置'
  }
  return routeNames[route.path]
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const refreshData = async () => {
  refreshing.value = true
  try {
    await portfolioStore.refresh()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessage.info('退出登录')
  }
}

// 监听路由变化
watch(() => route.path, () => {
  portfolioStore.fetchSummary()
})
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.sidebar {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 2px 0 8px 0 rgba(29, 35, 41, 0.05);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 18px;
  font-weight: bold;
  background-color: #409eff;
  color: #fff;
  padding: 0 10px;
  letter-spacing: 2px;
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 10px;
}

.logo-icon {
  font-size: 20px;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background-color: transparent;
  --el-menu-bg-color: #ffffff;
  --el-menu-text-color: #303133;
  --el-menu-hover-bg-color: #ecf5ff;
  --el-menu-active-color: #409eff;
  --el-menu-hover-text-color: #409eff;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

/* 菜单项样式 */
.sidebar-menu .el-menu-item {
  height: 56px;
  line-height: 56px;
  margin: 4px 8px;
  border-radius: 8px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: #ecf5ff;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #409eff;
  color: #fff;
}

.sidebar-menu .el-menu-item.is-active .el-icon {
  color: #fff;
}

/* 子菜单样式 */
.sidebar-menu .el-sub-menu__title {
  height: 56px;
  line-height: 56px;
  margin: 4px 8px;
  border-radius: 8px;
}

.sidebar-menu .el-sub-menu__title:hover {
  background-color: #ecf5ff;
}

.collapse-btn {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  cursor: pointer;
  background-color: #fafafa;
  border-top: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.collapse-btn:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.header {
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  color: #606266;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>