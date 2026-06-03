<template>
  <view class="diary-detail-page">
    <!-- Header mood display -->
    <view class="mood-header" :style="{ background: moodBg }">
      <view class="mood-emoji-circle" :style="{ background: moodColor + '22' }">
        <text class="mood-emoji">{{ moodEmoji }}</text>
      </view>
      <view class="mood-info">
        <view class="mood-names">
          <text class="mood-name" :style="{ color: moodColor }">{{ moodName }}</text>
          <template v-if="diary.second_mood && MOOD_CONFIG[diary.second_mood]">
            <text class="mood-separator">+</text>
            <text class="mood-name" :style="{ color: MOOD_CONFIG[diary.second_mood].color }">
              {{ MOOD_CONFIG[diary.second_mood].name }}
            </text>
          </template>
        </view>
        <view class="intensity-bar-wrap">
          <view class="intensity-bar-bg">
            <view class="intensity-bar-fill" :style="{ width: ((diary.mood_intensity || 0) * 20) + '%', background: moodColor }"></view>
          </view>
          <text class="intensity-label">{{ diary.mood_intensity || 0 }}/5</text>
        </view>
      </view>
    </view>

    <!-- Edit button -->
    <view class="edit-btn" v-if="isMine" @click="goEdit">
      <text class="edit-btn-text">编辑</text>
    </view>

    <!-- Content card -->
    <view class="content-card">
      <!-- Author info -->
      <view class="author-row">
        <image class="author-avatar" :src="resolveImageUrl(diary.avatar) || '/static/default-avatar.png'" mode="aspectFill" />
        <view class="author-info">
          <text class="author-name">{{ diary.nickname || '匿名' }}</text>
          <text class="author-time">{{ formatTime(diary.created_at) }}</text>
        </view>
      </view>

      <!-- Content text -->
      <view class="diary-content" v-if="diary.content">
        <text class="content-text">{{ diary.content }}</text>
      </view>

      <!-- Images -->
      <view class="image-grid" v-if="imageList.length">
        <image
          v-for="(img, idx) in imageList"
          :key="idx"
          class="grid-image"
          :src="resolveImageUrl(img)"
          mode="aspectFill"
          @click="previewImage(idx)"
        />
      </view>

      <!-- Tags -->
      <view class="tags-row" v-if="tagList.length">
        <view class="tag-chip" v-for="(tag, idx) in tagList" :key="idx">
          <text class="tag-text">#{{ tag }}</text>
        </view>
      </view>
    </view>

    <!-- Divider -->
    <view class="divider"></view>

    <!-- Reactions section -->
    <view class="section-card">
      <text class="section-title">快速反应</text>
      <view class="reaction-btns">
        <view
          v-for="(cfg, key) in REACTION_CONFIG"
          :key="key"
          class="reaction-btn"
          :class="{ 'reaction-active': hasMyReaction(key) }"
          :style="hasMyReaction(key) ? { background: '#FFE4EC' } : {}"
          @click="toggleReaction(key)"
        >
          <text class="reaction-emoji">{{ cfg.emoji }}</text>
          <text class="reaction-label">{{ cfg.name }}</text>
        </view>
      </view>

      <!-- Reaction list -->
      <view class="reaction-list" v-if="diary.reactions && diary.reactions.length">
        <view class="reaction-item" v-for="r in diary.reactions" :key="r.user_id + '-' + r.type">
          <image class="reaction-avatar" :src="resolveImageUrl(r.avatar) || '/static/default-avatar.png'" mode="aspectFill" />
          <text class="reaction-nickname">{{ r.nickname }}</text>
          <text class="reaction-user-emoji">{{ REACTION_CONFIG[r.type]?.emoji || '' }}</text>
        </view>
      </view>
    </view>

    <!-- Divider -->
    <view class="divider"></view>

    <!-- Replies section -->
    <view class="section-card reply-section">
      <text class="section-title">留言</text>

      <view v-if="!rootReplies.length" class="empty-replies">
        <text class="empty-text">还没有留言，快来抢先留言吧~</text>
      </view>

      <view class="reply-list">
        <view v-for="reply in rootReplies" :key="reply.id" class="reply-item">
          <view class="reply-main" @longpress="onLongPressReply(reply)">
            <image class="reply-avatar" :src="resolveImageUrl(reply.avatar) || '/static/default-avatar.png'" mode="aspectFill" />
            <view class="reply-body">
              <view class="reply-header">
                <text class="reply-name">{{ reply.nickname || '匿名' }}</text>
                <text class="reply-time">{{ formatTime(reply.created_at) }}</text>
              </view>
              <text class="reply-content">{{ reply.content }}</text>
              <view class="reply-actions">
                <text class="reply-action-btn" @click="startReply(reply)">回复</text>
              </view>
            </view>
          </view>

          <!-- Children replies -->
          <view v-if="reply.children && reply.children.length" class="child-reply-list">
            <view v-for="child in reply.children" :key="child.id" class="reply-item child" @longpress="onLongPressReply(child)">
              <image class="reply-avatar small" :src="resolveImageUrl(child.avatar) || '/static/default-avatar.png'" mode="aspectFill" />
              <view class="reply-body">
                <view class="reply-header">
                  <text class="reply-name">{{ child.nickname || '匿名' }}</text>
                  <text class="reply-time">{{ formatTime(child.created_at) }}</text>
                </view>
                <text class="reply-content">{{ child.content }}</text>
                <view class="reply-actions">
                  <text class="reply-action-btn" @click="startReply(child)">回复</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Bottom spacer for fixed input -->
    <view style="height: 140rpx;"></view>

    <!-- Reply input bar -->
    <view class="reply-input-bar">
      <view class="reply-target" v-if="replyTarget" @click="cancelReply">
        <text class="reply-target-text">回复 {{ replyTarget.nickname || '匿名' }}</text>
        <text class="reply-target-close">x</text>
      </view>
      <view class="input-row">
        <input
          class="reply-input"
          v-model="replyContent"
          :placeholder="replyTarget ? '回复 ' + (replyTarget.nickname || '匿名') + '...' : '写下你的留言...'"
          confirm-type="send"
          @confirm="submitReply"
        />
        <view class="send-btn" :class="{ 'send-active': replyContent.trim() }" @click="submitReply">
          <text class="send-btn-text">发送</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get, post, del } from '@/utils/request'
import { useUserStore } from '@/store/user'
import { getRelativeTime, resolveImageUrl } from '@/utils/common'

const MOOD_CONFIG = {
  happy:     { emoji: '😊', name: '开心', color: '#FFD700', bg: '#FFF8DC' },
  sweet:     { emoji: '🥰', name: '甜蜜', color: '#FF69B4', bg: '#FFE4EC' },
  calm:      { emoji: '😌', name: '平静', color: '#87CEEB', bg: '#E0F0FF' },
  tired:     { emoji: '😮‍💨', name: '疲惫', color: '#808080', bg: '#F0F0F0' },
  sad:       { emoji: '😢', name: '难过', color: '#4169E1', bg: '#E8EDFF' },
  angry:     { emoji: '😠', name: '生气', color: '#FF4500', bg: '#FFE8E0' },
  wronged:   { emoji: '🥺', name: '委屈', color: '#9370DB', bg: '#F0E8FF' },
  surprised: { emoji: '🤩', name: '惊喜', color: '#FFA500', bg: '#FFF0E0' }
}

const REACTION_CONFIG = {
  hug:    { emoji: '🤗', name: '抱抱' },
  kiss:   { emoji: '😘', name: '亲亲' },
  like:   { emoji: '👍', name: '点赞' },
  cheer:  { emoji: '💪', name: '加油' },
  pat:    { emoji: '🥰', name: '摸摸头' },
  heart:  { emoji: '🫰', name: '比心' }
}

const userStore = useUserStore()

const diaryId = ref(null)
const diary = ref({
  id: null,
  user_id: null,
  mood_type: '',
  mood_intensity: 0,
  second_mood: '',
  content: '',
  images: '[]',
  tags: '[]',
  is_read: false,
  read_time: null,
  publish_status: 1,
  created_at: '',
  updated_at: '',
  nickname: '',
  avatar: null,
  reactions: []
})
const replies = ref([])
const replyContent = ref('')
const replyTarget = ref(null)

const moodEmoji = computed(() => MOOD_CONFIG[diary.value.mood_type]?.emoji || '😊')
const moodName = computed(() => MOOD_CONFIG[diary.value.mood_type]?.name || '未知')
const moodColor = computed(() => MOOD_CONFIG[diary.value.mood_type]?.color || '#FFD700')
const moodBg = computed(() => MOOD_CONFIG[diary.value.mood_type]?.bg || '#FFF8DC')

const isMine = computed(() => {
  return userStore.userInfo && diary.value.user_id === userStore.userInfo.id
})

const imageList = computed(() => {
  try {
    const parsed = JSON.parse(diary.value.images || '[]')
    return Array.isArray(parsed) ? parsed : []
  } catch (e) {
    return []
  }
})

const tagList = computed(() => {
  try {
    const parsed = JSON.parse(diary.value.tags || '[]')
    return Array.isArray(parsed) ? parsed : []
  } catch (e) {
    return []
  }
})

const rootReplies = computed(() => {
  return replies.value.filter(r => !r.parent_id).map(r => ({
    ...r,
    children: replies.value.filter(c => c.parent_id === r.id)
  }))
})

onShow(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1]
  if (page.options && page.options.id) {
    diaryId.value = page.options.id
    loadDiary()
    loadReplies()
  }
})

async function loadDiary() {
  try {
    const res = await get(`/life/diary/${diaryId.value}`)
    if (res && res.data) {
      diary.value = res.data
    }
  } catch (e) {
    console.error('加载日记失败', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

async function loadReplies() {
  try {
    const res = await get(`/life/diary/${diaryId.value}/replies`)
    if (res && res.data) {
      replies.value = Array.isArray(res.data) ? res.data : []
    }
  } catch (e) {
    console.error('加载回复失败', e)
  }
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  return getRelativeTime(dateStr)
}

function hasMyReaction(type) {
  if (!diary.value.reactions || !userStore.userInfo) return false
  return diary.value.reactions.some(r => r.user_id === userStore.userInfo.id && r.type === type)
}

async function toggleReaction(type) {
  if (!userStore.checkAuth()) return
  try {
    if (hasMyReaction(type)) {
      await del(`/life/diary/${diaryId.value}/reaction`, { reaction_type: type })
    } else {
      await post(`/life/diary/${diaryId.value}/reaction`, { reaction_type: type })
    }
    await loadDiary()
  } catch (e) {
    console.error('操作反应失败', e)
    uni.showToast({ title: '操作失败，请重试', icon: 'none' })
  }
}

function previewImage(idx) {
  uni.previewImage({
    current: idx,
    urls: imageList.value.map(resolveImageUrl)
  })
}

function goEdit() {
  uni.navigateTo({ url: `/pages/life/item-edit?id=${diaryId.value}` })
}

function startReply(reply) {
  replyTarget.value = reply
}

function cancelReply() {
  replyTarget.value = null
}

async function submitReply() {
  if (!userStore.checkAuth()) return
  const content = replyContent.value.trim()
  if (!content) {
    uni.showToast({ title: '请输入留言内容', icon: 'none' })
    return
  }
  try {
    const body = { content }
    if (replyTarget.value) {
      body.parent_id = replyTarget.value.id
    }
    await post(`/life/diary/${diaryId.value}/reply`, body)
    replyContent.value = ''
    replyTarget.value = null
    await loadReplies()
    uni.showToast({ title: '留言成功' })
  } catch (e) {
    console.error('留言失败', e)
    uni.showToast({ title: '提交失败，请重试', icon: 'none' })
  }
}

function onLongPressReply(reply) {
  if (!userStore.userInfo || reply.user_id !== userStore.userInfo.id) return
  uni.showModal({
    title: '删除留言',
    content: '确定删除这条留言吗？',
    confirmColor: '#e43d33',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/life/diary/reply/${reply.id}`)
          await loadReplies()
          uni.showToast({ title: '已删除' })
        } catch (e) {
          console.error('删除留言失败', e)
          uni.showToast({ title: '删除失败，请重试', icon: 'none' })
        }
      }
    }
  })
}
</script>

<style scoped>
.diary-detail-page {
  background: #FFF5F9;
  min-height: 100vh;
  position: relative;
}

/* Mood header */
.mood-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 40rpx 40rpx;
}

.mood-emoji-circle {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.mood-emoji {
  font-size: 80rpx;
}

.mood-info {
  align-items: center;
}

.mood-names {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.mood-name {
  font-size: 34rpx;
  font-weight: bold;
}

.mood-separator {
  font-size: 28rpx;
  color: #999;
  margin: 0 12rpx;
}

.intensity-bar-wrap {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.intensity-bar-bg {
  width: 300rpx;
  height: 14rpx;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 7rpx;
  overflow: hidden;
}

.intensity-bar-fill {
  height: 100%;
  border-radius: 7rpx;
  transition: width 0.3s;
}

.intensity-label {
  font-size: 24rpx;
  color: #999;
}

/* Edit button */
.edit-btn {
  position: absolute;
  top: 40rpx;
  right: 30rpx;
  background: rgba(255, 255, 255, 0.8);
  padding: 10rpx 28rpx;
  border-radius: 30rpx;
  z-index: 10;
}

.edit-btn-text {
  font-size: 26rpx;
  color: #FF6B9D;
}

/* Content card */
.content-card {
  background: #fff;
  margin: 20rpx;
  border-radius: 24rpx;
  padding: 30rpx;
}

.author-row {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.author-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  background: #f0f0f0;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 6rpx;
}

.author-time {
  font-size: 24rpx;
  color: #999;
}

.diary-content {
  margin-bottom: 24rpx;
}

.content-text {
  font-size: 30rpx;
  color: #333;
  line-height: 1.8;
}

/* Images */
.image-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.grid-image {
  width: calc((100% - 24rpx) / 3);
  height: 0;
  padding-bottom: calc((100% - 24rpx) / 3);
  border-radius: 12rpx;
  background: #f0f0f0;
}

/* Tags */
.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag-chip {
  background: #FFE8F0;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
}

.tag-text {
  font-size: 24rpx;
  color: #FF6B9D;
}

/* Divider */
.divider {
  height: 1rpx;
  background: #FFE4EC;
  margin: 0 40rpx;
}

/* Section card */
.section-card {
  background: #fff;
  margin: 20rpx;
  border-radius: 24rpx;
  padding: 30rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 24rpx;
}

/* Reactions */
.reaction-btns {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.reaction-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: #FFF5F9;
  transition: all 0.2s;
}

.reaction-btn.reaction-active {
  background: #FFE4EC !important;
  transform: scale(1.1);
}

.reaction-emoji {
  font-size: 36rpx;
  margin-bottom: 2rpx;
}

.reaction-label {
  font-size: 18rpx;
  color: #999;
}

.reaction-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.reaction-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #FFF5F9;
  padding: 8rpx 16rpx;
  border-radius: 24rpx;
}

.reaction-avatar {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #f0f0f0;
}

.reaction-user-emoji {
  font-size: 28rpx;
}

.reaction-nickname {
  font-size: 22rpx;
  color: #999;
  max-width: 100rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Replies */
.reply-section {
  margin-bottom: 0;
}

.empty-replies {
  padding: 40rpx 0;
  text-align: center;
}

.empty-text {
  font-size: 26rpx;
  color: #ccc;
}

.reply-list {
  display: flex;
  flex-direction: column;
}

.reply-item {
  margin-bottom: 24rpx;
}

.reply-item.child {
  margin-bottom: 16rpx;
}

.reply-main {
  display: flex;
}

.reply-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  margin-right: 16rpx;
  flex-shrink: 0;
  background: #f0f0f0;
}

.reply-avatar.small {
  width: 48rpx;
  height: 48rpx;
}

.reply-body {
  flex: 1;
  min-width: 0;
}

.reply-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8rpx;
}

.reply-name {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
}

.reply-time {
  font-size: 22rpx;
  color: #ccc;
}

.reply-content {
  font-size: 28rpx;
  color: #555;
  line-height: 1.6;
}

.reply-actions {
  margin-top: 10rpx;
}

.reply-action-btn {
  font-size: 24rpx;
  color: #FF6B9D;
}

.child-reply-list {
  margin-left: 80rpx;
  margin-top: 16rpx;
  padding-left: 16rpx;
  border-left: 4rpx solid #FFE8F0;
}

.child-reply-list .reply-item {
  display: flex;
}

/* Reply input bar */
.reply-input-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.06);
  z-index: 100;
}

.reply-target {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #FFF5F9;
  padding: 10rpx 20rpx;
  border-radius: 12rpx;
  margin-bottom: 12rpx;
}

.reply-target-text {
  font-size: 24rpx;
  color: #FF6B9D;
}

.reply-target-close {
  font-size: 26rpx;
  color: #999;
  padding: 0 10rpx;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.reply-input {
  flex: 1;
  background: #FFF5F9;
  padding: 16rpx 24rpx;
  border-radius: 30rpx;
  font-size: 28rpx;
}

.send-btn {
  background: #eee;
  padding: 14rpx 32rpx;
  border-radius: 30rpx;
}

.send-btn.send-active {
  background: #FF6B9D;
}

.send-btn-text {
  font-size: 28rpx;
  color: #fff;
}
</style>
