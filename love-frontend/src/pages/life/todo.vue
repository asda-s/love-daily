<template>
  <view class="todo-page">
    <view class="main-tabs">
      <view :class="['main-tab', currentTab === 'pending' && 'active']" @click="currentTab = 'pending'">
        <text>待办</text>
        <view v-if="pendingList.length" class="tab-badge">{{ pendingList.length }}</view>
      </view>
      <view :class="['main-tab', currentTab === 'done' && 'active']" @click="currentTab = 'done'">
        <text>已完成</text>
      </view>
    </view>

    <view class="sub-tabs">
      <view :class="['sub-tab', scope === 'all' && 'active']" @click="scope = 'all'">全部</view>
      <view :class="['sub-tab', scope === 'mine' && 'active']" @click="scope = 'mine'">我的</view>
      <view :class="['sub-tab', scope === 'couple' && 'active']" @click="scope = 'couple'">情侣</view>
    </view>

    <scroll-view
      scroll-y
      style="flex:1;overflow:hidden;"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
    <view v-if="filteredList.length === 0" class="empty-state">
      <text class="empty-icon">📋</text>
      <text class="empty-title">{{ currentTab === 'pending' ? '暂无待办事项' : '暂无已完成事项' }}</text>
      <text class="empty-hint">{{ currentTab === 'pending' ? '点击右下角+号，添加你的第一个待办吧' : '完成待办后会出现在这里' }}</text>
      <view v-if="currentTab === 'pending'" class="empty-btn" @click="goAdd">立即添加</view>
    </view>

    <view v-else class="todo-list">
      <view v-for="item in filteredList" :key="item.id" class="todo-card">
        <view class="todo-main" @click="toggleDone(item)">
          <view :class="['todo-check', item.status === 'completed' && 'checked']">
            <text v-if="item.status === 'completed'">✓</text>
          </view>
          <view class="todo-content">
            <text :class="['todo-title', item.status === 'completed' && 'done']">{{ item.title }}</text>
            <view class="todo-meta">
              <text v-if="item.deadline" class="todo-deadline">{{ formatDeadline(item.deadline) }}</text>
              <text v-if="item.is_shared" class="todo-tag shared">情侣共享</text>
              <text v-else class="todo-tag mine">仅自己</text>
            </view>
          </view>
        </view>
        <view class="todo-actions">
          <text class="todo-edit" @click="goEdit(item.id)">编辑</text>
          <text class="todo-delete" @click="deleteTodo(item)">删除</text>
        </view>
      </view>
    </view>
    </scroll-view>

    <view class="fab" @click="goAdd">
      <text class="fab-icon">+</text>
    </view>
    <custom-tabbar :current="2" />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get, put, del } from '@/utils/request'
import CustomTabbar from '@/components/custom-tabbar.vue'
import { useUserStore } from '@/store/user.js'

const userStore = useUserStore()
const todoList = ref([])
const refreshing = ref(false)
const currentTab = ref('pending')
const scope = ref('all')

const pendingList = computed(() => todoList.value.filter(t => t.status === 'pending'))
const filteredList = computed(() => {
  const list = currentTab.value === 'pending' ? pendingList.value : todoList.value.filter(t => t.status === 'completed')
  if (scope.value === 'mine') return list.filter(t => !t.is_shared)
  if (scope.value === 'couple') return list.filter(t => t.is_shared)
  return list
})

function formatDeadline(d) {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const diff = Math.ceil((date - now) / 86400000)
  if (diff < 0) return '已过期'
  if (diff === 0) return '今天截止'
  if (diff === 1) return '明天截止'
  return `${date.getMonth()+1}/${date.getDate()} 截止`
}

async function loadTodos() {
  try {
    const res = await get('/life/todo')
    if (res && res.data) {
      todoList.value = res.data.map(t => ({
        ...t,
        is_shared: t.type === 'couple'
      }))
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

async function toggleDone(item) {
  const newStatus = item.status === 'pending' ? 'completed' : 'pending'
  try {
    await put(`/life/todo/${item.id}`, { status: newStatus })
    item.status = newStatus
  } catch (e) {
    uni.showToast({ title: '操作失败，请重试', icon: 'none' })
  }
}

async function onRefresh() {
  refreshing.value = true
  await loadTodos()
  refreshing.value = false
}

function deleteTodo(item) {
  uni.showModal({
    title: '确认删除',
    content: '确定删除该待办？',
    confirmColor: '#e43d33',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del('/life/todo/' + item.id)
          await loadTodos()
        } catch (e) {
          uni.showToast({ title: '删除失败，请重试', icon: 'none' })
        }
      }
    }
  })
}

function goAdd() { uni.navigateTo({ url: '/pages/life/todo-edit' }) }
function goEdit(id) { uni.navigateTo({ url: `/pages/life/todo-edit?id=${id}` }) }

onShow(() => {
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/user/login' })
    return
  }
  loadTodos()
})
</script>

<style lang="scss" scoped>
.todo-page {
  min-height: 100vh;
  background: #FFF5F9;
  padding-bottom: 140rpx;
}
.main-tabs {
  display: flex;
  background: #fff;
  padding: 0 40rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.04);
}
.main-tab {
  flex: 1;
  text-align: center;
  padding: 28rpx 0;
  font-size: 30rpx;
  color: #999;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}
.main-tab.active {
  color: #FF69B4;
  font-weight: bold;
}
.main-tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 30%;
  right: 30%;
  height: 6rpx;
  background: #FF69B4;
  border-radius: 3rpx;
}
.tab-badge {
  background: #FF69B4;
  color: #fff;
  font-size: 20rpx;
  min-width: 32rpx;
  height: 32rpx;
  line-height: 32rpx;
  border-radius: 16rpx;
  text-align: center;
  padding: 0 8rpx;
}
.sub-tabs {
  display: flex;
  gap: 16rpx;
  padding: 20rpx 20rpx 0;
}
.sub-tab {
  padding: 10rpx 28rpx;
  border-radius: 30rpx;
  font-size: 24rpx;
  color: #666;
  background: #fff;
}
.sub-tab.active {
  background: #FF69B4;
  color: #fff;
}
.empty-state {
  text-align: center;
  padding: 120rpx 40rpx;
}
.empty-icon {
  display: block;
  font-size: 100rpx;
  margin-bottom: 24rpx;
}
.empty-title {
  display: block;
  font-size: 32rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 12rpx;
}
.empty-hint {
  display: block;
  font-size: 26rpx;
  color: #999;
  margin-bottom: 30rpx;
}
.empty-btn {
  display: inline-block;
  background: #FF69B4;
  color: #fff;
  padding: 16rpx 60rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
}
.todo-list {
  padding: 20rpx;
}
.todo-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}
.todo-main {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 20rpx;
}
.todo-check {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  border: 3rpx solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: transparent;
  flex-shrink: 0;
}
.todo-check.checked {
  background: #FF69B4;
  border-color: #FF69B4;
  color: #fff;
}
.todo-content { flex: 1; }
.todo-title {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 8rpx;
}
.todo-title.done {
  text-decoration: line-through;
  color: #bbb;
}
.todo-meta {
  display: flex;
  gap: 12rpx;
  align-items: center;
}
.todo-deadline {
  font-size: 22rpx;
  color: #FF69B4;
}
.todo-tag {
  font-size: 20rpx;
  padding: 2rpx 12rpx;
  border-radius: 10rpx;
}
.todo-tag.shared {
  background: #FFE4EC;
  color: #FF69B4;
}
.todo-tag.mine {
  background: #f0f0f0;
  color: #999;
}
.todo-actions {
  display: flex;
  align-items: center;
  gap: 8rpx;
}
.todo-edit {
  font-size: 24rpx;
  color: #FF69B4;
  padding: 8rpx 16rpx;
}
.todo-delete {
  font-size: 24rpx;
  color: #999;
  padding: 8rpx 16rpx;
}
.fab {
  position: fixed;
  right: 40rpx;
  bottom: 140rpx;
  width: 100rpx;
  height: 100rpx;
  background: #FF69B4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(255,107,157,0.4);
}
.fab-icon {
  font-size: 50rpx;
  color: #fff;
  line-height: 1;
}
</style>
