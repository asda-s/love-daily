<template>
  <view class="emotion-publish-page">
    <view class="type-section">
      <text class="section-label">此刻的心情</text>
      <view class="type-grid">
        <view class="type-item" v-for="(icon, key) in emotionIcons" :key="key" :class="{ active: form.emotion_type === key }" @click="form.emotion_type = key">
          <text class="type-icon">{{ icon }}</text>
          <text class="type-name">{{ emotionNames[key] }}</text>
        </view>
      </view>
    </view>
    <view class="content-section">
      <textarea class="content-input" v-model="form.content" placeholder="说说你的心情..." maxlength="500" />
      <text class="word-count">{{ form.content.length }}/500</text>
    </view>
    <view class="sync-row">
      <text>同步给TA</text>
      <switch :checked="form.is_sync" @change="form.is_sync = $event.detail.value" color="#FF6B9D" />
    </view>
    <view class="submit-btn" @click="onSubmit">发布</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { post } from '@/utils/request'

const emotionIcons = { happy: '😊', sad: '😢', angry: '😠', wronged: '🥺', anxious: '😰' }
const emotionNames = { happy: '开心', sad: '难过', angry: '生气', wronged: '委屈', anxious: '焦虑' }
const form = ref({ emotion_type: 'happy', content: '', is_sync: false })

const onSubmit = async () => {
  if (!form.value.content.trim()) {
    uni.showToast({ title: '请输入内容', icon: 'none' })
    return
  }
  try {
    const res = await post('/interact/emotion', form.value)
    if (res) {
      uni.showToast({ title: '发布成功' })
      setTimeout(() => uni.navigateBack(), 1000)
    }
  } catch (e) {}
}
</script>

<style scoped>
.emotion-publish-page { background: #f5f5f5; min-height: 100vh; padding: 20rpx; }
.type-section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 20rpx; }
.section-label { font-size: 28rpx; font-weight: bold; display: block; margin-bottom: 20rpx; }
.type-grid { display: flex; justify-content: space-around; }
.type-item { text-align: center; padding: 16rpx 20rpx; border-radius: 16rpx; }
.type-item.active { background: #fff0f3; }
.type-icon { font-size: 48rpx; display: block; }
.type-name { font-size: 22rpx; color: #666; margin-top: 8rpx; }
.content-section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 20rpx; position: relative; }
.content-input { width: 100%; min-height: 200rpx; font-size: 28rpx; }
.word-count { position: absolute; right: 30rpx; bottom: 20rpx; font-size: 22rpx; color: #ccc; }
.sync-row { display: flex; justify-content: space-between; align-items: center; background: #fff; border-radius: 16rpx; padding: 24rpx 30rpx; margin-bottom: 40rpx; font-size: 28rpx; }
.submit-btn { background: #FF6B9D; color: #fff; text-align: center; padding: 24rpx; border-radius: 40rpx; font-size: 30rpx; }
</style>
