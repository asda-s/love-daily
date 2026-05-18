<template>
  <view class="checkin-page">
    <scroll-view
      scroll-y
      class="checkin-scroll"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
    <view class="stats-bar">
      <view class="stat-item">
        <text class="stat-value">{{ stats.total_checkins || 0 }}</text>
        <text class="stat-label">累计打卡</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ stats.today_checkins || 0 }}</text>
        <text class="stat-label">今日打卡</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ stats.max_consecutive_days || 0 }}</text>
        <text class="stat-label">最长连续</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ stats.heart_points || 0 }}</text>
        <text class="stat-label">心动分</text>
      </view>
    </view>

    <view class="project-list">
      <view class="project-card" v-for="project in projects" :key="project.id">
        <view class="project-info">
          <view class="project-name">{{ project.name }}</view>
          <view class="project-meta">
            <text class="points-tag">+{{ project.points }}分</text>
            <text class="joint-tag" v-if="project.is_joint">情侣共打卡</text>
            <text class="consecutive" v-if="project.consecutive_days > 0">连续{{ project.consecutive_days }}天</text>
          </view>
        </view>
        <view
          class="checkin-btn"
          :class="{ checked: project.is_checked_today }"
          @click="doCheckin(project)"
        >
          {{ project.is_checked_today ? '已打卡' : '打卡' }}
        </view>
      </view>
      <view class="empty" v-if="!projects.length">
        <text class="empty-icon">📝</text>
        <text class="empty-text">还没有打卡项目</text>
        <text class="empty-hint">点击下方"新建打卡项目"开始你们的第一个约定吧</text>
      </view>
    </view>
    </scroll-view>

    <view class="bottom-actions">
      <view class="action-btn" @click="showAddDialog = true">+ 新建打卡项目</view>
      <view class="action-btn secondary" @click="goHistory">打卡记录</view>
    </view>

    <view class="dialog-mask" v-if="showAddDialog" @click="showAddDialog = false">
      <view class="dialog" @click.stop>
        <view class="dialog-title">新建打卡项目</view>
        <input class="dialog-input" v-model="newProject.name" placeholder="项目名称" />
        <view class="dialog-row">
          <text>每次获得心动分</text>
          <input class="small-input" type="number" v-model="newProject.points" />
        </view>
        <view class="dialog-row">
          <text>情侣共同打卡</text>
          <switch :checked="newProject.is_joint" @change="newProject.is_joint = $event.detail.value" color="#FF6B9D" />
        </view>
        <view class="dialog-btns">
          <view class="dialog-btn cancel" @click="showAddDialog = false">取消</view>
          <view class="dialog-btn confirm" @click="addProject">确定</view>
        </view>
      </view>
    </view>
    <custom-tabbar :current="3" />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { get, post } from '@/utils/request'
import { useUserStore } from '@/store/user.js'
import CustomTabbar from '@/components/custom-tabbar.vue'

const userStore = useUserStore()
const projects = ref([])
const stats = ref({})
const refreshing = ref(false)
const showAddDialog = ref(false)
const newProject = ref({ name: '', points: 5, is_joint: false })

onShow(() => {
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/user/login' })
    return
  }
  loadData()
})

const loadData = async () => {
  try {
    const [pRes, sRes] = await Promise.all([
      get('/interact/checkin/project'),
      get('/interact/checkin/stats')
    ])
    if (pRes && pRes.data) projects.value = pRes.data
    if (sRes && sRes.data) stats.value = sRes.data
  } catch (e) {
    console.error('加载打卡数据失败', e)
  }
}

const doCheckin = async (project) => {
  if (project.is_checked_today) {
    uni.showToast({ title: '今日已打卡', icon: 'none' })
    return
  }
  try {
    const res = await post('/interact/checkin', { project_id: project.id })
    if (res && res.data) {
      uni.showToast({ title: `打卡成功 +${res.data.points_earned}分` })
      project.is_checked_today = true
      project.consecutive_days++
      stats.value.today_checkins++
      stats.value.total_checkins++
      stats.value.heart_points = res.data.total_points
    }
  } catch (e) {}
}

const addProject = async () => {
  if (!newProject.value.name.trim()) {
    uni.showToast({ title: '请输入名称', icon: 'none' })
    return
  }
  try {
    await post('/interact/checkin/project', newProject.value)
    uni.showToast({ title: '创建成功' })
    showAddDialog.value = false
    newProject.value = { name: '', points: 5, is_joint: false }
    loadData()
  } catch (e) {}
}

const goHistory = () => {
  uni.navigateTo({ url: '/pages/interact/checkin-history' })
}

async function onRefresh() {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}
</script>

<style scoped>
.checkin-page {
  background: #f5f5f5;
  min-height: 100vh;
}
.checkin-scroll {
  height: calc(100vh - 140rpx);
  padding-bottom: 140rpx;
}
.stats-bar {
  display: flex;
  background: linear-gradient(135deg, #FF6B9D, #FF8E53);
  padding: 30rpx;
}
.stat-item {
  flex: 1;
  text-align: center;
  color: #fff;
}
.stat-value {
  font-size: 36rpx;
  font-weight: bold;
  display: block;
}
.stat-label {
  font-size: 22rpx;
  opacity: 0.8;
}
.project-list {
  padding: 20rpx;
}
.project-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
}
.project-info {
  flex: 1;
}
.project-name {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 8rpx;
}
.project-meta {
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.points-tag {
  font-size: 22rpx;
  background: #fff0f3;
  color: #FF6B9D;
  padding: 4rpx 12rpx;
  border-radius: 10rpx;
}
.joint-tag {
  font-size: 20rpx;
  background: #e8f5e9;
  color: #4caf50;
  padding: 4rpx 10rpx;
  border-radius: 10rpx;
}
.consecutive {
  font-size: 22rpx;
  color: #ff9800;
}
.checkin-btn {
  padding: 16rpx 32rpx;
  background: #FF6B9D;
  color: #fff;
  border-radius: 30rpx;
  font-size: 26rpx;
}
.checkin-btn.checked {
  background: #e0e0e0;
  color: #999;
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
.bottom-actions {
  position: fixed;
  bottom: 110rpx;
  left: 0;
  right: 0;
  display: flex;
  gap: 16rpx;
  padding: 20rpx;
  background: #fff;
  z-index: 100;
}
.action-btn {
  flex: 1;
  text-align: center;
  padding: 24rpx;
  background: #FF6B9D;
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
}
.action-btn.secondary {
  background: #f5f5f5;
  color: #666;
}
.dialog-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.dialog {
  background: #fff;
  border-radius: 16rpx;
  padding: 40rpx;
  width: 80%;
}
.dialog-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 30rpx;
  text-align: center;
}
.dialog-input {
  border: 1rpx solid #eee;
  padding: 16rpx 20rpx;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
  font-size: 28rpx;
}
.dialog-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  font-size: 28rpx;
}
.small-input {
  width: 120rpx;
  border: 1rpx solid #eee;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  text-align: center;
  font-size: 28rpx;
}
.dialog-btns {
  display: flex;
  gap: 20rpx;
  margin-top: 30rpx;
}
.dialog-btn {
  flex: 1;
  text-align: center;
  padding: 18rpx;
  border-radius: 30rpx;
  font-size: 28rpx;
}
.dialog-btn.cancel {
  background: #f5f5f5;
  color: #666;
}
.dialog-btn.confirm {
  background: #FF6B9D;
  color: #fff;
}
</style>
