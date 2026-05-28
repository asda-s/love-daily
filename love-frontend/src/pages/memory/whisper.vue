<template>
  <view class="whisper-container">
    <!-- 未读提示条 -->
    <view v-if="unreadCount > 0" class="unread-banner">
      <text class="unread-banner-text">{{ unreadCount }}条未读悄悄话</text>
    </view>
    <!-- 发送按钮 -->
    <view class="send-btn" @click="goSend">
      <uni-icons type="compose" size="24" color="#FFFFFF"></uni-icons>
    </view>

    <!-- 悄悄话列表 -->
    <scroll-view 
      class="whisper-list" 
      scroll-y 
      @scrolltolower="loadMore"
    >
      <view v-if="list.length === 0" class="empty-state">
        <text class="empty-icon">💌</text>
        <text class="empty-text">还没有悄悄话</text>
        <text class="empty-tip">给TA发送一条悄悄话吧</text>
      </view>

      <view 
        v-for="item in list" 
        :key="item.id" 
        class="whisper-item"
        :class="{ 'is-self': item.is_self }"
        @click="markRead(item)"
      >
        <view v-if="!item.is_self" class="avatar-wrapper">
          <image 
            class="avatar" 
            :src="item.sender_avatar || '/static/default-avatar.png'" 
            mode="aspectFill"
          ></image>
        </view>

        <view class="message-wrapper">
          <view class="message-bubble" :class="{ 'is-self': item.is_self }">
            <text class="message-content">{{ item.content }}</text>
          </view>
          <view class="message-info">
            <text class="message-time">{{ item.send_time }}</text>
            <text v-if="item.is_self && item.is_read" class="read-status">已读</text>
            <text v-if="item.is_self && !item.is_read" class="read-status unread">未读</text>
          </view>
        </view>

        <view v-if="item.is_self" class="avatar-wrapper">
          <image 
            class="avatar" 
            :src="userStore.userInfo?.avatar || '/static/default-avatar.png'" 
            mode="aspectFill"
          ></image>
        </view>
      </view>

      <!-- 加载更多 -->
      <view v-if="loading" class="loading-more">
        <text>加载中...</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get, put } from '@/utils/request'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// 列表数据
const list = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const unreadCount = ref(0)

/**
 * 获取悄悄话列表
 */
async function fetchList() {
  if (loading.value) return

  loading.value = true
  try {
    const res = await get('/memory/whisper', {
      page: page.value,
      page_size: pageSize.value
    })

    list.value = [...list.value, ...res.data.list]
    total.value = res.data.total
    unreadCount.value = res.data.unread_count || 0
  } catch (e) {
    console.error('获取悄悄话失败', e)
  } finally {
    loading.value = false
  }
}

/**
 * 加载更多
 */
function loadMore() {
  if (list.value.length >= total.value || loading.value) return
  page.value++
  fetchList()
}

/**
 * 跳转发送页
 */
function goSend() {
  uni.navigateTo({ url: '/pages/memory/whisper-send' })
}

/**
 * 标记已读
 */
async function markRead(item) {
  if (item.is_self || item.is_read) return
  
  try {
    await put(`/memory/whisper/${item.id}/read`)
    item.is_read = true
  } catch (e) {
    console.error('标记已读失败', e)
  }
}

onShow(() => {
  list.value = []
  page.value = 1
  total.value = 0
  fetchList()
})
</script>

<style lang="scss" scoped>
.whisper-container {
  min-height: 100vh;
  background: #FFF5F9;
  position: relative;
}

.send-btn {
  position: fixed;
  right: 30rpx;
  bottom: 120rpx;
  width: 100rpx;
  height: 100rpx;
  background: #FF69B4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(255, 107, 157, 0.4);
  z-index: 100;
}

.unread-banner {
  background: linear-gradient(135deg, #FF69B4, #FF8FB1);
  padding: 16rpx 30rpx;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 50;
}
.unread-banner-text {
  color: #fff;
  font-size: 26rpx;
}

.whisper-list {
  height: 100vh;
  padding: 20rpx;
  padding-bottom: 140rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 0;

  .empty-icon {
    font-size: 80rpx;
    margin-bottom: 24rpx;
  }

  .empty-text {
    font-size: 32rpx;
    color: #333333;
    margin-bottom: 12rpx;
  }

  .empty-tip {
    font-size: 24rpx;
    color: #999999;
  }
}

.whisper-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 24rpx;

  &.is-self {
    flex-direction: row-reverse;
  }
}

.avatar-wrapper {
  flex-shrink: 0;
}

.avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
}

.message-wrapper {
  max-width: 70%;
  margin: 0 16rpx;
}

.message-bubble {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);

  &.is-self {
    background: #FFE4EC;
  }
}

.message-content {
  font-size: 28rpx;
  color: #333333;
  line-height: 1.6;
}

.message-info {
  display: flex;
  align-items: center;
  margin-top: 8rpx;
  gap: 12rpx;
}

.message-time {
  font-size: 22rpx;
  color: #999999;
}

.read-status {
  font-size: 22rpx;
  color: #999999;

  &.unread {
    color: #FF69B4;
  }
}

.loading-more {
  text-align: center;
  padding: 24rpx;
  font-size: 24rpx;
  color: #999999;
}
</style>
