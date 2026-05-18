<template>
  <view class="bill-page">
    <view class="month-header">
      <view class="nav-btn" @click="prevMonth">‹</view>
      <text class="month-title">{{ currentYear }}年{{ currentMonth }}月</text>
      <view class="nav-btn" @click="nextMonth">›</view>
    </view>

    <view class="summary-card" v-if="summary">
      <view class="summary-row">
        <view class="summary-item">
          <text class="summary-label">我的支出</text>
          <text class="summary-value">¥{{ summary.my_total }}</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">TA的支出</text>
          <text class="summary-value">¥{{ summary.lover_total }}</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">总计</text>
          <text class="summary-value highlight">¥{{ summary.total }}</text>
        </view>
      </view>
    </view>

    <scroll-view class="bill-list" scroll-y refresher-enabled :refresher-triggered="refreshing" @refresherrefresh="onRefresh">
      <view class="bill-item" v-for="b in bills" :key="b.id">
        <view class="bill-left">
          <text class="bill-type-tag">{{ typeNames[b.type] || b.type }}</text>
          <view class="bill-info">
            <text class="bill-payer">{{ b.nickname }}</text>
            <text class="bill-note" v-if="b.note">{{ b.note }}</text>
          </view>
        </view>
        <view class="bill-right">
          <text class="bill-amount">¥{{ b.amount }}</text>
          <text class="bill-date">{{ b.pay_time }}</text>
          <text class="bill-delete" @click="deleteBill(b)">删除</text>
        </view>
      </view>
      <view class="empty" v-if="!bills.length">
        <text class="empty-icon">🧾</text>
        <text class="empty-text">还没有账单记录</text>
        <text class="empty-hint">点击"记一笔"开始记录你们的共同花销</text>
      </view>
    </scroll-view>

    <view class="bottom-btns">
      <view class="btn" @click="goAdd">+ 记一笔</view>
      <view class="btn secondary" @click="goMonthly">月度统计</view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, del } from '@/utils/request'

const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth() + 1)
const bills = ref([])
const refreshing = ref(false)
const summary = ref(null)
const typeNames = { food: '餐饮', travel: '旅行', gift: '礼物', daily: '日常', other: '其他' }

onMounted(() => { loadData() })

const loadData = async () => {
  try {
    const params = { year: currentYear.value, month: currentMonth.value }
    const [bRes, sRes] = await Promise.all([
      get('/interact/bill', params),
      get('/interact/bill/monthly-summary', params)
    ])
    if (bRes && bRes.data) bills.value = bRes.data
    if (sRes && sRes.data) summary.value = sRes.data
  } catch (e) {}
}

const prevMonth = () => {
  if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value-- }
  else currentMonth.value--
  loadData()
}

const nextMonth = () => {
  if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++ }
  else currentMonth.value++
  loadData()
}

const goAdd = () => uni.navigateTo({ url: '/pages/interact/bill-add' })
const goMonthly = () => uni.navigateTo({ url: `/pages/interact/bill-monthly?year=${currentYear.value}&month=${currentMonth.value}` })

async function onRefresh() {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

function deleteBill(item) {
  uni.showModal({
    title: '确认删除',
    content: '确定删除该账单？',
    confirmColor: '#e43d33',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del('/interact/bill/' + item.id)
          await loadData()
        } catch (e) {}
      }
    }
  })
}
</script>

<style scoped>
.bill-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 140rpx; }
.month-header { display: flex; align-items: center; justify-content: center; gap: 30rpx; padding: 24rpx; background: #fff; }
.nav-btn { font-size: 40rpx; color: #FF6B9D; padding: 10rpx 20rpx; }
.month-title { font-size: 32rpx; font-weight: bold; }
.summary-card { background: #fff; margin: 20rpx; border-radius: 16rpx; padding: 30rpx; }
.summary-row { display: flex; }
.summary-item { flex: 1; text-align: center; }
.summary-label { font-size: 24rpx; color: #999; display: block; margin-bottom: 8rpx; }
.summary-value { font-size: 30rpx; font-weight: bold; }
.summary-value.highlight { color: #FF6B9D; }
.bill-list { padding: 0 20rpx; height: calc(100vh - 340rpx); }
.bill-item { display: flex; justify-content: space-between; align-items: center; background: #fff; border-radius: 12rpx; padding: 24rpx; margin-bottom: 12rpx; }
.bill-left { display: flex; align-items: center; gap: 16rpx; }
.bill-type-tag { background: #f0f0f0; padding: 6rpx 14rpx; border-radius: 8rpx; font-size: 22rpx; color: #666; }
.bill-payer { font-size: 26rpx; display: block; }
.bill-note { font-size: 22rpx; color: #999; }
.bill-amount { font-size: 30rpx; font-weight: bold; color: #FF6B9D; display: block; text-align: right; }
.bill-date { font-size: 22rpx; color: #999; }
.bill-delete { font-size: 22rpx; color: #ff4d4f; margin-top: 8rpx; display: block; text-align: right; }
.empty { text-align: center; padding: 80rpx 40rpx; color: #999; }
.empty-icon { font-size: 80rpx; display: block; margin-bottom: 20rpx; }
.empty-text { font-size: 30rpx; color: #666; display: block; margin-bottom: 12rpx; }
.empty-hint { font-size: 24rpx; color: #bbb; display: block; }
.bottom-btns { position: fixed; bottom: 110rpx; left: 0; right: 0; display: flex; gap: 16rpx; padding: 20rpx; background: #fff; z-index: 100; }
.btn { flex: 1; text-align: center; padding: 24rpx; background: #FF6B9D; color: #fff; border-radius: 40rpx; font-size: 28rpx; }
.btn.secondary { background: #f5f5f5; color: #666; }
</style>
