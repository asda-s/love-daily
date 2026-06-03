<template>
  <view class="whisper-container">
    <!-- 未读提示条 -->
    <view v-if="unreadCount > 0" class="unread-banner">
      <text class="unread-banner-text">{{ unreadCount }}条未读悄悄话</text>
    </view>

    <!-- 悄悄话列表 -->
    <scroll-view
      class="whisper-list"
      scroll-y
      :scroll-into-view="scrollTarget"
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
        :id="'msg-' + item.id"
        class="whisper-item"
        :class="{ 'is-self': item.is_self }"
        @click="markRead(item)"
      >
        <view v-if="!item.is_self" class="avatar-wrapper">
          <image
            class="avatar"
            :src="resolveImageUrl(item.sender_avatar)"
            mode="aspectFill"
          ></image>
        </view>

        <view class="message-wrapper">
          <view class="message-bubble" :class="{ 'is-self': item.is_self }">
            <text class="message-content">{{ item.content }}</text>
          </view>
          <view class="message-info">
            <text class="message-time">{{ formatChatTime(item.send_time) }}</text>
            <text v-if="item.is_self && item.is_read" class="read-status">已读</text>
            <text v-if="item.is_self && !item.is_read" class="read-status unread">未读</text>
          </view>
        </view>

        <view v-if="item.is_self" class="avatar-wrapper">
          <image
            class="avatar"
            :src="resolveImageUrl(userStore.userInfo?.avatar)"
            mode="aspectFill"
          ></image>
        </view>
      </view>

      <!-- 加载更多 -->
      <view v-if="loading" class="loading-more">
        <text>加载中...</text>
      </view>
    </scroll-view>

    <!-- 输入状态指示器 -->
    <view v-if="partnerTyping" class="typing-indicator">
      <text class="typing-text">对方正在输入</text>
      <view class="typing-dots">
        <view class="dot dot1"></view>
        <view class="dot dot2"></view>
        <view class="dot dot3"></view>
      </view>
    </view>

    <!-- 底部输入栏 -->
    <view class="input-bar">
      <view class="schedule-btn" @click="goSchedule">
        <uni-icons type="clock" size="20" color="#FF69B4"></uni-icons>
      </view>
      <input
        class="msg-input"
        v-model="inputText"
        placeholder="说点悄悄话..."
        confirm-type="send"
        @confirm="sendMessage"
        @input="onTyping"
      />
      <view class="send-btn-small" :class="{ active: inputText.trim() }" @click="sendMessage">
        <text class="send-text">发送</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onUnmounted, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get, put, post } from '@/utils/request'
import { useUserStore } from '@/store/user'
import { resolveImageUrl } from '@/utils/common'
import { subscribe, unsubscribe, send as wsSend, isConnected } from '@/utils/websocket'

const userStore = useUserStore()

// 格式化聊天时间：今天只显示时分，否则显示月日时分
function formatChatTime(timeStr) {
  if (!timeStr) return ''
  const today = new Date()
  const d = new Date(timeStr.replace(/-/g, '/'))
  const isToday = d.getFullYear() === today.getFullYear() &&
    d.getMonth() === today.getMonth() &&
    d.getDate() === today.getDate()
  const pad = n => String(n).padStart(2, '0')
  if (isToday) return `${pad(d.getHours())}:${pad(d.getMinutes())}`
  return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// 列表数据
const list = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const unreadCount = ref(0)
const scrollTarget = ref('')
const inputText = ref('')
const partnerTyping = ref(false)

let typingTimer = null
let typingClearTimer = null

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
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/**
 * 加载更多
 */
function loadMore() {
  if (list.value.length >= total.value || loading.value) return
  // 保存当前最后一条消息的id，加载后保持滚动位置
  const lastId = list.value.length > 0 ? list.value[list.value.length - 1].id : null
  page.value++
  fetchList().then(() => {
    if (lastId) {
      scrollTarget.value = ''
      nextTick(() => {
        scrollTarget.value = 'msg-' + lastId
      })
    }
  })
}

/**
 * 跳转定时发送页
 */
function goSchedule() {
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
    if (unreadCount.value > 0) unreadCount.value--
  } catch (e) {
    console.error('标记已读失败', e)
  }
}

/**
 * 发送悄悄话
 */
async function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return

  inputText.value = ''
  clearTyping()

  // 乐观更新：立即添加到本地列表
  const optimisticMsg = {
    id: 'temp-' + Date.now(),
    sender_id: userStore.userInfo?.id,
    sender_nickname: userStore.userInfo?.nickname,
    sender_avatar: userStore.userInfo?.avatar,
    content: text,
    send_time: new Date().toLocaleString('zh-CN', { hour12: false }),
    is_read: false,
    is_self: true
  }
  list.value.unshift(optimisticMsg)
  scrollToBottom()

  try {
    const res = await post('/memory/whisper', { content: text })
    // 用服务器返回的 id 替换临时 id
    const idx = list.value.findIndex(m => m.id === optimisticMsg.id)
    if (idx !== -1 && res.data?.id) {
      list.value[idx].id = res.data.id
    }
  } catch (e) {
    // 发送失败，移除乐观消息
    const idx = list.value.findIndex(m => m.id === optimisticMsg.id)
    if (idx !== -1) list.value.splice(idx, 1)
    uni.showToast({ title: '发送失败', icon: 'none' })
  }
}

/**
 * 输入事件 - 发送输入状态
 */
function onTyping() {
  if (!isConnected()) return
  wsSend(JSON.stringify({ type: 'typing', data: { is_typing: true } }))

  clearTimeout(typingTimer)
  typingTimer = setTimeout(() => {
    clearTyping()
  }, 2000)
}

function clearTyping() {
  clearTimeout(typingTimer)
  if (isConnected()) {
    wsSend(JSON.stringify({ type: 'typing', data: { is_typing: false } }))
  }
}

/**
 * 收到新悄悄话（WebSocket 推送）
 */
function onNewWhisper(data) {
  // 仅按 id 去重
  if (list.value.some(m => m.id === data.id)) return

  // 乐观更新：用服务器 id 替换临时 id
  const tempIdx = list.value.findIndex(m =>
    m.is_self && m.content === data.content && m.sender_id === data.sender_id && String(m.id).startsWith('temp-')
  )
  if (tempIdx !== -1) {
    list.value[tempIdx].id = data.id
    return
  }

  const msg = {
    id: data.id,
    sender_id: data.sender_id,
    sender_nickname: data.sender_nickname,
    sender_avatar: data.sender_avatar,
    content: data.content,
    send_time: data.send_time,
    is_read: false,
    is_self: data.sender_id === userStore.userInfo?.id
  }
  list.value.unshift(msg)

  if (!msg.is_self) {
    unreadCount.value++
    // 自动标记已读（因为正在查看）
    markRead(msg)
  }

  scrollToBottom()
}

/**
 * 收到输入状态（WebSocket 推送）
 */
function onTypingEvent(data) {
  if (data.user_id !== userStore.loverInfo?.id) return
  partnerTyping.value = data.is_typing

  clearTimeout(typingClearTimer)
  if (data.is_typing) {
    // 3秒无更新自动清除
    typingClearTimer = setTimeout(() => {
      partnerTyping.value = false
    }, 3000)
  }
}

/**
 * 滚动到底部
 */
function scrollToBottom() {
  nextTick(() => {
    if (list.value.length > 0) {
      scrollTarget.value = ''
      nextTick(() => {
        scrollTarget.value = 'msg-' + list.value[0].id
      })
    }
  })
}

let wsSubscribed = false
let dataLoaded = false

onShow(() => {
  // 首次进入才清空并加载，避免切换tab时闪烁
  if (!dataLoaded) {
    list.value = []
    page.value = 1
    total.value = 0
    fetchList()
    dataLoaded = true
  }

  // 订阅 WebSocket 事件（避免重复订阅）
  if (!wsSubscribed) {
    subscribe('whisper', onNewWhisper)
    subscribe('typing', onTypingEvent)
    wsSubscribed = true
  }
})

onUnmounted(() => {
  unsubscribe('whisper', onNewWhisper)
  unsubscribe('typing', onTypingEvent)
  wsSubscribed = false
  clearTyping()
  clearTimeout(typingClearTimer)
})
</script>

<style lang="scss" scoped>
.whisper-container {
  min-height: 100vh;
  background: #FFF5F9;
  display: flex;
  flex-direction: column;
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
  flex: 1;
  padding: 20rpx;
  padding-bottom: 20rpx;
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

/* 输入状态指示器 */
.typing-indicator {
  display: flex;
  align-items: center;
  padding: 8rpx 30rpx 4rpx;
  gap: 8rpx;
}

.typing-text {
  font-size: 22rpx;
  color: #999;
}

.typing-dots {
  display: flex;
  gap: 6rpx;
}

.dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  background: #FF69B4;
  animation: dot-bounce 1.4s infinite ease-in-out both;
}

.dot1 { animation-delay: 0s; }
.dot2 { animation-delay: 0.2s; }
.dot3 { animation-delay: 0.4s; }

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* 底部输入栏 */
.input-bar {
  display: flex;
  align-items: center;
  padding: 16rpx 20rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #FFFFFF;
  border-top: 1rpx solid #F0F0F0;
  gap: 16rpx;
}

.schedule-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.msg-input {
  flex: 1;
  height: 72rpx;
  background: #F5F5F5;
  border-radius: 36rpx;
  padding: 0 28rpx;
  font-size: 28rpx;
  color: #333;
}

.send-btn-small {
  width: 120rpx;
  height: 64rpx;
  background: #DDD;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.2s;

  &.active {
    background: #FF69B4;
  }
}

.send-text {
  font-size: 26rpx;
  color: #FFF;
}
</style>
