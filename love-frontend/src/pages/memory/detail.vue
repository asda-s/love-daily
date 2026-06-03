<template>
  <view class="detail-container">
    <view v-if="detail" class="detail-card">
      <!-- 用户信息 -->
      <view class="user-section">
        <view class="user-info">
          <image
            class="avatar"
            :src="resolveImageUrl(detail.avatar) || '/static/default-avatar.png'"
            mode="aspectFill"
          ></image>
          <view class="user-text">
            <text class="nickname">{{ detail.nickname }}</text>
            <text class="time">{{ detail.event_time }}</text>
          </view>
        </view>
      </view>

      <!-- 内容 -->
      <view class="content-section">
        <text class="title">{{ detail.title }}</text>
        <text v-if="detail.content" class="content">{{ detail.content }}</text>
      </view>

      <!-- 图片 -->
      <view v-if="detail.images && detail.images.length > 0" class="image-section">
        <image
          v-for="(img, index) in detail.images"
          :key="index"
          class="detail-image"
          :src="resolveImageUrl(img)"
          mode="widthFix"
          @click="previewImage(index)"
        ></image>
      </view>

      <!-- 操作按钮 -->
      <view v-if="isOwner" class="action-section">
        <view class="action-btn" @click="goEdit">
          <uni-icons type="compose" size="18" color="#666"></uni-icons>
          <text>编辑</text>
        </view>
        <view class="action-btn delete" @click="handleDelete">
          <uni-icons type="trash" size="18" color="#FF69B4"></uni-icons>
          <text>删除</text>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-else class="loading-state">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { get, del } from '@/utils/request'
import { useUserStore } from '@/store/user'
import { resolveImageUrl } from '@/utils/common'

const userStore = useUserStore()

// 详情数据
const detail = ref(null)
const memoryId = ref('')

// 是否为发布者
const isOwner = computed(() => {
  return detail.value && detail.value.user_id === userStore.userInfo?.id
})

/**
 * 获取详情
 */
async function fetchDetail() {
  try {
    const res = await get(`/memory/timeline/${memoryId.value}`)
    detail.value = res.data
  } catch (e) {
    console.error('获取详情失败', e)
    uni.showToast({ title: '获取详情失败', icon: 'none' })
  }
}

/**
 * 预览图片
 */
function previewImage(index) {
  uni.previewImage({
    urls: detail.value.images.map(resolveImageUrl),
    current: index
  })
}

/**
 * 跳转编辑页
 */
function goEdit() {
  uni.navigateTo({ url: `/pages/memory/publish?id=${memoryId.value}` })
}

/**
 * 删除时光线
 */
function handleDelete() {
  uni.showModal({
    title: '提示',
    content: '确定要删除这条时光记录吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/memory/timeline/${memoryId.value}`)
          uni.showToast({ title: '删除成功', icon: 'success' })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        } catch (e) {
          console.error('删除失败', e)
          uni.showToast({ title: '删除失败，请重试', icon: 'none' })
        }
      }
    }
  })
}

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  memoryId.value = currentPage.options.id
  
  if (memoryId.value) {
    fetchDetail()
  }
})
</script>

<style lang="scss" scoped>
.detail-container {
  min-height: 100vh;
  background: #FFF5F9;
  padding: 20rpx;
}

.detail-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.user-section {
  padding: 24rpx;
  border-bottom: 1rpx solid #FFF5F9;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  margin-right: 16rpx;
}

.user-text {
  flex: 1;
}

.nickname {
  font-size: 30rpx;
  color: #333333;
  font-weight: 500;
  margin-bottom: 4rpx;
  display: block;
}

.time {
  font-size: 24rpx;
  color: #999999;
}

.content-section {
  padding: 24rpx;
}

.title {
  font-size: 36rpx;
  color: #333333;
  font-weight: bold;
  margin-bottom: 16rpx;
  display: block;
}

.content {
  font-size: 28rpx;
  color: #666666;
  line-height: 1.8;
  display: block;
}

.image-section {
  padding: 0 24rpx 24rpx;
}

.detail-image {
  width: 100%;
  margin-bottom: 16rpx;
  border-radius: 8rpx;
}

.action-section {
  display: flex;
  justify-content: flex-end;
  padding: 20rpx 24rpx;
  border-top: 1rpx solid #FFF5F9;
}

.action-btn {
  display: flex;
  align-items: center;
  margin-left: 40rpx;
  font-size: 26rpx;
  color: #666666;

  text {
    margin-left: 8rpx;
  }

  &.delete {
    color: #FF69B4;
  }
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400rpx;
  font-size: 28rpx;
  color: #999999;
}
</style>
