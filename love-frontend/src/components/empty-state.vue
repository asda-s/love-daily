<template>
  <view class="empty-state">
    <text class="empty-icon">{{ icon }}</text>
    <text class="empty-text">{{ text }}</text>
    <text v-if="hint" class="empty-hint">{{ hint }}</text>
  </view>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📭' },
  text: { type: String, default: '暂无数据' },
  hint: { type: String, default: '' }
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 40rpx;
}
.empty-icon {
  font-size: 80rpx;
  margin-bottom: 24rpx;
}
.empty-text {
  font-size: 30rpx;
  color: #666;
  margin-bottom: 12rpx;
}
.empty-hint {
  font-size: 24rpx;
  color: #bbb;
}
</style>
