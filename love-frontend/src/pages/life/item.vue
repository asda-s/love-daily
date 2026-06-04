<template>
  <view class="diary-page">
    <!-- Header -->
    <view class="header">
      <view class="header-title">心情日记</view>
      <view class="header-actions">
        <view class="header-icon" @click="goCalendar">
          <text class="icon-text">📅</text>
        </view>
      </view>
    </view>

    <!-- Search Bar -->
    <view class="search-bar">
      <input
        class="search-input"
        v-model="searchKeyword"
        placeholder="搜索日记内容..."
        confirm-type="search"
        @confirm="doSearch"
        @input="onSearchInput"
      />
      <view v-if="searchKeyword" class="search-clear" @click="clearSearch">
        <text class="clear-text">✕</text>
      </view>
    </view>

    <!-- Mood Filter -->
    <scroll-view scroll-x class="mood-filter" :show-scrollbar="false">
      <view class="mood-filter-inner">
        <view
          class="mood-item"
          :class="{ active: selectedMood === '' }"
          @click="selectMood('')"
        >
          <view class="mood-emoji-wrap" :style="selectedMood === '' ? 'background: #FF69B4' : ''">
            <text class="mood-emoji">🌟</text>
          </view>
          <text class="mood-name" :style="selectedMood === '' ? 'color: #FF69B4' : ''">全部</text>
        </view>
        <view
          v-for="(cfg, key) in MOOD_CONFIG"
          :key="key"
          class="mood-item"
          :class="{ active: selectedMood === key }"
          @click="selectMood(key)"
        >
          <view
            class="mood-emoji-wrap"
            :style="selectedMood === key ? `background: ${cfg.color}` : `background: ${cfg.bg}`"
          >
            <text class="mood-emoji">{{ cfg.emoji }}</text>
          </view>
          <text class="mood-name" :style="selectedMood === key ? `color: ${cfg.color}` : ''">{{ cfg.name }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- Publisher Filter -->
    <view class="publisher-filter">
      <view
        v-for="p in publisherOptions"
        :key="p.value"
        class="publisher-pill"
        :class="{ active: selectedPublisher === p.value }"
        @click="selectPublisher(p.value)"
      >
        <text>{{ p.label }}</text>
      </view>
    </view>

    <!-- Diary List -->
    <scroll-view
      scroll-y
      class="diary-list"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="loadMore"
    >
      <view v-if="diaryList.length > 0" class="diary-cards">
        <view
          v-for="item in diaryList"
          :key="item.id"
          class="diary-card"
          @click="goDetail(item.id)"
          @longpress="onLongPress(item)"
        >
          <!-- Unread dot -->
          <view v-if="!item.is_read" class="unread-dot"></view>

          <view class="card-body">
            <!-- Left: mood emoji -->
            <view
              class="card-mood"
              :style="{ background: getMoodBg(item.mood_type) }"
            >
              <text class="card-mood-emoji">{{ getMoodEmoji(item.mood_type) }}</text>
            </view>

            <!-- Right: content -->
            <view class="card-content">
              <!-- User row -->
              <view class="card-user-row">
                <image
                  class="card-avatar"
                  :src="resolveImageUrl(item.avatar) || '/static/default-avatar.png'"
                  mode="aspectFill"
                />
                <text class="card-nickname">{{ item.nickname || '匿名' }}</text>
                <view
                  v-if="item.mood_intensity"
                  class="mood-intensity"
                  :style="{ color: getMoodColor(item.mood_type) }"
                >
                  {{ getMoodName(item.mood_type) }} × {{ item.mood_intensity }}
                </view>
              </view>

              <!-- Content preview -->
              <view class="card-text-wrap">
                <text class="card-text">{{ item.content }}</text>
              </view>

              <!-- Image thumbnail -->
              <view v-if="getImageUrl(item)" class="card-image-wrap">
                <image
                  class="card-image"
                  :src="getImageUrl(item)"
                  mode="aspectFill"
                />
              </view>

              <!-- Tags -->
              <view v-if="getTags(item).length" class="card-tags">
                <view v-for="(tag, idx) in getTags(item)" :key="idx" class="tag-chip">
                  <text class="tag-text">#{{ tag }}</text>
                </view>
              </view>

              <!-- Bottom row: time + reactions -->
              <view class="card-bottom">
                <text class="card-time">{{ formatRelativeTime(item.created_at) }}</text>
                <view class="reaction-bar" @click.stop>
                  <!-- Existing reactions -->
                  <view
                    v-for="(r, idx) in getExistingReactions(item)"
                    :key="idx"
                    class="reaction-chip"
                    :class="{ 'my-reaction': r.isMine }"
                    @click.stop="toggleReaction(item, r.type)"
                  >
                    <text class="reaction-chip-emoji">{{ r.emoji }}</text>
                    <text class="reaction-chip-count">{{ r.count }}</text>
                  </view>
                  <!-- Add reaction button -->
                  <view class="reaction-add" @click.stop="showReactionPicker(item)">
                    <text class="reaction-add-text">+</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- Loading more -->
      <view v-if="loading && page > 1" class="loading-more">
        <text class="loading-text">加载中...</text>
      </view>

      <!-- No more -->
      <view v-if="noMore && diaryList.length > 0" class="no-more">
        <text class="no-more-text">—— 没有更多了 ——</text>
      </view>

      <!-- Empty state -->
      <view v-if="!loading && diaryList.length === 0" class="empty-state">
        <text class="empty-emoji">😢</text>
        <text class="empty-text">还没有日记，写一篇吧</text>
      </view>
    </scroll-view>

    <!-- Reaction popup -->
    <view v-if="reactionPickerVisible" class="reaction-mask" @click="reactionPickerVisible = false">
      <view class="reaction-popup" @click.stop>
        <view class="reaction-popup-title">选择一个互动</view>
        <view class="reaction-options">
          <view
            v-for="(cfg, key) in REACTION_CONFIG"
            :key="key"
            class="reaction-option"
            @click="addReaction(key)"
          >
            <text class="reaction-option-emoji">{{ cfg.emoji }}</text>
            <text class="reaction-option-name">{{ cfg.name }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- FAB -->
    <view class="fab" @click="goCreate">
      <text class="fab-icon">✏️</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get, post, del } from '@/utils/request'
import { useUserStore } from '@/store/user'
import { resolveImageUrl } from '@/utils/common'

const userStore = useUserStore()

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

const publisherOptions = [
  { label: '全部', value: 'all' },
  { label: '我', value: 'me' },
  { label: 'TA', value: 'lover' }
]

const diaryList = ref([])
const selectedMood = ref('')
const selectedPublisher = ref('all')
const refreshing = ref(false)
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const noMore = ref(false)

const reactionPickerVisible = ref(false)
const reactionTargetItem = ref(null)
const searchKeyword = ref('')
let searchTimer = null

onShow(() => {
  loadDiaryList(true)
})

function selectMood(mood) {
  selectedMood.value = mood
  loadDiaryList(true)
}

function selectPublisher(pub) {
  selectedPublisher.value = pub
  loadDiaryList(true)
}

function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    doSearch()
  }, 500)
}

function doSearch() {
  if (searchKeyword.value.trim()) {
    searchDiaries()
  } else {
    loadDiaryList(true)
  }
}

function clearSearch() {
  searchKeyword.value = ''
  loadDiaryList(true)
}

async function searchDiaries() {
  if (loading.value) return
  loading.value = true
  try {
    const res = await get('/life/diary/search', { keyword: searchKeyword.value.trim() }, { useLoading: false })
    if (res && res.data) {
      diaryList.value = res.data
      noMore.value = true
    }
  } catch (e) {
    console.error('搜索失败', e)
    uni.showToast({ title: '搜索失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

async function loadDiaryList(reset = false) {
  if (loading.value) return
  if (reset) {
    page.value = 1
    noMore.value = false
    diaryList.value = []
  }
  if (noMore.value) return

  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize
    }
    if (selectedMood.value) {
      params.mood_type = selectedMood.value
    }
    if (selectedPublisher.value === 'me') {
      params.user_id = userStore.userInfo?.id
    } else if (selectedPublisher.value === 'lover') {
      params.user_id = userStore.loverInfo?.id
    }
    const res = await get('/life/diary', params, { useLoading: false })
    if (res && res.data) {
      const items = res.data.list || []
      total.value = res.data.total || 0
      if (reset) {
        diaryList.value = items
      } else {
        diaryList.value = [...diaryList.value, ...items]
      }
      if (diaryList.value.length >= total.value || items.length < pageSize) {
        noMore.value = true
      } else {
        page.value++
      }
    }
  } catch (e) {
    console.error('加载日记失败', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

async function onRefresh() {
  refreshing.value = true
  await loadDiaryList(true)
  refreshing.value = false
}

function loadMore() {
  if (!noMore.value && !loading.value) {
    loadDiaryList(false)
  }
}

function getMoodEmoji(moodType) {
  return MOOD_CONFIG[moodType]?.emoji || '😊'
}

function getMoodBg(moodType) {
  return MOOD_CONFIG[moodType]?.bg || '#FFF8DC'
}

function getMoodColor(moodType) {
  return MOOD_CONFIG[moodType]?.color || '#FFD700'
}

function getMoodName(moodType) {
  return MOOD_CONFIG[moodType]?.name || '未知'
}

function getImageUrl(item) {
  if (!item.images) return ''
  try {
    const arr = typeof item.images === 'string' ? JSON.parse(item.images) : item.images
    return arr.length > 0 ? resolveImageUrl(arr[0]) : ''
  } catch {
    return ''
  }
}

function getTags(item) {
  if (!item.tags) return []
  try {
    return typeof item.tags === 'string' ? JSON.parse(item.tags) : item.tags
  } catch {
    return []
  }
}

function getExistingReactions(item) {
  if (!item.reactions || !Array.isArray(item.reactions)) return []
  const currentUserId = userStore.userInfo?.id
  const grouped = {}
  for (const r of item.reactions) {
    if (!grouped[r.type]) {
      grouped[r.type] = { type: r.type, count: 0, isMine: false }
    }
    grouped[r.type].count++
    if (r.user_id === currentUserId) {
      grouped[r.type].isMine = true
    }
  }
  return Object.values(grouped)
    .filter(g => g.count > 0 && REACTION_CONFIG[g.type])
    .map(g => ({ ...g, emoji: REACTION_CONFIG[g.type].emoji }))
}

function showReactionPicker(item) {
  reactionTargetItem.value = item
  reactionPickerVisible.value = true
}

async function addReaction(reactionType) {
  reactionPickerVisible.value = false
  if (!reactionTargetItem.value) return
  try {
    await post(`/life/diary/${reactionTargetItem.value.id}/reaction`, {
      reaction_type: reactionType
    }, { useLoading: false })
    await loadDiaryList(true)
  } catch (e) {
    console.error('添加互动失败', e)
    uni.showToast({ title: '操作失败，请重试', icon: 'none' })
  }
}

async function toggleReaction(item, reactionType) {
  const currentUserId = userStore.userInfo?.id
  const isMine = item.reactions?.some(r => r.type === reactionType && r.user_id === currentUserId)

  try {
    if (isMine) {
      await del(`/life/diary/${item.id}/reaction`, {
        reaction_type: reactionType
      }, { useLoading: false })
    } else {
      await post(`/life/diary/${item.id}/reaction`, {
        reaction_type: reactionType
      }, { useLoading: false })
    }
    await loadDiaryList(true)
  } catch (e) {
    console.error('操作互动失败', e)
    uni.showToast({ title: '操作失败，请重试', icon: 'none' })
  }
}

function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  const now = Date.now()
  const date = new Date(dateStr)
  const ts = date.getTime()
  const diff = now - ts
  if (diff < 0) return '刚刚'
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function onLongPress(item) {
  const currentUserId = userStore.userInfo?.id
  const isOwner = item.user_id === currentUserId
  const actions = []
  if (isOwner) {
    actions.push('删除')
  }
  actions.push('取消')
  uni.showActionSheet({
    itemList: actions,
    success: async (res) => {
      if (isOwner && res.tapIndex === 0) {
        uni.showModal({
          title: '确认删除',
          content: '确定删除这篇日记吗？',
          confirmColor: '#FF69B4',
          success: (modalRes) => {
            if (modalRes.confirm) {
              deleteDiary(item.id)
            }
          }
        })
      }
    }
  })
}

async function deleteDiary(id) {
  try {
    await del(`/life/diary/${id}`)
    uni.showToast({ title: '已删除', icon: 'success' })
    await loadDiaryList(true)
  } catch (e) {
    console.error('删除日记失败', e)
    uni.showToast({ title: '删除失败，请重试', icon: 'none' })
  }
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/life/diary-detail?id=${id}` })
}

function goCalendar() {
  uni.navigateTo({ url: '/pages/life/mood-calendar' })
}

function goReport() {
  uni.navigateTo({ url: '/pages/life/mood-calendar' })
}

function goCreate() {
  uni.navigateTo({ url: '/pages/life/item-edit' })
}
</script>

<style scoped>
.diary-page {
  background: #FFF5F9;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 30rpx;
  background: #fff;
}

.header-title {
  font-size: 38rpx;
  font-weight: bold;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.header-icon {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFF5F9;
  border-radius: 50%;
}

.icon-text {
  font-size: 32rpx;
}

/* Search bar */
.search-bar {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 12rpx 30rpx;
  gap: 12rpx;
}
.search-input {
  flex: 1;
  height: 64rpx;
  background: #F5F5F5;
  border-radius: 32rpx;
  padding: 0 28rpx;
  font-size: 26rpx;
  color: #333;
}
.search-clear {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eee;
  border-radius: 50%;
}
.clear-text {
  font-size: 24rpx;
  color: #999;
}

/* Mood filter */
.mood-filter {
  background: #fff;
  padding: 16rpx 0;
  white-space: nowrap;
}

.mood-filter-inner {
  display: inline-flex;
  padding: 0 20rpx;
  gap: 16rpx;
}

.mood-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  min-width: 90rpx;
}

.mood-emoji-wrap {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.mood-emoji {
  font-size: 36rpx;
}

.mood-name {
  font-size: 22rpx;
  color: #999;
}

/* Publisher filter */
.publisher-filter {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 12rpx 30rpx 16rpx;
  background: #fff;
}

.publisher-pill {
  padding: 8rpx 28rpx;
  border-radius: 28rpx;
  font-size: 24rpx;
  color: #999;
  background: #F5F5F5;
}

.publisher-pill.active {
  background: #FFE4EC;
  color: #FF69B4;
}

/* Diary list */
.diary-list {
  flex: 1;
  height: 0;
}

.diary-cards {
  padding: 20rpx;
}

/* Diary card */
.diary-card {
  position: relative;
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(255, 105, 180, 0.08);
}

.unread-dot {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #FF69B4;
}

.card-body {
  display: flex;
  gap: 24rpx;
}

/* Left mood circle */
.card-mood {
  width: 96rpx;
  height: 96rpx;
  min-width: 96rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-mood-emoji {
  font-size: 48rpx;
}

/* Right content */
.card-content {
  flex: 1;
  min-width: 0;
}

.card-user-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 12rpx;
}

.card-avatar {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #f0f0f0;
}

.card-nickname {
  font-size: 24rpx;
  color: #666;
}

.mood-intensity {
  font-size: 22rpx;
  margin-left: auto;
}

.card-text-wrap {
  margin-bottom: 12rpx;
}

.card-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-image-wrap {
  margin-bottom: 12rpx;
}

.card-image {
  width: 200rpx;
  height: 150rpx;
  border-radius: 12rpx;
  background: #f5f5f5;
}

/* Tags */
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-bottom: 12rpx;
}

.tag-chip {
  background: #FFF0F5;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
}

.tag-text {
  font-size: 22rpx;
  color: #FF69B4;
}

/* Bottom row */
.card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-time {
  font-size: 22rpx;
  color: #bbb;
}

/* Reaction bar */
.reaction-bar {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.reaction-chip {
  display: flex;
  align-items: center;
  gap: 4rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  background: #F5F5F5;
}

.reaction-chip.my-reaction {
  background: #FFE4EC;
}

.reaction-chip-emoji {
  font-size: 24rpx;
}

.reaction-chip-count {
  font-size: 20rpx;
  color: #999;
}

.reaction-add {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #F5F5F5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reaction-add-text {
  font-size: 24rpx;
  color: #999;
}

/* Reaction popup */
.reaction-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reaction-popup {
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  width: 580rpx;
}

.reaction-popup-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 32rpx;
}

.reaction-options {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 32rpx;
}

.reaction-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  width: 120rpx;
}

.reaction-option-emoji {
  font-size: 56rpx;
}

.reaction-option-name {
  font-size: 22rpx;
  color: #666;
}

/* Loading / No more */
.loading-more {
  text-align: center;
  padding: 24rpx;
}

.loading-text {
  font-size: 24rpx;
  color: #bbb;
}

.no-more {
  text-align: center;
  padding: 24rpx;
}

.no-more-text {
  font-size: 24rpx;
  color: #ccc;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 160rpx 40rpx;
}

.empty-emoji {
  font-size: 96rpx;
  margin-bottom: 24rpx;
}

.empty-text {
  font-size: 30rpx;
  color: #999;
}

/* FAB */
.fab {
  position: fixed;
  right: 40rpx;
  bottom: 140rpx;
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #FF69B4, #FF8EC7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(255, 105, 180, 0.4);
  z-index: 100;
}

.fab-icon {
  font-size: 44rpx;
}
</style>
