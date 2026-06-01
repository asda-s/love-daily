<template>
  <view class="notification-page">
    <scroll-view
      class="notification-list"
      scroll-y
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view v-if="list.length === 0" class="empty-state">
        <text class="empty-icon">🔔</text>
        <text class="empty-text">暂无通知</text>
        <text class="empty-tip">收到新消息时会在这里提醒你</text>
      </view>

      <view
        v-for="item in list"
        :key="item.id"
        class="notification-item"
        :class="{ unread: !item.is_read }"
        @click="markRead(item)"
      >
        <view class="noti-icon-wrap">
          <text class="noti-icon">{{ typeIcons[item.type] || '🔔' }}</text>
          <view v-if="!item.is_read" class="unread-dot"></view>
        </view>
        <view class="noti-content">
          <text class="noti-title">{{ item.title }}</text>
          <text class="noti-body">{{ item.content }}</text>
          <text class="noti-time">{{ item.created_at }}</text>
        </view>
      </view>

      <view v-if="list.length > 0" class="mark-all" @click="markAllRead">
        <text class="mark-all-text">全部已读</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get, put } from '@/utils/request'

const list = ref([])
const refreshing = ref(false)

const typeIcons = {
  anniversary: '📅',
  period: '🩸',
  item: '📔',
  todo: '⏰',
  whisper: '💌',
  diary: '📔',
  reaction: '🤗',
  reply: '💬',
  system: '🔔'
}

async function loadData() {
  try {
    const res = await get('/user/notifications')
    if (res && res.data) list.value = res.data
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

async function onRefresh() {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

async function markRead(item) {
  if (item.is_read) return
  try {
    await put(`/user/notifications/${item.id}/read`)
    item.is_read = true
  } catch (e) {
    // silent
  }
}

async function markAllRead() {
  const unread = list.value.filter(n => !n.is_read)
  if (unread.length === 0) return
  try {
    await Promise.all(unread.map(n => put(`/user/notifications/${n.id}/read`)))
    unread.forEach(n => { n.is_read = true })
    uni.showToast({ title: '已全部标记已读' })
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

onShow(() => { loadData() })
</script>

<style scoped>
.notification-page { background: #FFF5F9; min-height: 100vh; }
.notification-list { height: 100vh; padding: 20rpx; }

.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 200rpx 0;
}
.empty-icon { font-size: 80rpx; margin-bottom: 24rpx; }
.empty-text { font-size: 32rpx; color: #333; margin-bottom: 12rpx; }
.empty-tip { font-size: 24rpx; color: #999; }

.notification-item {
  display: flex; align-items: flex-start; gap: 20rpx;
  background: #fff; border-radius: 16rpx; padding: 24rpx;
  margin-bottom: 16rpx;
}
.notification-item.unread { background: #FFF0F5; }

.noti-icon-wrap { position: relative; flex-shrink: 0; }
.noti-icon { font-size: 44rpx; }
.unread-dot {
  position: absolute; top: 0; right: 0;
  width: 16rpx; height: 16rpx;
  background: #FF4757; border-radius: 50%;
}

.noti-content { flex: 1; min-width: 0; }
.noti-title { display: block; font-size: 28rpx; color: #333; font-weight: 600; margin-bottom: 8rpx; }
.noti-body { display: block; font-size: 24rpx; color: #666; line-height: 1.5; margin-bottom: 8rpx; }
.noti-time { display: block; font-size: 22rpx; color: #bbb; }

.mark-all {
  text-align: center; padding: 30rpx;
}
.mark-all-text {
  font-size: 26rpx; color: #FF69B4;
  background: rgba(255,105,180,0.1);
  padding: 12rpx 40rpx; border-radius: 30rpx;
}
</style>
