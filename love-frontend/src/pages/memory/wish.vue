<template>
  <view class="wish-container">
    <!-- 添加按钮 -->
    <view class="add-btn" @click="goAdd">
      <uni-icons type="plusempty" size="24" color="#FFFFFF"></uni-icons>
    </view>

    <!-- Tab切换 -->
    <view class="tab-bar">
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'pending' }"
        @click="currentTab = 'pending'"
      >
        <text>待完成</text>
      </view>
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'completed' }"
        @click="currentTab = 'completed'"
      >
        <text>已完成</text>
      </view>
    </view>

    <!-- 心愿列表 -->
    <scroll-view
      class="wish-list"
      scroll-y
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view v-if="filteredList.length === 0" class="empty-state">
        <text class="empty-icon">🌟</text>
        <text class="empty-text">{{ currentTab === 'pending' ? '还没有心愿' : '还没有完成的心愿' }}</text>
        <text class="empty-tip" v-if="currentTab === 'pending'">许下你们的共同心愿，一起努力实现吧</text>
      </view>

      <view 
        v-for="item in filteredList" 
        :key="item.id" 
        class="wish-card"
      >
        <view class="card-content" @click="goEdit(item.id)">
          <view class="wish-info">
            <text class="wish-text">{{ item.content }}</text>
            <text v-if="item.type === 'couple'" class="type-tag">情侣心愿</text>
          </view>
          <text v-if="item.complete_time" class="complete-time">
            完成于 {{ item.complete_time }}
          </text>
        </view>

        <view v-if="currentTab === 'pending'" class="card-action">
          <view class="complete-btn" @click="handleComplete(item.id)">
            <uni-icons type="checkmarkempty" size="20" color="#FF69B4"></uni-icons>
          </view>
          <view class="delete-btn" @click="handleDelete(item.id)">
            <uni-icons type="trash" size="18" color="#999"></uni-icons>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get, put, del } from '@/utils/request'

// 当前Tab
const currentTab = ref('pending')

// 列表数据
const list = ref([])
const refreshing = ref(false)

// 过滤后的列表
const filteredList = computed(() => {
  return list.value.filter(item => item.status === currentTab.value)
})

/**
 * 获取心愿列表
 */
async function fetchList() {
  try {
    const res = await get('/memory/wish')
    list.value = res.data
  } catch (e) {
    console.error('获取心愿失败', e)
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
 * 删除心愿
 */
function handleDelete(id) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这个心愿吗？',
    confirmColor: '#e43d33',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/memory/wish/${id}`)
          uni.showToast({ title: '已删除', icon: 'success' })
          fetchList()
        } catch (e) {}
      }
    }
  })
}

/**
 * 跳转添加页
 */
function goAdd() {
  uni.navigateTo({ url: '/pages/memory/wish-edit' })
}

/**
 * 跳转编辑页
 */
function goEdit(id) {
  uni.navigateTo({ url: `/pages/memory/wish-edit?id=${id}` })
}

/**
 * 标记完成
 */
function handleComplete(id) {
  uni.showModal({
    title: '完成心愿',
    content: '确定要标记这个心愿为已完成吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await put(`/memory/wish/${id}/complete`, {
            complete_time: new Date().toISOString().replace('T', ' ').substring(0, 19)
          })
          uni.showToast({ title: '恭喜完成心愿！', icon: 'success' })
          fetchList()
        } catch (e) {
          console.error('操作失败', e)
        }
      }
    }
  })
}

onShow(() => {
  fetchList()
})
</script>

<style lang="scss" scoped>
.wish-container {
  min-height: 100vh;
  background: transparent;
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

.tab-bar {
  display: flex;
  background: #FFFFFF;
  padding: 20rpx;
  gap: 20rpx;
}

.tab-item {
  flex: 1;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFF5F9;
  border-radius: 36rpx;
  font-size: 28rpx;
  color: #666666;

  &.active {
    background: #FFE4EC;
    color: #FF69B4;
  }
}

.wish-list {
  padding: 20rpx;
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
    font-size: 28rpx;
    color: #999999;
  }

  .empty-tip {
    font-size: 24rpx;
    color: #bbbbbb;
    margin-top: 12rpx;
  }
}

.wish-card {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-content {
  flex: 1;
  padding: 24rpx;
}

.wish-info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.wish-text {
  font-size: 28rpx;
  color: #333333;
}

.type-tag {
  display: inline-block;
  background: #FFE4EC;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  color: #FF69B4;
}

.complete-time {
  font-size: 24rpx;
  color: #999999;
}

.card-action {
  padding: 24rpx;
  border-left: 1rpx solid #FFF5F9;
}

.complete-btn {
  width: 64rpx;
  height: 64rpx;
  border: 2rpx solid #FF69B4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 12rpx;
}
</style>
