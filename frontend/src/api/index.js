import request from '../utils/request'

// 组合总览
export function getPortfolioSummary() {
  return request.get('/portfolio/summary')
}

// 持仓管理
export function getPositions(params) {
  return request.get('/positions', { params })
}

export function getPosition(code) {
  return request.get(`/positions/${code}`)
}

export function getPositionCostDetail(code) {
  return request.get(`/positions/${code}/cost-detail`)
}

export function createPosition(data) {
  return request.post('/positions', data)
}

export function updatePosition(code, data) {
  return request.put(`/positions/${code}`, data)
}

export function deletePosition(code) {
  return request.delete(`/positions/${code}`)
}

// 交易管理
export function buyStock(data) {
  return request.post('/trades/buy', data)
}

export function sellStock(data) {
  return request.post('/trades/sell', data)
}

export function getTrades(params) {
  return request.get('/trades', { params })
}

export function getRealizedPnl(code) {
  return request.get(`/trades/${code}/realized-pnl`)
}

// 券商管理
export function getBrokers() {
  return request.get('/brokers')
}

export function getBrokerCommission(brokerId, type) {
  return request.get(`/brokers/${brokerId}/commission`, { params: { type } })
}

// 股票行情
export function searchStocks(name) {
  return request.get('/stocks/search', { params: { name } })
}

export function getStockRealtime(code) {
  return request.get(`/stocks/${code}/realtime`)
}

export function getStockKline(code, params) {
  return request.get(`/stocks/${code}/kline`, { params })
}

export function identifyStockType(code) {
  return request.get(`/stocks/${code}/identify`)
}

// 费用计算
export function calculateFee(data) {
  return request.post('/calculator/fee', data)
}

// 财经新闻
export function getFinancialNews(params) {
  return request.get('/news', { params })
}

export function getImportantEvents() {
  return request.get('/news/important-events')
}