<template>
  <view class="achievement-page">
    <view class="achievement-list">
      <view class="achievement-card" v-for="a in achievements" :key="a.id" :class="{ unlocked: a.is_unlocked }">
        <view class="achievement-icon">{{ a.is_unlocked ? '🏅' : '🔒' }}</view>
        <view class="achievement-info">
          <view class="achievement-name">{{ a.name }}</view>
          <view class="achievement-desc">{{ a.description }}</view>
          <view class="achievement-reward">奖励 {{ a.reward_points }} 心动分</view>
        </view>
        <view class="achievement-status">
          <text class="status-text" v-if="a.is_unlocked">已解锁</text>
          <text class="status-text locked" v-else>未解锁</text>
          <text class="unlock-time" v-if="a.unlock_time">{{ a.unlock_time }}</text>
        </view>
      </view>
      <view class="empty" v-if="!achievements.length"><text>暂无成就</text></view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'

const achievements = ref([])

onMounted(async () => {
  try {
    const res = await get('/love/achievements')
    if (res && res.data) achievements.value = res.data
  } catch (e) {
    console.error('加载成就失败', e)
  }
})
</script>

<style scoped>
.achievement-page { background: #f5f5f5; min-height: 100vh; padding: 20rpx; }
.achievement-card { display: flex; align-items: center; background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; opacity: 0.6; }
.achievement-card.unlocked { opacity: 1; border-left: 6rpx solid #FFD700; }
.achievement-icon { font-size: 48rpx; margin-right: 20rpx; }
.achievement-info { flex: 1; }
.achievement-name { font-size: 28rpx; font-weight: bold; margin-bottom: 6rpx; }
.achievement-desc { font-size: 24rpx; color: #666; margin-bottom: 6rpx; }
.achievement-reward { font-size: 22rpx; color: #FF6B9D; }
.achievement-status { text-align: right; }
.status-text { font-size: 24rpx; color: #4caf50; display: block; }
.status-text.locked { color: #ccc; }
.unlock-time { font-size: 20rpx; color: #999; margin-top: 4rpx; display: block; }
.empty { text-align: center; padding: 80rpx; color: #999; }
</style>
