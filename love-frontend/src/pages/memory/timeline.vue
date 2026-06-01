<template>
  <view class="timeline-container">
    <!-- 发布按钮 -->
    <view class="publish-btn" @click="goPublish">
      <uni-icons type="plusempty" size="24" color="#FFFFFF"></uni-icons>
    </view>

    <!-- 时光线列表 -->
    <scroll-view 
      class="timeline-list" 
      scroll-y 
      @scrolltolower="loadMore"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view v-if="list.length === 0" class="empty-state">
        <text class="empty-icon">📷</text>
        <text class="empty-text">还没有时光记录</text>
        <text class="empty-tip">点击右下角按钮，记录你们的美好瞬间</text>
      </view>

      <view 
        v-for="item in list" 
        :key="item.id" 
        class="timeline-card"
        @click="goDetail(item.id)"
      >
        <view class="card-header">
          <view class="user-info">
            <image 
              class="avatar" 
              :src="item.avatar || '/static/default-avatar.png'" 
              mode="aspectFill"
            ></image>
            <text class="nickname">{{ item.nickname }}</text>
          </view>
          <text class="time">{{ item.event_time }}</text>
        </view>
        
        <view class="card-body">
          <text class="title">{{ item.title }}</text>
          <text v-if="item.content" class="content">{{ item.content }}</text>
          
          <!-- 图片展示 -->
          <view v-if="item.images && item.images.length > 0" class="image-grid">
            <image 
              v-for="(img, index) in item.images.slice(0, 3)" 
              :key="index"
              class="preview-image"
              :src="img"
              mode="aspectFill"
              @click.stop="previewImage(item.images, index)"
            ></image>
            <view v-if="item.images.length > 3" class="more-images">
              <text>+{{ item.images.length - 3 }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 加载更多 -->
      <view v-if="loading" class="loading-more">
        <text>加载中...</text>
      </view>
      <view v-if="noMore && list.length > 0" class="no-more">
        <text>没有更多了</text>
      </view>
    </scroll-view>
    <custom-tabbar :current="1" />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get } from '@/utils/request'
import { useUserStore } from '@/store/user.js'
import CustomTabbar from '@/components/custom-tabbar.vue'

const userStore = useUserStore()
// 列表数据
const list = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const refreshing = ref(false)
const noMore = ref(false)

/**
 * 获取时光线列表
 */
async function fetchList(isRefresh = false) {
  if (loading.value) return

  loading.value = true
  try {
    const res = await get('/memory/timeline', {
      page: page.value,
      page_size: pageSize.value
    })

    if (isRefresh) {
      list.value = res.data.list
    } else {
      list.value = [...list.value, ...res.data.list]
    }

    total.value = res.data.total
    noMore.value = list.value.length >= total.value
  } catch (e) {
    console.error('获取时光线失败', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

/**
 * 下拉刷新
 */
function onRefresh() {
  refreshing.value = true
  page.value = 1
  noMore.value = false
  fetchList(true)
}

/**
 * 加载更多
 */
function loadMore() {
  if (noMore.value || loading.value) return
  page.value++
  fetchList()
}

/**
 * 跳转发布页
 */
function goPublish() {
  uni.navigateTo({ url: '/pages/memory/publish' })
}

/**
 * 跳转详情页
 */
function goDetail(id) {
  uni.navigateTo({ url: `/pages/memory/detail?id=${id}` })
}

/**
 * 预览图片
 */
function previewImage(urls, index) {
  uni.previewImage({
    urls: urls,
    current: index
  })
}

onShow(() => {
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/user/login' })
    return
  }
  fetchList()
})
</script>

<style lang="scss" scoped>
.timeline-container {
  min-height: 100vh;
  background: #FFF5F9;
  position: relative;
  padding-bottom: 140rpx;
}

.publish-btn {
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

  &:active {
    transform: scale(0.95);
  }
}

.timeline-list {
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

.timeline-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);

  &:active {
    opacity: 0.9;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 24rpx;
  border-bottom: 1rpx solid #FFF5F9;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  margin-right: 12rpx;
}

.nickname {
  font-size: 28rpx;
  color: #333333;
  font-weight: 500;
}

.time {
  font-size: 24rpx;
  color: #999999;
}

.card-body {
  padding: 20rpx 24rpx;
}

.title {
  font-size: 30rpx;
  color: #333333;
  font-weight: 500;
  margin-bottom: 12rpx;
  display: block;
}

.content {
  font-size: 26rpx;
  color: #666666;
  line-height: 1.6;
  margin-bottom: 16rpx;
  display: block;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.image-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.preview-image {
  width: 200rpx;
  height: 200rpx;
  border-radius: 8rpx;
}

.more-images {
  width: 200rpx;
  height: 200rpx;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-size: 32rpx;
}

.loading-more,
.no-more {
  text-align: center;
  padding: 24rpx;
  font-size: 24rpx;
  color: #999999;
}
</style>
