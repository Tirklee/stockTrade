import { defineStore } from 'pinia'
import { buyStock, sellStock } from '../api'

export const useTradeStore = defineStore('trade', {
  state: () => ({
    brokers: [],
    submitting: false,
    lastTrade: null
  }),

  actions: {
    async executeBuy(data) {
      this.submitting = true
      try {
        const res = await buyStock(data)
        if (res.code === 0) {
          this.lastTrade = res.data
          return { success: true, data: res.data }
        }
        return { success: false, message: res.message }
      } catch (error) {
        return { success: false, message: error.message }
      } finally {
        this.submitting = false
      }
    },

    async executeSell(data) {
      this.submitting = true
      try {
        const res = await sellStock(data)
        if (res.code === 0) {
          this.lastTrade = res.data
          return { success: true, data: res.data }
        }
        return { success: false, message: res.message }
      } catch (error) {
        return { success: false, message: error.message }
      } finally {
        this.submitting = false
      }
    }
  }
})