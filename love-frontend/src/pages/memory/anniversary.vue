<template>
  <view class="anniversary-container">
    <!-- 添加按钮 -->
    <view class="add-btn" @click="goAdd">
      <uni-icons type="plusempty" size="24" color="#FFFFFF"></uni-icons>
    </view>

    <!-- 纪念日列表 -->
    <scroll-view
      class="anniversary-list"
      scroll-y
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
    <view v-if="list.length === 0" class="empty-state">
      <text class="empty-icon">📅</text>
      <text class="empty-text">还没有纪念日</text>
      <text class="empty-tip">添加你们的重要日子，不错过每一个纪念日</text>
    </view>

    <view class="anniversary-items">
      <view 
        v-for="item in list" 
        :key="item.id" 
        class="anniversary-card"
        @click="goEdit(item.id)"
      >
        <view class="card-left">
          <view class="days-badge" :class="{ 'is-today': item.days_left === 0 }">
            <text v-if="item.days_left === 0" class="days-text">今天</text>
            <text v-else-if="item.days_left > 0" class="days-number">{{ item.days_left }}</text>
            <text v-else class="days-number expired">已过</text>
            <text v-if="item.days_left > 0" class="days-label">天后</text>
          </view>
        </view>

        <view class="card-center">
          <text class="title">{{ item.title }}</text>
          <text class="date">{{ item.target_date }}</text>
          <view v-if="item.type === 'couple'" class="type-tag">
            <text>情侣纪念日</text>
          </view>
        </view>

        <view class="card-right">
          <uni-icons type="right" size="16" color="#999"></uni-icons>
        </view>
      </view>
    </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get } from '@/utils/request'

// 列表数据
const list = ref([])
const refreshing = ref(false)

/**
 * 获取纪念日列表
 */
async function fetchList() {
  try {
    const res = await get('/memory/anniversary')
    list.value = res.data
  } catch (e) {
    console.error('获取纪念日失败', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

/**
 * 下拉刷新
 */
async function onRefresh() {
  refreshing.value = true
  await fetchList()
  refreshing.value = false
}

/**
 * 跳转添加页
 */
function goAdd() {
  uni.navigateTo({ url: '/pages/memory/anniversary-edit' })
}

/**
 * 跳转编辑页
 */
function goEdit(id) {
  uni.navigateTo({ url: `/pages/memory/anniversary-edit?id=${id}` })
}

onShow(() => {
  fetchList()
})
</script>

<style lang="scss" scoped>
.anniversary-container {
  min-height: 100vh;
  background: #FFF5F9;
  padding: 20rpx;
  padding-bottom: 140rpx;
}

.add-btn {
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

.anniversary-list {
  height: calc(100vh - 20rpx);
  padding: 20rpx;
}

.anniversary-items {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.anniversary-card {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);

  &:active {
    opacity: 0.9;
  }
}

.card-left {
  margin-right: 24rpx;
}

.days-badge {
  width: 120rpx;
  height: 120rpx;
  background: #FFE4EC;
  border-radius: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  &.is-today {
    background: #FF69B4;
    .days-text {
      color: #FFFFFF;
    }
  }
}

.days-number {
  font-size: 40rpx;
  font-weight: bold;
  color: #FF69B4;

  &.expired {
    font-size: 24rpx;
    color: #999999;
  }
}

.days-text {
  font-size: 28rpx;
  font-weight: bold;
  color: #FF69B4;
}

.days-label {
  font-size: 20rpx;
  color: #FF69B4;
  margin-top: 4rpx;
}

.card-center {
  flex: 1;
}

.title {
  font-size: 30rpx;
  color: #333333;
  font-weight: 500;
  margin-bottom: 8rpx;
  display: block;
}

.date {
  font-size: 24rpx;
  color: #999999;
  margin-bottom: 8rpx;
  display: block;
}

.type-tag {
  display: inline-block;
  background: #FFE4EC;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  color: #FF69B4;
}

.card-right {
  margin-left: 16rpx;
}
</style>
