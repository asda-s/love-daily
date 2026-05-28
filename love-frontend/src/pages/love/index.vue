<template>
  <view class="love-page">
    <view class="level-card">
      <view class="level-header">
        <text class="level-badge">Lv.{{ overview.level || 1 }}</text>
        <text class="level-name">{{ levelName }}</text>
      </view>
      <view class="level-progress">
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: levelProgress + '%' }"></view>
        </view>
        <view class="progress-info">
          <text class="progress-current">{{ overview.heart_points || 0 }} 心动分</text>
          <text class="progress-next">下一级 {{ nextLevelPoints }} 分</text>
        </view>
      </view>
      <text class="level-hint">距下一级还需 {{ Math.max(0, nextLevelPoints - (overview.heart_points || 0)) }} 分</text>
      <text class="level-unlock">下一级解锁：{{ nextLevelBenefit }}</text>
    </view>

    <view class="section">
      <text class="section-title">功能入口</text>
      <view class="action-grid">
        <view class="action-item" @click="go('achievement')">
          <text class="action-icon">🏆</text>
          <text class="action-name">我的成就</text>
          <text class="action-desc">{{ overview.achievement_count || 0 }} 个已解锁</text>
        </view>
        <view class="action-item" @click="go('level-benefit')">
          <text class="action-icon">🎁</text>
          <text class="action-name">等级福利</text>
          <text class="action-desc">查看可兑换福利</text>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-title">积分获取指南</text>
      <view class="guide-card">
        <view class="guide-item" v-for="item in pointsGuide" :key="item.icon">
          <text class="guide-icon">{{ item.icon }}</text>
          <view class="guide-info">
            <text class="guide-name">{{ item.name }}</text>
            <text class="guide-desc">{{ item.desc }}</text>
          </view>
          <text class="guide-pts">+{{ item.pts }}分</text>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-title">积分兑换福利</text>
      <view class="benefit-card">
        <view class="benefit-item" v-for="item in exchangeList" :key="item.name">
          <text class="benefit-icon">{{ item.icon }}</text>
          <view class="benefit-info">
            <text class="benefit-name">{{ item.name }}</text>
            <text class="benefit-cost">{{ item.cost }} 心动分</text>
          </view>
          <view :class="['benefit-btn', (overview.heart_points || 0) < item.cost && 'disabled']" @click="exchangeBenefit(item)">
            {{ (overview.heart_points || 0) >= item.cost ? '兑换' : '积分不足' }}
          </view>
        </view>
      </view>
    </view>

    <view v-if="!overview.level" class="empty-guide">
      <text class="empty-icon">💕</text>
      <text class="empty-title">快去和TA一起完成任务吧</text>
      <text class="empty-hint">打卡、发悄悄话、完成心愿都能获得心动分，升级你们的恋爱等级</text>
    </view>
  <custom-tabbar :current="4" />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get } from '@/utils/request'
import { useUserStore } from '@/store/user.js'
import CustomTabbar from '@/components/custom-tabbar.vue'

const userStore = useUserStore()
const overview = ref({})

const LEVEL_POINTS = { 1: 100, 2: 300, 3: 600, 4: 1000, 5: 1500, 6: 2100, 7: 2800, 8: 3600, 9: 4500, 10: 5500 }
const LEVEL_NAMES = { 1: '初识心动', 2: '甜蜜热恋', 3: '默契伴侣', 4: '灵魂知己', 5: '真爱永恒', 6: '神仙眷侣', 7: '心有灵犀', 8: '情深似海', 9: '至死不渝', 10: '天作之合' }
const LEVEL_BENEFITS = { 1: '奶茶报销券', 2: '免生气卡', 3: '惊喜盲盒', 4: '旅行基金', 5: '定制纪念品' }

const pointsGuide = [
  { icon: '✅', name: '每日打卡', desc: '坚持打卡养成好习惯', pts: 5 },
  { icon: '💌', name: '发送悄悄话', desc: '给TA一句暖心的话', pts: 5 },
  { icon: '✨', name: '完成心愿', desc: '帮TA实现一个小愿望', pts: 30 },
  { icon: '📅', name: '纪念日惊喜', desc: '在纪念日给TA准备惊喜', pts: 100 },
  { icon: '🎭', name: '记录情绪', desc: '分享今天的心情', pts: 3 },
]

const exchangeList = [
  { icon: '🧋', name: '奶茶报销券', cost: 20 },
  { icon: '😤', name: '免生气卡', cost: 50 },
  { icon: '🎁', name: '惊喜盲盒', cost: 100 },
  { icon: '✈️', name: '旅行基金', cost: 200 },
]

const levelName = computed(() => LEVEL_NAMES[overview.value.level || 1] || '恋爱新手')
const nextLevelPoints = computed(() => LEVEL_POINTS[(overview.value.level || 1)] || ((overview.value.level || 1) + 1) * 500)
const nextLevelBenefit = computed(() => LEVEL_BENEFITS[(overview.value.level || 1) + 1] || '更多惊喜')
const levelProgress = computed(() => {
  const pts = overview.value.heart_points || 0
  const next = nextLevelPoints.value
  const prev = LEVEL_POINTS[(overview.value.level || 1) - 1] || 0
  return Math.min(100, Math.max(0, Math.round(((pts - prev) / (next - prev)) * 100)))
})

onShow(async () => {
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/user/login' })
    return
  }
  try {
    const res = await get('/love/overview')
    if (res && res.data) overview.value = res.data
  } catch (e) {
    console.error('加载恋爱概览失败', e)
  }
})

function go(page) { uni.navigateTo({ url: `/pages/love/${page}` }) }

function exchangeBenefit(item) {
  if ((overview.value.heart_points || 0) < item.cost) {
    uni.showToast({ title: '心动分不足', icon: 'none' })
    return
  }
  uni.showToast({ title: '兑换功能即将上线', icon: 'none' })
}
</script>

<style lang="scss" scoped>
.love-page {
  min-height: 100vh;
  background: #FFF5F9;
  padding: 20rpx;
  padding-bottom: 140rpx;
}
.level-card {
  background: linear-gradient(135deg, #FF69B4, #FF8FB1);
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 8rpx 30rpx rgba(255,107,157,0.3);
}
.level-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.level-badge {
  font-size: 56rpx;
  font-weight: bold;
  color: #fff;
}
.level-name {
  font-size: 28rpx;
  color: rgba(255,255,255,0.85);
}
.level-progress { margin-bottom: 16rpx; }
.progress-bar {
  height: 16rpx;
  background: rgba(255,255,255,0.3);
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}
.progress-fill {
  height: 100%;
  background: #fff;
  border-radius: 8rpx;
  transition: width 0.3s;
}
.progress-info {
  display: flex;
  justify-content: space-between;
}
.progress-current {
  font-size: 24rpx;
  color: #fff;
}
.progress-next {
  font-size: 24rpx;
  color: rgba(255,255,255,0.7);
}
.level-hint {
  display: block;
  font-size: 24rpx;
  color: rgba(255,255,255,0.8);
  margin-bottom: 8rpx;
}
.level-unlock {
  display: block;
  font-size: 24rpx;
  color: rgba(255,255,255,0.7);
}
.section { margin-bottom: 30rpx; }
.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 16rpx;
}
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}
.action-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  text-align: center;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}
.action-icon { display: block; font-size: 56rpx; margin-bottom: 12rpx; }
.action-name { display: block; font-size: 28rpx; color: #333; font-weight: bold; margin-bottom: 8rpx; }
.action-desc { display: block; font-size: 22rpx; color: #999; }
.guide-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 10rpx 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}
.guide-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #FFF5F9;
}
.guide-item:last-child { border-bottom: none; }
.guide-icon { font-size: 40rpx; margin-right: 20rpx; }
.guide-info { flex: 1; }
.guide-name { display: block; font-size: 28rpx; color: #333; margin-bottom: 4rpx; }
.guide-desc { display: block; font-size: 22rpx; color: #999; }
.guide-pts { font-size: 28rpx; color: #FF69B4; font-weight: bold; }
.benefit-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 10rpx 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}
.benefit-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #FFF5F9;
}
.benefit-item:last-child { border-bottom: none; }
.benefit-icon { font-size: 48rpx; margin-right: 20rpx; }
.benefit-info { flex: 1; }
.benefit-name { display: block; font-size: 28rpx; color: #333; margin-bottom: 4rpx; }
.benefit-cost { display: block; font-size: 22rpx; color: #999; }
.benefit-btn {
  background: #FF69B4;
  color: #fff;
  padding: 12rpx 28rpx;
  border-radius: 30rpx;
  font-size: 24rpx;
}
.benefit-btn.disabled {
  background: #eee;
  color: #bbb;
}
.empty-guide {
  text-align: center;
  padding: 80rpx 40rpx;
}
.empty-icon { display: block; font-size: 100rpx; margin-bottom: 24rpx; }
.empty-title { display: block; font-size: 32rpx; color: #333; font-weight: bold; margin-bottom: 12rpx; }
.empty-hint { display: block; font-size: 26rpx; color: #999; line-height: 1.6; }
</style>
