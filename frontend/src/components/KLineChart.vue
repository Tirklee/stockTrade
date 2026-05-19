<template>
  <div class="kline-container">
    <div class="control-row">
      <div class="period-btns">
        <button
          v-for="p in periods"
          :key="p"
          :class="['btn', { active: period === p }]"
          @click="period = p"
        >{{ p }}</button>
      </div>
      <div class="indicator-selector">
        <el-select v-model="subIndicator" size="small" placeholder="选择指标">
          <el-option label="成交量" value="VOL" />
          <el-option label="MACD" value="MACD" />
          <el-option label="KDJ" value="KDJ" />
          <el-option label="RSI" value="RSI" />
          <el-option label="WR" value="WR" />
          <el-option label="BIAS" value="BIAS" />
          <el-option label="ROC" value="ROC" />
          <el-option label="PSY" value="PSY" />
        </el-select>
      </div>
      <div class="chart-legend">
        <span class="legend-item"><span class="dot" style="background:#ef5350"></span>K线</span>
        <span class="legend-item"><span class="dot" style="background:#f5d74e"></span>MA5</span>
        <span class="legend-item"><span class="dot" style="background:#5ba3f5"></span>MA10</span>
        <span class="legend-item"><span class="dot" style="background:#b06ab3"></span>MA20</span>
        <span class="legend-item"><span class="dot" style="background:#f5a74e"></span>MA30</span>
        <span class="legend-item"><span class="dot" style="background:#a3f5b0"></span>MA60</span>
      </div>
    </div>

    <div class="price-info">
      <span class="index-name">{{ name }}</span>
      <span :class="['price', priceChange >= 0 ? 'up' : 'down']">{{ currentPrice.toFixed(2) }}</span>
      <span :class="['change', priceChange >= 0 ? 'up' : 'down']">
        {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
      </span>
    </div>

    <div class="charts-area">
      <div ref="mainChartRef" class="main-chart"></div>
      <div ref="subChartRef" class="sub-chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  code: { type: String, required: true },
  name: { type: String, required: true }
})

const periods = ['分时', '5日', '日线', '周线', '月线']
const period = ref('日线')
const subIndicator = ref('MACD')
const mainChartRef = ref(null)
const subChartRef = ref(null)
let mainChart = null
let subChart = null

let rawData = { dates: [], data: [] }
const currentPrice = ref(0)
const priceChange = ref(0)

const COLORS = {
  up: '#ef5350',
  down: '#26a69a',
  ma5: '#f5d74e',
  ma10: '#5ba3f5',
  ma20: '#b06ab3',
  ma30: '#f5a74e',
  ma60: '#a3f5b0',
  dif: '#30d4d4',
  dea: '#ee6161',
  k: '#f5d74e',
  d: '#5ba3f5',
  j: '#b06ab3',
  rsi6: '#f5d74e',
  rsi12: '#5ba3f5',
  rsi24: '#b06ab3'
}

const generateMockData = () => {
  const base = props.code.includes('sz399') ? 10000 : props.code.includes('bj') ? 800 : 3000
  const dates = []
  const data = []
  let count = period.value === '分时' ? 240 : period.value === '5日' ? 20 : 60

  for (let i = 0; i < count; i++) {
    if (period.value === '分时') {
      let hour, min
      if (i < 120) {
        const totalMin = 9 * 60 + 30 + i
        hour = Math.floor(totalMin / 60)
        min = totalMin % 60
      } else {
        const totalMin = 13 * 60 + (i - 120)
        hour = Math.floor(totalMin / 60)
        min = totalMin % 60
      }
      dates.push(`${hour}:${min.toString().padStart(2, '0')}`)
    } else if (period.value === '5日') {
      dates.push(`${Math.floor(i / 4) + 1}日`)
    } else {
      dates.push(`${i + 1}`)
    }

    const open = base + Math.random() * base * 0.02
    const close = open + (Math.random() - 0.48) * base * 0.015
    const high = Math.max(open, close) * (1 + Math.random() * 0.005)
    const low = Math.min(open, close) * (1 - Math.random() * 0.005)
    data.push([+open.toFixed(2), +close.toFixed(2), +low.toFixed(2), +high.toFixed(2)])
  }

  currentPrice.value = data[data.length - 1][1]
  const firstClose = data[0][1]
  priceChange.value = ((currentPrice.value - firstClose) / firstClose * 100)

  return { dates, data }
}

const calcMA = (data) => {
  const close = data.map(d => d[1])
  const result = {}
  for (const p of [5, 10, 20, 30, 60]) {
    result[`ma${p}`] = []
    for (let i = 0; i < close.length; i++) {
      if (i < p - 1) result[`ma${p}`].push('-')
      else result[`ma${p}`].push(+(close.slice(i - p + 1, i + 1).reduce((a, b) => a + b, 0) / p).toFixed(2))
    }
  }
  return result
}

const calcMACD = (data) => {
  const close = data.map(d => d[1])
  const dif = [], dea = [], macd = []
  let ema12 = close[0], ema26 = close[0]

  for (const c of close) {
    ema12 = (2 / 13) * c + (11 / 13) * ema12
    ema26 = (2 / 27) * c + (25 / 27) * ema26
    dif.push(ema12 - ema26)
  }

  let dea_val = dif[0]
  for (let i = 0; i < dif.length; i++) {
    dea_val = (2 / 10) * dif[i] + (8 / 10) * dea_val
    dea.push(dea_val)
    macd.push(2 * (dif[i] - dea_val))
  }

  return {
    dif: dif.map(v => +v.toFixed(3)),
    dea: dea.map(v => +v.toFixed(3)),
    macd: macd.map(v => +v.toFixed(3))
  }
}

const calcKDJ = (data) => {
  const high = data.map(d => d[2])
  const low = data.map(d => d[3])
  const close = data.map(d => d[1])
  const k = [], d = [], j = []
  let k_val = 50, d_val = 50

  for (let i = 0; i < close.length; i++) {
    const h = Math.max(...high.slice(Math.max(0, i - 8), i + 1))
    const l = Math.min(...low.slice(Math.max(0, i - 8), i + 1))
    const rsv = h === l ? 50 : (close[i] - l) / (h - l) * 100
    k_val = (2 / 3) * k_val + (1 / 3) * rsv
    d_val = (2 / 3) * d_val + (1 / 3) * k_val
    j.push(3 * k_val - 2 * d_val)
    k.push(+k_val.toFixed(2))
    d.push(+d_val.toFixed(2))
  }

  return { k, d, j }
}

const calcRSI = (data) => {
  const close = data.map(d => d[1])
  const result = { rsi6: [], rsi12: [], rsi24: [] }

  for (let i = 0; i < close.length; i++) {
    for (const [p, key] of [[6, 'rsi6'], [12, 'rsi12'], [24, 'rsi24']]) {
      if (i < p) {
        result[key].push('-')
      } else {
        let gains = 0, losses = 0
        for (let j = i - p + 1; j <= i; j++) {
          const change = close[j] - close[j - 1]
          if (change > 0) gains += change
          else losses -= change
        }
        const rs = losses === 0 ? 100 : gains / losses
        result[key].push(+(100 - 100 / (1 + rs)).toFixed(2))
      }
    }
  }
  return result
}

const calcWR = (data) => {
  const high = data.map(d => d[2])
  const low = data.map(d => d[3])
  const close = data.map(d => d[1])
  const wr6 = [], wr10 = []

  for (let i = 0; i < close.length; i++) {
    const h6 = Math.max(...high.slice(Math.max(0, i - 5), i + 1))
    const l6 = Math.min(...low.slice(Math.max(0, i - 5), i + 1))
    const h10 = Math.max(...high.slice(Math.max(0, i - 9), i + 1))
    const l10 = Math.min(...low.slice(Math.max(0, i - 9), i + 1))
    wr6.push(h6 === l6 ? 50 : +((h6 - close[i]) / (h6 - l6) * 100).toFixed(2))
    wr10.push(h10 === l10 ? 50 : +((h10 - close[i]) / (h10 - l10) * 100).toFixed(2))
  }
  return { wr6, wr10 }
}

const calcBIAS = (data) => {
  const close = data.map(d => d[1])
  const result = { bias6: [], bias12: [], bias24: [] }

  for (let i = 0; i < close.length; i++) {
    const ma6 = i < 5 ? 0 : close.slice(i - 5, i + 1).reduce((a, b) => a + b, 0) / 6
    const ma12 = i < 11 ? 0 : close.slice(i - 11, i + 1).reduce((a, b) => a + b, 0) / 12
    const ma24 = i < 23 ? 0 : close.slice(i - 23, i + 1).reduce((a, b) => a + b, 0) / 24
    result.bias6.push(ma6 ? +((close[i] - ma6) / ma6 * 100).toFixed(2) : '-')
    result.bias12.push(ma12 ? +((close[i] - ma12) / ma12 * 100).toFixed(2) : '-')
    result.bias24.push(ma24 ? +((close[i] - ma24) / ma24 * 100).toFixed(2) : '-')
  }
  return result
}

const calcROC = (data) => {
  const close = data.map(d => d[1])
  const roc6 = [], roc12 = []

  for (let i = 0; i < close.length; i++) {
    const prev6 = close[i - 6] || 0
    const prev12 = close[i - 12] || 0
    roc6.push(prev6 ? +((close[i] - prev6) / prev6 * 100).toFixed(2) : '-')
    roc12.push(prev12 ? +((close[i] - prev12) / prev12 * 100).toFixed(2) : '-')
  }
  return { roc6, roc12 }
}

const calcPSY = (data) => {
  const close = data.map(d => d[1])
  const psy = []

  for (let i = 0; i < close.length; i++) {
    if (i < 11) {
      psy.push('-')
    } else {
      let count = 0
      for (let j = i - 11; j <= i; j++) {
        if (close[j] > close[j - 1]) count++
      }
      psy.push(+(count / 12 * 100).toFixed(2))
    }
  }
  return { psy }
}

const initCharts = () => {
  if (mainChartRef.value) mainChart = echarts.init(mainChartRef.value)
  if (subChartRef.value) subChart = echarts.init(subChartRef.value)
}

const updateCharts = () => {
  if (!mainChart || !subChart) return

  rawData = generateMockData()
  const { dates, data } = rawData
  const ma = calcMA(data)
  const candleData = data.map(d => [d[0], d[3], d[2], d[1]])

  // 主图：K线 + MA
  mainChart.setOption({
    backgroundColor: '#fff',
    animation: false,
    grid: { left: 60, right: 15, top: 10, bottom: 30 },
    xAxis: [{
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666', fontSize: 11, interval: Math.floor(dates.length / 6) },
      splitLine: { show: false }
    }],
    yAxis: [{
      type: 'value',
      scale: true,
      position: 'left',
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666', fontSize: 11, formatter: v => v.toFixed(0) },
      splitLine: { lineStyle: { color: '#eee', type: 'dashed' } },
      splitNumber: 4
    }],
    dataZoom: [
      { type: 'inside', xAxisIndex: 0, start: 0, end: 100 },
      { type: 'slider', xAxisIndex: 0, start: 0, end: 100, height: 16, bottom: 5, borderColor: '#eee', backgroundColor: '#fafafa', fillerColor: 'rgba(100, 150, 255, 0.1)', handleStyle: { color: '#999' }, textStyle: { color: '#999', fontSize: 10 } }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: candleData,
        itemStyle: { color: COLORS.up, color0: COLORS.down, borderColor: COLORS.up, borderColor0: COLORS.down }
      },
      { name: 'MA5', type: 'line', data: ma.ma5, smooth: true, lineStyle: { width: 1.5, color: COLORS.ma5 }, symbol: 'none' },
      { name: 'MA10', type: 'line', data: ma.ma10, smooth: true, lineStyle: { width: 1.5, color: COLORS.ma10 }, symbol: 'none' },
      { name: 'MA20', type: 'line', data: ma.ma20, smooth: true, lineStyle: { width: 1.5, color: COLORS.ma20 }, symbol: 'none' },
      { name: 'MA30', type: 'line', data: ma.ma30, smooth: true, lineStyle: { width: 1.5, color: COLORS.ma30 }, symbol: 'none' },
      { name: 'MA60', type: 'line', data: ma.ma60, smooth: true, lineStyle: { width: 1.5, color: COLORS.ma60 }, symbol: 'none' }
    ]
  })

  // 副图：根据选择的指标显示
  updateSubChart(dates, data)
}

const updateSubChart = (dates, data) => {
  const macdData = calcMACD(data)
  const kdjData = calcKDJ(data)
  const rsiData = calcRSI(data)
  const wrData = calcWR(data)
  const biasData = calcBIAS(data)
  const rocData = calcROC(data)
  const psyData = calcPSY(data)

  let subOption = {}

  if (subIndicator.value === 'VOL') {
    const volData = data.map(d => ({
      value: d[1] - d[0],
      itemStyle: { color: d[1] >= d[0] ? COLORS.up : COLORS.down }
    }))
    subOption = {
      title: { text: 'VOL', left: 10, top: 5, textStyle: { fontSize: 12, color: '#666', fontWeight: 'normal' } },
      grid: { left: 60, right: 15, top: 30, bottom: 25 },
      xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { show: false }, splitLine: { show: false } }],
      yAxis: [{ type: 'value', axisLine: { show: false }, axisLabel: { show: false }, splitLine: { show: false } }],
      series: [{ name: 'VOL', type: 'bar', data: volData, barWidth: '60%' }]
    }
  } else if (subIndicator.value === 'MACD') {
    subOption = {
      title: { text: 'MACD', left: 10, top: 5, textStyle: { fontSize: 12, color: '#666', fontWeight: 'normal' } },
      grid: { left: 60, right: 15, top: 30, bottom: 25 },
      xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { show: false }, splitLine: { show: false } }],
      yAxis: [{ type: 'value', axisLine: { show: false }, axisLabel: { show: false }, splitLine: { lineStyle: { color: '#eee', type: 'dashed' } } }],
      series: [
        { name: 'DIF', type: 'line', data: macdData.dif, smooth: true, lineStyle: { width: 1.5, color: COLORS.dif }, symbol: 'none' },
        { name: 'DEA', type: 'line', data: macdData.dea, smooth: true, lineStyle: { width: 1.5, color: COLORS.dea }, symbol: 'none' },
        { name: 'MACD', type: 'bar', data: macdData.macd.map(v => ({ value: v, itemStyle: { color: v >= 0 ? COLORS.up : COLORS.down } })), barWidth: '60%' }
      ]
    }
  } else if (subIndicator.value === 'KDJ') {
    subOption = {
      title: { text: 'KDJ', left: 10, top: 5, textStyle: { fontSize: 12, color: '#666', fontWeight: 'normal' } },
      grid: { left: 60, right: 15, top: 30, bottom: 25 },
      xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { show: false }, splitLine: { show: false } }],
      yAxis: [{ type: 'value', min: 0, max: 100, axisLine: { show: false }, axisLabel: { show: false }, splitLine: { lineStyle: { color: '#eee', type: 'dashed' } } }],
      series: [
        { name: 'K', type: 'line', data: kdjData.k, smooth: true, lineStyle: { width: 1.5, color: COLORS.k }, symbol: 'none' },
        { name: 'D', type: 'line', data: kdjData.d, smooth: true, lineStyle: { width: 1.5, color: COLORS.d }, symbol: 'none' },
        { name: 'J', type: 'line', data: kdjData.j, smooth: true, lineStyle: { width: 1.5, color: COLORS.j, type: 'dashed' }, symbol: 'none' }
      ]
    }
  } else if (subIndicator.value === 'RSI') {
    subOption = {
      title: { text: 'RSI', left: 10, top: 5, textStyle: { fontSize: 12, color: '#666', fontWeight: 'normal' } },
      grid: { left: 60, right: 15, top: 30, bottom: 25 },
      xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { show: false }, splitLine: { show: false } }],
      yAxis: [{ type: 'value', min: 0, max: 100, axisLine: { show: false }, axisLabel: { show: false }, splitLine: { lineStyle: { color: '#eee', type: 'dashed' } } }],
      series: [
        { name: 'RSI6', type: 'line', data: rsiData.rsi6, smooth: true, lineStyle: { width: 1.5, color: COLORS.rsi6 }, symbol: 'none' },
        { name: 'RSI12', type: 'line', data: rsiData.rsi12, smooth: true, lineStyle: { width: 1.5, color: COLORS.rsi12 }, symbol: 'none' },
        { name: 'RSI24', type: 'line', data: rsiData.rsi24, smooth: true, lineStyle: { width: 1.5, color: COLORS.rsi24 }, symbol: 'none' }
      ]
    }
  } else if (subIndicator.value === 'WR') {
    subOption = {
      title: { text: 'WR', left: 10, top: 5, textStyle: { fontSize: 12, color: '#666', fontWeight: 'normal' } },
      grid: { left: 60, right: 15, top: 30, bottom: 25 },
      xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { show: false }, splitLine: { show: false } }],
      yAxis: [{ type: 'value', min: -20, max: 100, axisLine: { show: false }, axisLabel: { show: false }, splitLine: { lineStyle: { color: '#eee', type: 'dashed' } } }],
      series: [
        { name: 'WR6', type: 'line', data: wrData.wr6, smooth: true, lineStyle: { width: 1.5, color: '#f5a74e' }, symbol: 'none' },
        { name: 'WR10', type: 'line', data: wrData.wr10, smooth: true, lineStyle: { width: 1.5, color: '#a3f5b0' }, symbol: 'none' }
      ]
    }
  } else if (subIndicator.value === 'BIAS') {
    subOption = {
      title: { text: 'BIAS', left: 10, top: 5, textStyle: { fontSize: 12, color: '#666', fontWeight: 'normal' } },
      grid: { left: 60, right: 15, top: 30, bottom: 25 },
      xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { show: false }, splitLine: { show: false } }],
      yAxis: [{ type: 'value', axisLine: { show: false }, axisLabel: { show: false }, splitLine: { lineStyle: { color: '#eee', type: 'dashed' } } }],
      series: [
        { name: 'BIAS6', type: 'line', data: biasData.bias6, smooth: true, lineStyle: { width: 1.5, color: COLORS.rsi6 }, symbol: 'none' },
        { name: 'BIAS12', type: 'line', data: biasData.bias12, smooth: true, lineStyle: { width: 1.5, color: COLORS.rsi12 }, symbol: 'none' },
        { name: 'BIAS24', type: 'line', data: biasData.bias24, smooth: true, lineStyle: { width: 1.5, color: COLORS.rsi24 }, symbol: 'none' }
      ]
    }
  } else if (subIndicator.value === 'ROC') {
    subOption = {
      title: { text: 'ROC', left: 10, top: 5, textStyle: { fontSize: 12, color: '#666', fontWeight: 'normal' } },
      grid: { left: 60, right: 15, top: 30, bottom: 25 },
      xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { show: false }, splitLine: { show: false } }],
      yAxis: [{ type: 'value', axisLine: { show: false }, axisLabel: { show: false }, splitLine: { lineStyle: { color: '#eee', type: 'dashed' } } }],
      series: [
        { name: 'ROC6', type: 'line', data: rocData.roc6, smooth: true, lineStyle: { width: 1.5, color: COLORS.rsi6 }, symbol: 'none' },
        { name: 'ROC12', type: 'line', data: rocData.roc12, smooth: true, lineStyle: { width: 1.5, color: COLORS.rsi12 }, symbol: 'none' }
      ]
    }
  } else if (subIndicator.value === 'PSY') {
    subOption = {
      title: { text: 'PSY', left: 10, top: 5, textStyle: { fontSize: 12, color: '#666', fontWeight: 'normal' } },
      grid: { left: 60, right: 15, top: 30, bottom: 25 },
      xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { show: false }, splitLine: { show: false } }],
      yAxis: [{ type: 'value', min: 0, max: 100, axisLine: { show: false }, axisLabel: { show: false }, splitLine: { lineStyle: { color: '#eee', type: 'dashed' } } }],
      series: [
        { name: 'PSY', type: 'line', data: psyData.psy, smooth: true, lineStyle: { width: 1.5, color: '#f5a74e' }, symbol: 'none' }
      ]
    }
  }

  subChart.setOption({
    backgroundColor: '#fff',
    animation: false,
    ...subOption
  })
}

const resizeCharts = () => {
  mainChart?.resize()
  subChart?.resize()
}

onMounted(async () => {
  await nextTick()
  initCharts()
  updateCharts()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  mainChart?.dispose()
  subChart?.dispose()
})

watch([period, subIndicator], () => {
  nextTick(() => updateCharts())
})

defineExpose({ resizeCharts })
</script>

<style scoped>
.kline-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.control-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.period-btns {
  display: flex;
  gap: 4px;
}

.indicator-selector {
  margin-left: auto;
}

.chart-legend {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #666;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 16px;
  height: 3px;
  border-radius: 1px;
}

.btn {
  padding: 4px 12px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.btn.active {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.price-info {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 8px 12px;
  flex-shrink: 0;
}

.index-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.price {
  font-size: 22px;
  font-weight: bold;
}

.change {
  font-size: 14px;
}

.up { color: #ef5350; }
.down { color: #26a69a; }

.charts-area {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 0 8px 8px;
}

.main-chart {
  flex: 1;
  min-height: 0;
}

.sub-chart {
  height: 100px;
  flex-shrink: 0;
  margin-top: 8px;
}
</style>