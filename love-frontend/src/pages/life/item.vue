<template>
  <view class="item-page">
    <view class="search-bar">
      <input class="search-input" v-model="keyword" placeholder="搜索物品" @confirm="loadItems" />
      <picker :range="categoryOptions" :value="categoryIndex" @change="onCategoryChange">
        <view class="category-picker">{{ categoryOptions[categoryIndex] }}</view>
      </picker>
    </view>

    <scroll-view
      scroll-y
      class="scroll-area"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
    <view class="expiring-section" v-if="expiringItems.length">
      <view class="section-title">⚠️ 即将过期</view>
      <view class="item-card expiring" v-for="item in expiringItems" :key="item.id" @click="goEdit(item.id)">
        <view class="item-info">
          <view class="item-name">{{ item.name }}</view>
          <view class="item-detail">
            <text class="category-tag">{{ item.category }}</text>
            <text v-if="item.location">📍{{ item.location }}</text>
          </view>
          <view class="item-expiry" v-if="item.expiry_date">
            到期：{{ item.expiry_date }}
          </view>
        </view>
      </view>
    </view>

    <view class="item-list">
      <view class="section-title">全部物品</view>
      <view class="item-card" v-for="item in filteredItems" :key="item.id">
        <view class="item-info" @click="goEdit(item.id)">
          <view class="item-name">{{ item.name }}</view>
          <view class="item-detail">
            <text class="category-tag">{{ item.category }}</text>
            <text class="quantity">x{{ item.quantity }}</text>
            <text v-if="item.location">📍{{ item.location }}</text>
          </view>
        </view>
        <view class="delete-btn" @click.stop="deleteItem(item)">删除</view>
      </view>
      <view class="empty" v-if="!filteredItems.length">
        <text class="empty-icon">📦</text>
        <text class="empty-text">还没有物品</text>
        <text class="empty-hint">点击右下角"+"添加你们的共享物品</text>
      </view>
    </view>
    </scroll-view>

    <view class="fab" @click="goAdd">+</view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { get, del } from '@/utils/request'

const items = ref([])
const refreshing = ref(false)
const keyword = ref('')
const categoryOptions = ['全部', '食品', '日用品', '药品', '其他']
const categoryIndex = ref(0)

onMounted(() => {
  loadItems()
})

const loadItems = async () => {
  try {
    const params = {}
    if (keyword.value) params.keyword = keyword.value
    const res = await get('/life/item', params)
    if (res && res.data) {
      items.value = res.data
    }
  } catch (e) {
    console.error('加载物品失败', e)
  }
}

const onCategoryChange = (e) => {
  categoryIndex.value = e.detail.value
}

const filteredItems = computed(() => {
  let list = items.value
  if (categoryIndex.value > 0) {
    list = list.filter(i => i.category === categoryOptions[categoryIndex.value])
  }
  return list
})

const expiringItems = computed(() => {
  const now = new Date()
  const weekLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
  return items.value.filter(i => {
    if (!i.expiry_date) return false
    const d = new Date(i.expiry_date)
    return d <= weekLater && d >= now
  })
})

const goEdit = (id) => {
  uni.navigateTo({ url: `/pages/life/item-edit?id=${id}` })
}

const goAdd = () => {
  uni.navigateTo({ url: '/pages/life/item-edit' })
}

async function onRefresh() {
  refreshing.value = true
  await loadItems()
  refreshing.value = false
}

function deleteItem(item) {
  uni.showModal({
    title: '确认删除',
    content: '确定删除该物品？',
    confirmColor: '#e43d33',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del('/life/item/' + item.id)
          await loadItems()
        } catch (e) {}
      }
    }
  })
}
</script>

<style scoped>
.item-page {
  background: #FFF5F9;
  min-height: 100vh;
  padding-bottom: 120rpx;
}
.search-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx;
  background: #fff;
}
.search-input {
  flex: 1;
  background: #FFF5F9;
  padding: 16rpx 24rpx;
  border-radius: 30rpx;
  font-size: 28rpx;
}
.category-picker {
  background: #FFF5F9;
  padding: 16rpx 24rpx;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #666;
}
.section-title {
  font-size: 28rpx;
  font-weight: bold;
  padding: 20rpx 20rpx 10rpx;
}
.expiring-section {
  margin-bottom: 20rpx;
}
.item-list {
  padding: 0 20rpx;
}
.item-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.item-info {
  flex: 1;
  min-width: 0;
}
.delete-btn {
  font-size: 24rpx;
  color: #ff4d4f;
  padding: 8rpx 20rpx;
  border: 1rpx solid #ff4d4f;
  border-radius: 20rpx;
  margin-left: 16rpx;
}
.scroll-area {
  height: calc(100vh - 120rpx);
}
.item-card.expiring {
  margin: 0 20rpx 16rpx;
  border-left: 6rpx solid #ff4d4f;
}
.item-name {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}
.item-detail {
  display: flex;
  align-items: center;
  gap: 16rpx;
  font-size: 24rpx;
  color: #666;
}
.category-tag {
  background: #f0f0f0;
  padding: 4rpx 12rpx;
  border-radius: 10rpx;
  font-size: 22rpx;
}
.quantity {
  color: #FF69B4;
}
.item-expiry {
  font-size: 24rpx;
  color: #ff4d4f;
  margin-top: 8rpx;
}
.empty {
  text-align: center;
  padding: 80rpx 40rpx;
  color: #999;
}
.empty-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 20rpx;
}
.empty-text {
  font-size: 30rpx;
  color: #666;
  display: block;
  margin-bottom: 12rpx;
}
.empty-hint {
  font-size: 24rpx;
  color: #bbb;
  display: block;
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
  font-size: 48rpx;
  color: #fff;
  box-shadow: 0 4rpx 16rpx rgba(255, 107, 157, 0.4);
}
</style>
