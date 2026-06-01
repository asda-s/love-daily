<template>
  <view class="emotion-page">
    <scroll-view
      class="emotion-list"
      scroll-y
      style="height: calc(100vh - 120rpx)"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view class="emotion-card" v-for="e in emotions" :key="e.id" :class="e.emotion_type">
        <view class="emotion-header">
          <view class="emotion-icon">{{ emotionIcons[e.emotion_type] }}</view>
          <view class="emotion-meta">
            <text class="emotion-name">{{ e.nickname }}</text>
            <text class="emotion-time">{{ e.created_at }}</text>
          </view>
          <view class="delete-btn" v-if="e.is_mine" @click="deleteEmotion(e.id)">×</view>
        </view>
        <view class="emotion-content">{{ e.content }}</view>
        <view class="warm-reply" v-if="e.warm_reply">
          <text class="warm-icon">💕</text>
          <text class="warm-text">{{ e.warm_reply }}</text>
        </view>
        <view class="sync-tag" v-if="e.is_sync">已同步给TA</view>
      </view>

      <view class="empty" v-if="!emotions.length">
        <text class="empty-icon">🫧</text>
        <text class="empty-text">还没有情绪记录</text>
        <text class="empty-hint">记录你的心情，让TA更懂你</text>
      </view>
    </scroll-view>
    <view class="fab" @click="goPublish">+</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get, del } from '@/utils/request'

const emotions = ref([])
const emotionIcons = { happy: '😊', sad: '😢', angry: '😠', wronged: '🥺', anxious: '😰' }
const refreshing = ref(false)

onShow(() => { loadEmotions() })

const loadEmotions = async () => {
  try {
    const res = await get('/interact/emotion')
    if (res && res.data) emotions.value = res.data
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

const onRefresh = async () => {
  refreshing.value = true
  await loadEmotions()
  refreshing.value = false
}

const deleteEmotion = async (id) => {
  uni.showModal({
    title: '确认', content: '确定删除？',
    success: async (r) => {
      if (r.confirm) {
        try {
          await del(`/interact/emotion/${id}`)
          emotions.value = emotions.value.filter(e => e.id !== id)
        } catch (e) {
          uni.showToast({ title: '删除失败，请重试', icon: 'none' })
        }
      }
    }
  })
}

const goPublish = () => {
  uni.navigateTo({ url: '/pages/interact/emotion-publish' })
}
</script>

<style scoped>
.emotion-page { background: #FFF5F9; min-height: 100vh; padding: 20rpx; padding-bottom: 120rpx; }
.emotion-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.emotion-card.happy { border-left: 6rpx solid #FFD700; }
.emotion-card.sad { border-left: 6rpx solid #6495ED; }
.emotion-card.angry { border-left: 6rpx solid #FF6347; }
.emotion-card.wronged { border-left: 6rpx solid #DDA0DD; }
.emotion-card.anxious { border-left: 6rpx solid #FFA500; }
.emotion-header { display: flex; align-items: center; margin-bottom: 16rpx; }
.emotion-icon { font-size: 40rpx; margin-right: 16rpx; }
.emotion-meta { flex: 1; }
.emotion-name { font-size: 26rpx; font-weight: bold; display: block; }
.emotion-time { font-size: 22rpx; color: #999; }
.delete-btn { font-size: 36rpx; color: #ccc; padding: 10rpx; }
.emotion-content { font-size: 28rpx; line-height: 1.6; }
.warm-reply { display: flex; align-items: flex-start; gap: 8rpx; margin-top: 16rpx; padding: 16rpx; background: #FFE4EC; border-radius: 12rpx; }
.warm-icon { font-size: 28rpx; }
.warm-text { font-size: 26rpx; color: #FF69B4; line-height: 1.5; }
.sync-tag { font-size: 20rpx; color: #FF69B4; margin-top: 12rpx; }
.empty { text-align: center; padding: 80rpx 40rpx; color: #999; }
.empty-icon { font-size: 80rpx; display: block; margin-bottom: 20rpx; }
.empty-text { font-size: 30rpx; color: #666; display: block; margin-bottom: 12rpx; }
.empty-hint { font-size: 24rpx; color: #bbb; display: block; }
.fab { position: fixed; right: 40rpx; bottom: 140rpx; width: 100rpx; height: 100rpx; background: #FF69B4; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: #fff; box-shadow: 0 4rpx 16rpx rgba(255,107,157,0.4); }
</style>
