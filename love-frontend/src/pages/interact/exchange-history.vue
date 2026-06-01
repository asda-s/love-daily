<template>
  <view class="exchange-page">
    <scroll-view
      class="record-list"
      scroll-y
      style="height: calc(100vh - 20rpx)"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="loadMore"
    >
      <view class="record-item" v-for="r in records" :key="r.id">
        <view class="record-info">
          <view class="record-name">{{ r.benefit_name }}</view>
          <view class="record-time">{{ r.exchange_time }}</view>
        </view>
        <view class="record-right">
          <text class="record-points">-{{ r.points }}分</text>
          <view class="fulfill-row">
            <text class="fulfill-tag" :class="{ done: r.is_fulfilled }">{{ r.is_fulfilled ? '已兑现' : '待兑现' }}</text>
            <text v-if="!r.is_fulfilled" class="fulfill-btn" @click="fulfillRecord(r)">兑现</text>
          </view>
        </view>
      </view>
      <!-- 加载更多提示 -->
      <view class="loading-more" v-if="loadingMore">
        <text>加载中...</text>
      </view>
      <view class="no-more" v-if="!hasMore && records.length > 0">
        <text>没有更多了</text>
      </view>

      <view class="empty" v-if="!records.length"><text>暂无兑换记录</text></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, put } from '@/utils/request'

const records = ref([])
const refreshing = ref(false)
const page = ref(1)
const pageSize = 20
const hasMore = ref(true)
const loadingMore = ref(false)

const loadData = async () => {
  try {
    const res = await get('/interact/exchange/history')
    if (res && res.data) records.value = res.data
  } catch (e) {
    console.error('加载兑换记录失败', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

const onRefresh = async () => {
  refreshing.value = true
  page.value = 1
  hasMore.value = true
  await loadData()
  refreshing.value = false
}

const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return
  loadingMore.value = true
  page.value++
  await loadData()
  loadingMore.value = false
}

onMounted(() => { loadData() })

async function fulfillRecord(record) {
  uni.showModal({
    title: '确认兑现',
    content: `确认将「${record.benefit_name}」标记为已兑现？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await put(`/interact/exchange/${record.id}/fulfill`)
          record.is_fulfilled = true
          uni.showToast({ title: '已兑现', icon: 'success' })
        } catch (e) {
          uni.showToast({ title: '操作失败', icon: 'none' })
        }
      }
    }
  })
}
</script>

<style scoped>
.exchange-page { background: #FFF5F9; min-height: 100vh; }
.record-list { padding: 20rpx; }
.record-item { display: flex; justify-content: space-between; align-items: center; background: #fff; border-radius: 12rpx; padding: 24rpx; margin-bottom: 12rpx; }
.record-name { font-size: 28rpx; font-weight: bold; }
.record-time { font-size: 22rpx; color: #999; margin-top: 6rpx; }
.record-points { font-size: 28rpx; color: #FF69B4; font-weight: bold; display: block; text-align: right; }
.fulfill-tag { font-size: 20rpx; color: #999; margin-top: 4rpx; }
.fulfill-tag.done { color: #4caf50; }
.fulfill-row { display: flex; align-items: center; gap: 12rpx; justify-content: flex-end; }
.fulfill-btn { font-size: 22rpx; color: #FF69B4; background: rgba(255,105,180,0.1); padding: 4rpx 16rpx; border-radius: 20rpx; }
.empty { text-align: center; padding: 80rpx; color: #999; }
.loading-more, .no-more { text-align: center; padding: 30rpx 0; font-size: 24rpx; color: #999; }
</style>
