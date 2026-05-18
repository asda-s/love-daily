<template>
  <view class="level-benefit-page">
    <view class="level-list">
      <view class="level-card" v-for="l in levels" :key="l.level" :class="{ current: l.level === currentLevel, reached: l.level <= currentLevel }">
        <view class="level-badge">
          <text class="level-num">Lv.{{ l.level }}</text>
        </view>
        <view class="level-info">
          <view class="level-name">{{ l.name }}</view>
          <view class="level-desc">{{ l.description }}</view>
          <view class="level-points">需要 {{ l.points_required }} 心动分</view>
        </view>
        <view class="level-status">
          <text v-if="l.level < currentLevel" class="reached-tag">已达成</text>
          <text v-else-if="l.level === currentLevel" class="current-tag">当前</text>
          <text v-else class="locked-tag">未达成</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'

const levels = ref([])
const currentLevel = ref(1)

onMounted(async () => {
  try {
    const [lRes, oRes] = await Promise.all([
      get('/love/levels'),
      get('/love/overview')
    ])
    if (lRes && lRes.data) levels.value = lRes.data
    if (oRes && oRes.data) currentLevel.value = oRes.data.level || 1
  } catch (e) {}
})
</script>

<style scoped>
.level-benefit-page { background: #f5f5f5; min-height: 100vh; padding: 20rpx; }
.level-card { display: flex; align-items: center; background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; opacity: 0.5; }
.level-card.reached { opacity: 1; }
.level-card.current { border: 2rpx solid #FF6B9D; opacity: 1; }
.level-badge { width: 80rpx; height: 80rpx; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 20rpx; }
.level-card.reached .level-badge { background: linear-gradient(135deg, #FF6B9D, #FF8E53); }
.level-card.current .level-badge { background: linear-gradient(135deg, #FF6B9D, #FF8E53); }
.level-num { font-size: 24rpx; font-weight: bold; color: #666; }
.level-card.reached .level-num, .level-card.current .level-num { color: #fff; }
.level-info { flex: 1; }
.level-name { font-size: 28rpx; font-weight: bold; margin-bottom: 6rpx; }
.level-desc { font-size: 24rpx; color: #666; margin-bottom: 6rpx; }
.level-points { font-size: 22rpx; color: #999; }
.level-status { text-align: right; }
.reached-tag { font-size: 22rpx; color: #4caf50; background: #e8f5e9; padding: 4rpx 12rpx; border-radius: 10rpx; }
.current-tag { font-size: 22rpx; color: #FF6B9D; background: #fff0f3; padding: 4rpx 12rpx; border-radius: 10rpx; }
.locked-tag { font-size: 22rpx; color: #999; }
</style>
