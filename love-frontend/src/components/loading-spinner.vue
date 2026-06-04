<template>
  <view class="loading-wrap">
    <view class="spinner"></view>
    <text class="loading-text">{{ text }}</text>
  </view>
</template>

<script setup>
defineProps({
  text: { type: String, default: '加载中...' }
})
</script>

<style scoped>
.loading-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
}
.spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid #f0f0f0;
  border-top-color: #FF69B4;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16rpx;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.loading-text {
  font-size: 24rpx;
  color: #999;
}
</style>
