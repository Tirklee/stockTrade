import { defineStore } from 'pinia'
import { getPortfolioSummary, getPositions } from '../api'

export const usePortfolioStore = defineStore('portfolio', {
  state: () => ({
    summary: {
      total_market_value: 0,
      total_cost: 0,
      total_pnl: 0,
      pnl_rate: 0,
      stock_count: 0
    },
    positions: [],
    loading: false
  }),

  getters: {
    isProfit: (state) => state.summary.total_pnl >= 0
  },

  actions: {
    async fetchSummary() {
      try {
        const res = await getPortfolioSummary()
        if (res.code === 0) {
          this.summary = res.data
        }
      } catch (error) {
        console.error('获取总览失败:', error)
      }
    },

    async fetchPositions() {
      this.loading = true
      try {
        const res = await getPositions()
        if (res.code === 0) {
          this.positions = res.data
        }
      } catch (error) {
        console.error('获取持仓失败:', error)
      } finally {
        this.loading = false
      }
    },

    async refresh() {
      await Promise.all([this.fetchSummary(), this.fetchPositions()])
    }
  }
})