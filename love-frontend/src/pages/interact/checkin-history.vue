<template>
  <view class="history-page">
    <view class="filter-bar">
      <view class="filter-item" :class="{ active: !projectId }" @click="projectId = null; loadHistory()">全部</view>
      <view class="filter-item" :class="{ active: projectId === p.id }" v-for="p in projects" :key="p.id" @click="projectId = p.id; loadHistory()">{{ p.name }}</view>
    </view>
    <view class="record-list">
      <view class="record-item" v-for="r in records" :key="r.id">
        <view class="record-left">
          <view class="record-name">{{ r.project_name }}</view>
          <view class="record-note" v-if="r.note">{{ r.note }}</view>
        </view>
        <view class="record-right">
          <view class="record-date">{{ r.checkin_date }}</view>
        </view>
      </view>
      <view class="empty" v-if="!records.length"><text>暂无记录</text></view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'

const projects = ref([])
const records = ref([])
const projectId = ref(null)

onMounted(async () => {
  try {
    const pRes = await get('/interact/checkin/project')
    if (pRes && pRes.data) projects.value = pRes.data
  } catch (e) {
    console.error('加载打卡项目失败', e)
  }
  loadHistory()
})

const loadHistory = async () => {
  try {
    const params = {}
    if (projectId.value) params.project_id = projectId.value
    const res = await get('/interact/checkin/history', params)
    if (res && res.data) records.value = res.data
  } catch (e) {
    console.error('加载打卡记录失败', e)
  }
}
</script>

<style scoped>
.history-page { background: transparent; min-height: 100vh; }
.filter-bar { display: flex; gap: 16rpx; padding: 20rpx; overflow-x: auto; white-space: nowrap; }
.filter-item { padding: 10rpx 24rpx; background: #fff; border-radius: 30rpx; font-size: 24rpx; color: #666; flex-shrink: 0; }
.filter-item.active { background: #FF69B4; color: #fff; }
.record-list { padding: 0 20rpx; }
.record-item { display: flex; justify-content: space-between; align-items: center; background: #fff; border-radius: 12rpx; padding: 24rpx; margin-bottom: 12rpx; }
.record-name { font-size: 28rpx; font-weight: bold; }
.record-note { font-size: 24rpx; color: #999; margin-top: 6rpx; }
.record-date { font-size: 24rpx; color: #999; }
.empty { text-align: center; padding: 80rpx; color: #999; }
</style>
