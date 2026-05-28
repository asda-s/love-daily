<template>
  <view class="bill-monthly-page">
    <view class="summary-header">
      <text class="summary-title">{{ year }}年{{ month }}月账单统计</text>
    </view>
    <view class="summary-card" v-if="summary">
      <view class="total-section">
        <text class="total-label">本月总支出</text>
        <text class="total-value">¥{{ summary.total }}</text>
      </view>
      <view class="detail-row">
        <view class="detail-item">
          <text class="detail-label">我的</text>
          <text class="detail-value">¥{{ summary.my_total }}</text>
        </view>
        <view class="detail-item">
          <text class="detail-label">TA的</text>
          <text class="detail-value">¥{{ summary.lover_total }}</text>
        </view>
      </view>
    </view>

    <view class="type-breakdown" v-if="summary && summary.type_totals">
      <view class="section-title">分类统计</view>
      <view class="type-item" v-for="(amount, type) in summary.type_totals" :key="type">
        <view class="type-left">
          <text class="type-name">{{ typeNames[type] || type }}</text>
          <view class="type-bar">
            <view class="type-bar-fill" :style="{ width: (amount / summary.total * 100) + '%' }"></view>
          </view>
        </view>
        <text class="type-amount">¥{{ amount.toFixed(2) }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'

const typeNames = { food: '餐饮', travel: '旅行', gift: '礼物', daily: '日常', other: '其他' }
const summary = ref(null)
const year = ref(new Date().getFullYear())
const month = ref(new Date().getMonth() + 1)

onMounted(async () => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1]
  if (page.options.year) year.value = parseInt(page.options.year)
  if (page.options.month) month.value = parseInt(page.options.month)

  try {
    const res = await get('/interact/bill/monthly-summary', { year: year.value, month: month.value })
    if (res && res.data) summary.value = res.data
  } catch (e) {
    console.error('加载月度统计失败', e)
  }
})
</script>

<style scoped>
.bill-monthly-page { background: transparent; min-height: 100vh; }
.summary-header { background: linear-gradient(135deg, #FF69B4, #FF8FB1); padding: 40rpx; text-align: center; }
.summary-title { color: #fff; font-size: 30rpx; }
.summary-card { background: #fff; margin: 20rpx; border-radius: 16rpx; padding: 30rpx; }
.total-section { text-align: center; margin-bottom: 30rpx; }
.total-label { font-size: 26rpx; color: #999; display: block; margin-bottom: 10rpx; }
.total-value { font-size: 56rpx; font-weight: bold; color: #FF69B4; }
.detail-row { display: flex; }
.detail-item { flex: 1; text-align: center; padding: 20rpx 0; background: #FFF5F9; border-radius: 12rpx; margin: 0 10rpx; }
.detail-label { font-size: 24rpx; color: #999; display: block; }
.detail-value { font-size: 30rpx; font-weight: bold; }
.type-breakdown { background: #fff; margin: 20rpx; border-radius: 16rpx; padding: 30rpx; }
.section-title { font-size: 28rpx; font-weight: bold; margin-bottom: 20rpx; }
.type-item { display: flex; align-items: center; justify-content: space-between; padding: 16rpx 0; }
.type-left { flex: 1; margin-right: 20rpx; }
.type-name { font-size: 26rpx; color: #666; margin-bottom: 8rpx; display: block; }
.type-bar { height: 12rpx; background: #f0f0f0; border-radius: 6rpx; overflow: hidden; }
.type-bar-fill { height: 100%; background: #FF69B4; border-radius: 6rpx; }
.type-amount { font-size: 28rpx; font-weight: bold; color: #333; }
</style>
