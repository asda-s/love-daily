<template>
  <view class="period-page">
    <view class="calendar-section">
      <view class="calendar-header">
        <view class="nav-btn" @click="prevMonth">‹</view>
        <view class="month-title">{{ currentYear }}年{{ currentMonth }}月</view>
        <view class="nav-btn" @click="nextMonth">›</view>
      </view>
      <view class="weekday-row">
        <view class="weekday" v-for="day in weekDays" :key="day">{{ day }}</view>
      </view>
      <view class="calendar-grid">
        <view
          class="calendar-day"
          v-for="(day, index) in calendarDays"
          :key="index"
          :class="{
            'other-month': !day.currentMonth,
            'today': day.isToday,
            'period': day.isPeriod,
            'predicted-period': day.isPredictedPeriod,
            'ovulation': day.isOvulation,
            'safe': day.isSafe && day.currentMonth && !day.isPeriod && !day.isPredictedPeriod
          }"
          @click="day.currentMonth && onDayClick(day)"
        >
          <text class="day-text">{{ day.day }}</text>
          <view class="day-dot" v-if="day.isPeriod"></view>
          <view class="day-dot predicted" v-else-if="day.isPredictedPeriod"></view>
          <view class="day-dot ovulation" v-else-if="day.isOvulation"></view>
        </view>
      </view>
    </view>

    <view class="legend-section">
      <view class="legend-item">
        <view class="legend-dot period"></view>
        <text>经期</text>
      </view>
      <view class="legend-item">
        <view class="legend-dot predicted"></view>
        <text>预测经期</text>
      </view>
      <view class="legend-item">
        <view class="legend-dot ovulation"></view>
        <text>排卵日</text>
      </view>
    </view>

    <view class="info-card" v-if="prediction">
      <view class="card-title">周期预测</view>
      <view class="info-row">
        <text class="info-label">上次经期</text>
        <text class="info-value">{{ prediction.last_period_start }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">预测下次</text>
        <text class="info-value highlight">{{ prediction.next_period_start }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">排卵日</text>
        <text class="info-value">{{ prediction.ovulation_day }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">前安全期</text>
        <text class="info-value">{{ prediction.safe_before_start }} ~ {{ prediction.safe_before_end }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">后安全期</text>
        <text class="info-value">{{ prediction.safe_after_start }} ~ {{ prediction.safe_after_end }}</text>
      </view>
    </view>

    <view class="record-section">
      <view class="section-header">
        <text class="section-title">经期记录</text>
        <view class="add-btn" @click="goAdd">+ 记录经期</view>
      </view>
      <view class="record-list" v-if="records.length">
        <view class="record-item" v-for="record in records" :key="record.id">
          <view class="record-date">{{ record.start_date }} ~ {{ record.end_date }}</view>
          <view class="record-duration">{{ record.duration }}天</view>
        </view>
      </view>
      <view class="empty" v-else>
        <text>暂无记录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get } from '@/utils/request'

const weekDays = ['日', '一', '二', '三', '四', '五', '六']
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const calendarDays = ref([])
const records = ref([])
const prediction = ref(null)

onShow(() => {
  loadData()
})

const loadData = async () => {
  await Promise.all([loadRecords(), loadPrediction()])
  generateCalendar()
}

const loadRecords = async () => {
  try {
    const res = await get('/life/period')
    if (res && res.data) {
      records.value = res.data
    }
  } catch (e) {
    console.error('加载经期记录失败', e)
  }
}

const loadPrediction = async () => {
  try {
    const res = await get('/life/period/predict')
    if (res && res.data) {
      const d = res.data
      const safeBefore = d.safe_period?.before
      const safeAfter = d.safe_period?.after
      prediction.value = {
        last_period_start: d.latest_period?.start_date || '',
        next_period_start: d.next_period?.start_date || '',
        duration_days: d.latest_period?.duration_days || 5,
        ovulation_day: d.ovulation?.day || '',
        ovulation_start: d.ovulation?.start_date || '',
        ovulation_end: d.ovulation?.end_date || '',
        safe_before_start: safeBefore?.start_date || '',
        safe_before_end: safeBefore?.end_date || '',
        safe_after_start: safeAfter?.start_date || '',
        safe_after_end: safeAfter?.end_date || ''
      }
    }
  } catch (e) {
    console.error('加载预测失败', e)
  }
}

const generateCalendar = () => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value - 1, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value, 0)
  const startWeekDay = firstDay.getDay()

  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  const periodDates = new Set()
  const predictedDates = new Set()
  const ovulationDates = new Set()

  records.value.forEach(r => {
    const start = new Date(r.start_date)
    const end = new Date(r.end_date)
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      periodDates.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`)
    }
  })

  if (prediction.value) {
    const predStart = new Date(prediction.value.next_period_start)
    const predEnd = new Date(predStart)
    predEnd.setDate(predEnd.getDate() + (prediction.value.duration_days || 5) - 1)
    for (let d = new Date(predStart); d <= predEnd; d.setDate(d.getDate() + 1)) {
      predictedDates.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`)
    }
    // Mark ovulation window
    if (prediction.value.ovulation_start && prediction.value.ovulation_end) {
      const ovuStart = new Date(prediction.value.ovulation_start)
      const ovuEnd = new Date(prediction.value.ovulation_end)
      for (let d = new Date(ovuStart); d <= ovuEnd; d.setDate(d.getDate() + 1)) {
        ovulationDates.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`)
      }
    } else if (prediction.value.ovulation_day) {
      ovulationDates.add(prediction.value.ovulation_day)
    }
  }

  for (let i = startWeekDay - 1; i >= 0; i--) {
    const d = new Date(currentYear.value, currentMonth.value - 1, -i)
    days.push({
      day: d.getDate(),
      currentMonth: false,
      isToday: false,
      isPeriod: false,
      isPredictedPeriod: false,
      isOvulation: false,
      isSafe: false
    })
  }

  for (let i = 1; i <= lastDay.getDate(); i++) {
    const dateStr = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(i).padStart(2, '0')}`
    days.push({
      day: i,
      currentMonth: true,
      isToday: dateStr === todayStr,
      isPeriod: periodDates.has(dateStr),
      isPredictedPeriod: predictedDates.has(dateStr),
      isOvulation: ovulationDates.has(dateStr),
      isSafe: false
    })
  }

  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    days.push({
      day: i,
      currentMonth: false,
      isToday: false,
      isPeriod: false,
      isPredictedPeriod: false,
      isOvulation: false,
      isSafe: false
    })
  }

  calendarDays.value = days
}

const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  generateCalendar()
}

const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  generateCalendar()
}

const onDayClick = (day) => {
  uni.navigateTo({
    url: `/pages/life/period-edit?date=${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(day.day).padStart(2, '0')}`
  })
}

const goAdd = () => {
  uni.navigateTo({ url: '/pages/life/period-edit' })
}
</script>

<style scoped>
.period-page {
  background: #f5f5f5;
  min-height: 100vh;
  padding-bottom: 30rpx;
}
.calendar-section {
  background: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 20rpx;
}
.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10rpx 20rpx;
}
.nav-btn {
  font-size: 40rpx;
  color: #FF6B9D;
  padding: 10rpx 20rpx;
}
.month-title {
  font-size: 32rpx;
  font-weight: bold;
}
.weekday-row {
  display: flex;
  padding: 10rpx 0;
}
.weekday {
  flex: 1;
  text-align: center;
  font-size: 24rpx;
  color: #999;
}
.calendar-grid {
  display: flex;
  flex-wrap: wrap;
}
.calendar-day {
  width: 14.28%;
  height: 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}
.day-text {
  font-size: 28rpx;
}
.other-month .day-text {
  color: #ccc;
}
.today .day-text {
  color: #FF6B9D;
  font-weight: bold;
}
.period {
  background: rgba(255, 107, 157, 0.2);
  border-radius: 50%;
}
.predicted-period {
  background: rgba(255, 107, 157, 0.1);
  border-radius: 50%;
  border: 1rpx dashed #FF6B9D;
}
.ovulation {
  background: rgba(255, 165, 0, 0.2);
  border-radius: 50%;
}
.day-dot {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: #FF6B9D;
  position: absolute;
  bottom: 8rpx;
}
.day-dot.predicted {
  background: #FFB6C1;
}
.day-dot.ovulation {
  background: #FFA500;
}
.legend-section {
  display: flex;
  justify-content: center;
  gap: 30rpx;
  padding: 10rpx 20rpx;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 22rpx;
  color: #666;
}
.legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
}
.legend-dot.period {
  background: rgba(255, 107, 157, 0.4);
}
.legend-dot.predicted {
  background: rgba(255, 107, 157, 0.2);
  border: 1rpx dashed #FF6B9D;
}
.legend-dot.ovulation {
  background: rgba(255, 165, 0, 0.4);
}
.info-card {
  background: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 30rpx;
}
.card-title {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}
.info-row {
  display: flex;
  justify-content: space-between;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}
.info-label {
  color: #666;
  font-size: 28rpx;
}
.info-value {
  font-size: 28rpx;
}
.info-value.highlight {
  color: #FF6B9D;
  font-weight: bold;
}
.record-section {
  background: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 30rpx;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}
.section-title {
  font-size: 30rpx;
  font-weight: bold;
}
.add-btn {
  background: #FF6B9D;
  color: #fff;
  padding: 10rpx 24rpx;
  border-radius: 30rpx;
  font-size: 24rpx;
}
.record-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}
.record-date {
  font-size: 28rpx;
}
.record-duration {
  color: #FF6B9D;
  font-size: 26rpx;
}
.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
}
</style>
