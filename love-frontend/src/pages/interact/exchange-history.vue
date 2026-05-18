<template>
  <view class="exchange-page">
    <view class="record-list">
      <view class="record-item" v-for="r in records" :key="r.id">
        <view class="record-info">
          <view class="record-name">{{ r.benefit_name }}</view>
          <view class="record-time">{{ r.exchange_time }}</view>
        </view>
        <view class="record-right">
          <text class="record-points">-{{ r.points }}分</text>
          <text class="fulfill-tag" :class="{ done: r.is_fulfilled }">{{ r.is_fulfilled ? '已兑现' : '待兑现' }}</text>
        </view>
      </view>
      <view class="empty" v-if="!records.length"><text>暂无兑换记录</text></view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'

const records = ref([])

onMounted(async () => {
  try {
    const res = await get('/interact/exchange/history')
    if (res && res.data) records.value = res.data
  } catch (e) {
    console.error('加载兑换记录失败', e)
  }
})
</script>

<style scoped>
.exchange-page { background: #f5f5f5; min-height: 100vh; }
.record-list { padding: 20rpx; }
.record-item { display: flex; justify-content: space-between; align-items: center; background: #fff; border-radius: 12rpx; padding: 24rpx; margin-bottom: 12rpx; }
.record-name { font-size: 28rpx; font-weight: bold; }
.record-time { font-size: 22rpx; color: #999; margin-top: 6rpx; }
.record-points { font-size: 28rpx; color: #FF6B9D; font-weight: bold; display: block; text-align: right; }
.fulfill-tag { font-size: 20rpx; color: #999; margin-top: 4rpx; }
.fulfill-tag.done { color: #4caf50; }
.empty { text-align: center; padding: 80rpx; color: #999; }
</style>
