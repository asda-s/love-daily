<template>
  <view class="mood-calendar-page">
    <!-- Month Navigation -->
    <view class="month-nav">
      <view class="nav-arrow" @click="changeMonth(-1)">
        <text class="arrow-text">&lt;</text>
      </view>
      <text class="month-title">{{ currentYear }}年{{ currentMonth }}月</text>
      <view class="nav-arrow" @click="changeMonth(1)">
        <text class="arrow-text">&gt;</text>
      </view>
    </view>

    <!-- Calendar Card -->
    <view class="calendar-card">
      <!-- Weekday Headers -->
      <view class="weekday-row">
        <text class="weekday-cell" v-for="w in weekdays" :key="w">{{ w }}</text>
      </view>

      <!-- Day Grid -->
      <view class="day-grid">
        <view
          class="day-cell"
          v-for="(day, idx) in calendarDays"
          :key="idx"
          :class="{
            'other-month': !day.currentMonth,
            'is-today': day.isToday,
            'has-entries': day.entries.length > 0
          }"
          @tap="onDayTap(day)"
        >
          <text class="day-number" :class="{ 'today-text': day.isToday }">{{ day.day }}</text>
          <view class="day-emojis" v-if="day.entries.length > 0">
            <text
              class="emoji-dot"
              v-for="(entry, eIdx) in day.displayEntries"
              :key="eIdx"
              :style="{ color: entry.color }"
            >{{ entry.emoji }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Monthly Mood Distribution -->
    <view class="stats-section" v-if="moodStats.length > 0">
      <view class="section-title">本月心情分布</view>
      <view class="stats-card">
        <view class="stat-row" v-for="item in moodStats" :key="item.type">
          <text class="stat-emoji">{{ item.emoji }}</text>
          <text class="stat-name">{{ item.name }}</text>
          <view class="stat-bar-wrap">
            <view class="stat-bar" :style="{ width: item.percent + '%', background: item.color }"></view>
          </view>
          <text class="stat-count">{{ item.count }}</text>
        </view>
      </view>
    </view>

    <!-- Day Detail Popup -->
    <view class="popup-mask" v-if="showPopup" @tap="showPopup = false"></view>
    <view class="popup-sheet" :class="{ 'popup-show': showPopup }">
      <view class="popup-header">
        <text class="popup-date">{{ selectedDate }}</text>
        <view class="popup-close" @tap="showPopup = false">
          <text class="close-text">&times;</text>
        </view>
      </view>
      <view class="popup-list">
        <view
          class="diary-item"
          v-for="entry in selectedEntries"
          :key="entry.id"
          @tap="goToDetail(entry.id)"
        >
          <view class="diary-left">
            <text class="diary-emoji">{{ getMoodEmoji(entry.mood_type) }}</text>
          </view>
          <view class="diary-right">
            <view class="diary-top-row">
              <text class="diary-nickname">{{ entry.nickname }}</text>
              <text class="diary-mood-name">{{ getMoodName(entry.mood_type) }}</text>
            </view>
            <text class="diary-preview" v-if="entry.content">{{ entry.content }}</text>
            <text class="diary-preview" v-else>无内容预览</text>
            <text class="diary-time" v-if="entry.created_at">{{ formatTime(entry.created_at) }}</text>
          </view>
        </view>
        <view class="empty-tip" v-if="selectedEntries.length === 0">
          <text>暂无心情记录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { get } from '@/utils/request'

const MOOD_CONFIG = {
  happy:     { emoji: '\u{1F60A}', name: '开心', color: '#FFD700', bg: '#FFF8DC' },
  sweet:     { emoji: '\u{1F970}', name: '甜蜜', color: '#FF69B4', bg: '#FFE4EC' },
  calm:      { emoji: '\u{1F60C}', name: '平静', color: '#87CEEB', bg: '#E0F0FF' },
  tired:     { emoji: '\u{1F62E}\u{200D}\u{1F4A8}', name: '疲惫', color: '#808080', bg: '#F0F0F0' },
  sad:       { emoji: '\u{1F622}', name: '难过', color: '#4169E1', bg: '#E8EDFF' },
  angry:     { emoji: '\u{1F620}', name: '生气', color: '#FF4500', bg: '#FFE8E0' },
  wronged:   { emoji: '\u{1F97A}', name: '委屈', color: '#9370DB', bg: '#F0E8FF' },
  surprised: { emoji: '\u{1F929}', name: '惊喜', color: '#FFA500', bg: '#FFF0E0' }
}

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth() + 1)

const daysData = ref({})
const monthStats = ref({})

const showPopup = ref(false)
const selectedDate = ref('')
const selectedEntries = ref([])

function getMoodEmoji(type) {
  return MOOD_CONFIG[type]?.emoji || '\u{1F610}'
}

function getMoodName(type) {
  return MOOD_CONFIG[type]?.name || '未知'
}

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${hh}:${mm}`
}

function getDaysInMonth(year, month) {
  return new Date(year, month, 0).getDate()
}

function getFirstDayOfWeek(year, month) {
  return new Date(year, month - 1, 1).getDay()
}

const calendarDays = computed(() => {
  const days = []
  const firstDay = getFirstDayOfWeek(currentYear.value, currentMonth.value)
  const totalDays = getDaysInMonth(currentYear.value, currentMonth.value)

  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  // Previous month padding
  const prevMonth = currentMonth.value === 1 ? 12 : currentMonth.value - 1
  const prevYear = currentMonth.value === 1 ? currentYear.value - 1 : currentYear.value
  const prevDays = getDaysInMonth(prevYear, prevMonth)

  for (let i = firstDay - 1; i >= 0; i--) {
    const d = prevDays - i
    const dateStr = `${prevYear}-${String(prevMonth).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const entries = daysData.value[dateStr] || []
    days.push({
      day: d,
      currentMonth: false,
      isToday: false,
      dateStr,
      entries,
      displayEntries: buildDisplayEntries(entries)
    })
  }

  // Current month days
  for (let d = 1; d <= totalDays; d++) {
    const dateStr = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const entries = daysData.value[dateStr] || []
    days.push({
      day: d,
      currentMonth: true,
      isToday: dateStr === todayStr,
      dateStr,
      entries,
      displayEntries: buildDisplayEntries(entries)
    })
  }

  // Next month padding
  const remaining = 42 - days.length
  const nextMonth = currentMonth.value === 12 ? 1 : currentMonth.value + 1
  const nextYear = currentMonth.value === 12 ? currentYear.value + 1 : currentYear.value

  for (let d = 1; d <= remaining; d++) {
    const dateStr = `${nextYear}-${String(nextMonth).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const entries = daysData.value[dateStr] || []
    days.push({
      day: d,
      currentMonth: false,
      isToday: false,
      dateStr,
      entries,
      displayEntries: buildDisplayEntries(entries)
    })
  }

  return days
})

function buildDisplayEntries(entries) {
  if (!entries || entries.length === 0) return []
  const mine = entries.find(e => e.is_mine)
  const partner = entries.find(e => !e.is_mine)
  const result = []
  if (mine) {
    result.push({
      emoji: getMoodEmoji(mine.mood_type),
      color: MOOD_CONFIG[mine.mood_type]?.color || '#999'
    })
  }
  if (partner) {
    result.push({
      emoji: getMoodEmoji(partner.mood_type),
      color: MOOD_CONFIG[partner.mood_type]?.color || '#999'
    })
  }
  // If more than 2 entries, show at most 2
  return result.slice(0, 2)
}

const moodStats = computed(() => {
  const stats = monthStats.value
  if (!stats || Object.keys(stats).length === 0) return []

  const maxCount = Math.max(...Object.values(stats), 1)

  return Object.entries(stats)
    .map(([type, count]) => ({
      type,
      count,
      emoji: MOOD_CONFIG[type]?.emoji || '\u{1F610}',
      name: MOOD_CONFIG[type]?.name || type,
      color: MOOD_CONFIG[type]?.color || '#999',
      percent: Math.round((count / maxCount) * 100)
    }))
    .sort((a, b) => b.count - a.count)
})

async function loadCalendarData() {
  try {
    const res = await get('/life/diary/calendar', {
      year: currentYear.value,
      month: currentMonth.value
    })
    if (res && res.data) {
      daysData.value = res.data.days || {}
      monthStats.value = res.data.stats || {}
    }
  } catch (e) {
    console.error('加载心情日历数据失败', e)
  }
}

function changeMonth(delta) {
  let m = currentMonth.value + delta
  let y = currentYear.value
  if (m < 1) {
    m = 12
    y -= 1
  } else if (m > 12) {
    m = 1
    y += 1
  }
  currentYear.value = y
  currentMonth.value = m
  daysData.value = {}
  monthStats.value = {}
  loadCalendarData()
}

function onDayTap(day) {
  if (day.entries.length === 0) return
  selectedDate.value = day.dateStr
  selectedEntries.value = day.entries
  showPopup.value = true
}

function goToDetail(id) {
  showPopup.value = false
  uni.navigateTo({
    url: `/pages/life/diary-detail?id=${id}`
  })
}

onMounted(() => {
  loadCalendarData()
})
</script>

<style scoped>
.mood-calendar-page {
  background: #FFF5F9;
  min-height: 100vh;
  padding: 20rpx;
}

/* Month Navigation */
.month-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx 0 30rpx;
  gap: 40rpx;
}

.nav-arrow {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 2rpx 8rpx rgba(255, 107, 157, 0.15);
}

.arrow-text {
  font-size: 32rpx;
  color: #FF6B9D;
  font-weight: bold;
}

.month-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  min-width: 220rpx;
  text-align: center;
}

/* Calendar Card */
.calendar-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(255, 107, 157, 0.08);
}

.weekday-row {
  display: flex;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #FFF0F5;
}

.weekday-cell {
  flex: 1;
  text-align: center;
  font-size: 24rpx;
  color: #999;
  font-weight: 500;
}

.day-grid {
  display: flex;
  flex-wrap: wrap;
}

.day-cell {
  width: calc(100% / 7);
  height: 110rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 8rpx;
  box-sizing: border-box;
  position: relative;
}

.day-cell.other-month {
  opacity: 0.35;
}

.day-cell.is-today .day-number {
  background: #FF6B9D;
  color: #fff;
  border-radius: 50%;
  width: 48rpx;
  height: 48rpx;
  line-height: 48rpx;
  text-align: center;
}

.day-number {
  font-size: 28rpx;
  color: #333;
  width: 48rpx;
  height: 48rpx;
  line-height: 48rpx;
  text-align: center;
}

.today-text {
  background: #FF6B9D;
  color: #fff !important;
  border-radius: 50%;
}

.day-emojis {
  display: flex;
  gap: 4rpx;
  margin-top: 4rpx;
}

.emoji-dot {
  font-size: 26rpx;
  line-height: 1;
}

/* Stats Section */
.stats-section {
  margin-top: 30rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.stats-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(255, 107, 157, 0.08);
}

.stat-row {
  display: flex;
  align-items: center;
  padding: 14rpx 0;
}

.stat-emoji {
  font-size: 32rpx;
  margin-right: 12rpx;
}

.stat-name {
  font-size: 26rpx;
  color: #666;
  width: 80rpx;
}

.stat-bar-wrap {
  flex: 1;
  height: 24rpx;
  background: #FFF0F5;
  border-radius: 12rpx;
  margin: 0 16rpx;
  overflow: hidden;
}

.stat-bar {
  height: 100%;
  border-radius: 12rpx;
  min-width: 8rpx;
  transition: width 0.3s ease;
}

.stat-count {
  font-size: 26rpx;
  color: #999;
  width: 48rpx;
  text-align: right;
}

/* Popup */
.popup-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 998;
}

.popup-sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  z-index: 999;
  padding: 30rpx;
  max-height: 70vh;
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.popup-sheet.popup-show {
  transform: translateY(0);
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #FFF0F5;
  margin-bottom: 20rpx;
}

.popup-date {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.popup-close {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-text {
  font-size: 40rpx;
  color: #999;
}

.popup-list {
  max-height: 55vh;
  overflow-y: auto;
}

.diary-item {
  display: flex;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #FFF5F9;
  align-items: flex-start;
}

.diary-item:last-child {
  border-bottom: none;
}

.diary-left {
  margin-right: 20rpx;
}

.diary-emoji {
  font-size: 48rpx;
}

.diary-right {
  flex: 1;
  min-width: 0;
}

.diary-top-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.diary-nickname {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.diary-mood-name {
  font-size: 22rpx;
  color: #FF6B9D;
  background: #FFF0F5;
  padding: 2rpx 12rpx;
  border-radius: 16rpx;
}

.diary-preview {
  font-size: 26rpx;
  color: #666;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  line-height: 1.5;
}

.diary-time {
  font-size: 22rpx;
  color: #bbb;
  margin-top: 8rpx;
}

.empty-tip {
  text-align: center;
  padding: 60rpx 0;
  color: #ccc;
  font-size: 28rpx;
}
</style>
