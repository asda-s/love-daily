<template>
  <view class="stats-page">
    <view class="month-header">
      <view class="nav-btn" @click="prevMonth">‹</view>
      <text class="month-title">{{ year }}年{{ month }}月情绪报告</text>
      <view class="nav-btn" @click="nextMonth">›</view>
    </view>

    <view v-if="stats" class="stats-content">
      <!-- 概览卡片 -->
      <view class="overview-card">
        <view class="overview-item">
          <text class="overview-num">{{ stats.my_count || 0 }}</text>
          <text class="overview-label">我的情绪</text>
        </view>
        <view class="overview-divider"></view>
        <view class="overview-item">
          <text class="overview-num">{{ stats.lover_count || 0 }}</text>
          <text class="overview-label">TA的情绪</text>
        </view>
      </view>

      <!-- 我的情绪分布 -->
      <view class="section-card" v-if="Object.keys(stats.my_distribution || {}).length > 0">
        <text class="section-title">我的情绪分布</text>
        <view class="dist-list">
          <view v-for="(count, name) in stats.my_distribution" :key="name" class="dist-item">
            <view class="dist-bar-wrap">
              <view class="dist-bar" :style="{ width: getBarWidth(count, stats.my_count), background: getColor(name) }"></view>
            </view>
            <text class="dist-name">{{ name }}</text>
            <text class="dist-count">{{ count }}次</text>
          </view>
        </view>
      </view>

      <!-- TA的情绪分布 -->
      <view class="section-card" v-if="Object.keys(stats.lover_distribution || {}).length > 0">
        <text class="section-title">TA的情绪分布</text>
        <view class="dist-list">
          <view v-for="(count, name) in stats.lover_distribution" :key="name" class="dist-item">
            <view class="dist-bar-wrap">
              <view class="dist-bar" :style="{ width: getBarWidth(count, stats.lover_count), background: getColor(name) }"></view>
            </view>
            <text class="dist-name">{{ name }}</text>
            <text class="dist-count">{{ count }}次</text>
          </view>
        </view>
      </view>

      <!-- 每日趋势 -->
      <view class="section-card" v-if="Object.keys(stats.daily_trend || {}).length > 0">
        <text class="section-title">每日情绪趋势</text>
        <view class="trend-list">
          <view v-for="(items, day) in stats.daily_trend" :key="day" class="trend-day">
            <text class="trend-date">{{ day }}</text>
            <view class="trend-emojis">
              <text v-for="(item, idx) in items" :key="idx" class="trend-emoji">
                {{ getEmotionEmoji(item.emotion_type) }}
              </text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view v-if="!stats || (stats.my_count === 0 && stats.lover_count === 0)" class="empty">
      <text class="empty-icon">🫧</text>
      <text class="empty-text">本月还没有情绪记录</text>
      <text class="empty-hint">切换月份或去情绪树洞记录心情</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { get } from '@/utils/request'

const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const stats = ref(null)

onLoad(() => {
  loadStats()
})

async function loadStats() {
  try {
    const res = await get('/interact/emotion/monthly-stats', {
      year: year.value,
      month: month.value
    })
    if (res && res.data) stats.value = res.data
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

function prevMonth() {
  if (month.value === 1) { month.value = 12; year.value-- }
  else month.value--
  loadStats()
}

function nextMonth() {
  if (month.value === 12) { month.value = 1; year.value++ }
  else month.value++
  loadStats()
}

function getBarWidth(count, total) {
  if (!total) return '0%'
  return Math.round((count / total) * 100) + '%'
}

const colorMap = {
  '开心': '#FFD700', '难过': '#6495ED', '生气': '#FF6347',
  '委屈': '#DDA0DD', '焦虑': '#FFA500'
}

function getColor(name) {
  return colorMap[name] || '#FF69B4'
}

const emojiMap = { happy: '😊', sad: '😢', angry: '😠', wronged: '🥺', anxious: '😰' }

function getEmotionEmoji(type) {
  return emojiMap[type] || '😶'
}
</script>

<style scoped>
.stats-page { background: #FFF5F9; min-height: 100vh; padding-bottom: 40rpx; }
.month-header { display: flex; align-items: center; justify-content: center; gap: 30rpx; padding: 24rpx; background: #fff; }
.nav-btn { font-size: 40rpx; color: #FF69B4; padding: 10rpx 20rpx; }
.month-title { font-size: 30rpx; font-weight: bold; }

.stats-content { padding: 20rpx; }

.overview-card { display: flex; background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 20rpx; }
.overview-item { flex: 1; text-align: center; }
.overview-num { display: block; font-size: 44rpx; font-weight: bold; color: #FF69B4; }
.overview-label { font-size: 24rpx; color: #999; }
.overview-divider { width: 1rpx; background: #f0f0f0; }

.section-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 20rpx; }
.section-title { display: block; font-size: 28rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }

.dist-list {}
.dist-item { display: flex; align-items: center; gap: 12rpx; margin-bottom: 16rpx; }
.dist-bar-wrap { flex: 1; height: 24rpx; background: #f5f5f5; border-radius: 12rpx; overflow: hidden; }
.dist-bar { height: 100%; border-radius: 12rpx; transition: width 0.3s; }
.dist-name { font-size: 24rpx; color: #666; width: 60rpx; }
.dist-count { font-size: 22rpx; color: #999; width: 60rpx; text-align: right; }

.trend-list {}
.trend-day { display: flex; align-items: center; padding: 12rpx 0; border-bottom: 1rpx solid #f8f8f8; }
.trend-day:last-child { border-bottom: none; }
.trend-date { font-size: 24rpx; color: #999; width: 80rpx; }
.trend-emojis { display: flex; gap: 8rpx; flex: 1; }
.trend-emoji { font-size: 32rpx; }

.empty { text-align: center; padding: 120rpx 40rpx; color: #999; }
.empty-icon { font-size: 80rpx; display: block; margin-bottom: 20rpx; }
.empty-text { font-size: 30rpx; color: #666; display: block; margin-bottom: 12rpx; }
.empty-hint { font-size: 24rpx; color: #bbb; display: block; }
</style>
