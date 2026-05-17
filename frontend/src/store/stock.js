import { defineStore } from 'pinia'
import { searchStocks, getStockRealtime, getStockKline, identifyStockType } from '../api'

export const useStockStore = defineStore('stock', {
  state: () => ({
    searchResults: [],
    realtimeData: null,
    klineData: [],
    loading: false
  }),

  actions: {
    async search(name) {
      if (!name || name.length < 1) {
        this.searchResults = []
        return
      }
      try {
        const res = await searchStocks(name)
        if (res.code === 0) {
          this.searchResults = res.data
        }
      } catch (error) {
        console.error('搜索失败:', error)
      }
    },

    async fetchRealtime(code) {
      this.loading = true
      try {
        const res = await getStockRealtime(code)
        if (res.code === 0) {
          this.realtimeData = res.data
        }
      } catch (error) {
        console.error('获取行情失败:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchKline(code, period = 'daily') {
      try {
        const res = await getStockKline(code, { period })
        if (res.code === 0) {
          this.klineData = res.data.data
        }
      } catch (error) {
        console.error('获取K线失败:', error)
      }
    },

    async identifyType(code) {
      try {
        const res = await identifyStockType(code)
        return res.code === 0 ? res.data : null
      } catch (error) {
        return null
      }
    },

    clearRealtime() {
      this.realtimeData = null
      this.klineData = []
    }
  }
})