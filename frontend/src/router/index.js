import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '总览' }
  },
  {
    path: '/positions',
    name: 'Positions',
    component: () => import('../views/Positions.vue'),
    meta: { title: '持仓管理' }
  },
  {
    path: '/stocks',
    name: 'Stocks',
    component: () => import('../views/Stocks.vue'),
    meta: { title: '股票搜索' }
  },
  {
    path: '/trades',
    name: 'Trades',
    component: () => import('../views/Trades.vue'),
    meta: { title: '交易记录' }
  },
  {
    path: '/settings/brokers',
    name: 'BrokerSettings',
    component: () => import('../views/BrokerSettings.vue'),
    meta: { title: '券商管理' }
  },
  {
    path: '/settings/indicators',
    name: 'IndicatorSettings',
    component: () => import('../views/IndicatorSettings.vue'),
    meta: { title: '指标设置' }
  },
  {
    path: '/stock/:code',
    name: 'StockDetail',
    component: () => import('../views/StockDetail.vue'),
    meta: { title: '股票详情' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router