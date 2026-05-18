<template>
  <view class="benefit-page">
    <view class="points-header">
      <text class="points-label">我的心动分</text>
      <text class="points-value">{{ userPoints }}</text>
    </view>
    <scroll-view class="benefit-list" scroll-y refresher-enabled :refresher-triggered="refreshing" @refresherrefresh="onRefresh">
      <view class="benefit-card" v-for="b in benefits" :key="b.id">
        <view class="benefit-info">
          <view class="benefit-name">{{ b.name }}</view>
          <view class="benefit-points">{{ b.points }}分</view>
          <view class="benefit-rule" v-if="b.rule">{{ b.rule }}</view>
        </view>
        <view class="benefit-actions">
          <view class="exchange-btn" :class="{ disabled: !b.can_exchange }" @click="exchange(b)">
            {{ b.can_exchange ? '兑换' : '积分不足' }}
          </view>
          <view class="delete-btn" @click="deleteBenefit(b)">删除</view>
        </view>
      </view>
      <view class="empty" v-if="!benefits.length">
        <text class="empty-icon">🎁</text>
        <text class="empty-text">还没有积分福利</text>
        <text class="empty-hint">创建一个福利，用心动分兑换惊喜吧</text>
      </view>
    </scroll-view>
    <view class="bottom-btns">
      <view class="btn" @click="showAdd = true">+ 创建福利</view>
      <view class="btn secondary" @click="goHistory">兑换记录</view>
    </view>

    <view class="dialog-mask" v-if="showAdd" @click="showAdd = false">
      <view class="dialog" @click.stop>
        <view class="dialog-title">创建积分福利</view>
        <input class="dialog-input" v-model="form.name" placeholder="福利名称" />
        <input class="dialog-input" type="number" v-model="form.points" placeholder="所需心动分" />
        <input class="dialog-input" v-model="form.rule" placeholder="兑换规则（可选）" />
        <view class="dialog-row">
          <text>可重复兑换</text>
          <switch :checked="form.is_repeatable" @change="form.is_repeatable = $event.detail.value" color="#FF6B9D" />
        </view>
        <view class="dialog-btns">
          <view class="dialog-btn cancel" @click="showAdd = false">取消</view>
          <view class="dialog-btn confirm" @click="addBenefit">确定</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, post, del } from '@/utils/request'
import { useUserStore } from '@/store/user.js'

const userStore = useUserStore()
const userPoints = ref(0)
const benefits = ref([])
const showAdd = ref(false)
const refreshing = ref(false)
const form = ref({ name: '', points: 10, rule: '', is_repeatable: false })

onMounted(async () => {
  await userStore.getUserInfoFromServer()
  userPoints.value = userStore.userInfo?.heart_points || 0
  loadBenefits()
})

const loadBenefits = async () => {
  try {
    const res = await get('/interact/benefit')
    if (res && res.data) benefits.value = res.data
  } catch (e) {
    console.error('加载福利失败', e)
  }
}

const exchange = async (benefit) => {
  if (!benefit.can_exchange) return
  uni.showModal({
    title: '确认兑换',
    content: `确定使用${benefit.points}心动分兑换"${benefit.name}"？`,
    success: async (r) => {
      if (r.confirm) {
        try {
          const res = await post(`/interact/benefit/${benefit.id}/exchange`)
          if (res && res.data) {
            uni.showToast({ title: '兑换成功' })
            userPoints.value = res.data.remaining_points
            loadBenefits()
          }
        } catch (e) {}
      }
    }
  })
}

const addBenefit = async () => {
  if (!form.value.name.trim()) {
    uni.showToast({ title: '请输入名称', icon: 'none' })
    return
  }
  try {
    await post('/interact/benefit', form.value)
    uni.showToast({ title: '创建成功' })
    showAdd.value = false
    form.value = { name: '', points: 10, rule: '', is_repeatable: false }
    loadBenefits()
  } catch (e) {}
}

const goHistory = () => {
  uni.navigateTo({ url: '/pages/interact/exchange-history' })
}

async function onRefresh() {
  refreshing.value = true
  await userStore.getUserInfoFromServer()
  userPoints.value = userStore.userInfo?.heart_points || 0
  await loadBenefits()
  refreshing.value = false
}

function deleteBenefit(benefit) {
  uni.showModal({
    title: '确认删除',
    content: '确定删除该福利？',
    confirmColor: '#e43d33',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del('/interact/benefit/' + benefit.id)
          await loadBenefits()
        } catch (e) {}
      }
    }
  })
}
</script>

<style scoped>
.benefit-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 140rpx; }
.points-header { background: linear-gradient(135deg, #FF6B9D, #FF8E53); padding: 40rpx; text-align: center; color: #fff; }
.points-label { font-size: 26rpx; opacity: 0.8; display: block; margin-bottom: 10rpx; }
.points-value { font-size: 56rpx; font-weight: bold; }
.benefit-list { padding: 20rpx; height: calc(100vh - 200rpx); }
.benefit-card { display: flex; align-items: center; background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.benefit-info { flex: 1; }
.benefit-name { font-size: 30rpx; font-weight: bold; }
.benefit-points { font-size: 24rpx; color: #FF6B9D; margin-top: 6rpx; }
.benefit-rule { font-size: 22rpx; color: #999; margin-top: 4rpx; }
.exchange-btn { padding: 12rpx 28rpx; background: #FF6B9D; color: #fff; border-radius: 30rpx; font-size: 24rpx; }
.exchange-btn.disabled { background: #e0e0e0; color: #999; }
.delete-btn { padding: 12rpx 28rpx; background: #ff4d4f; color: #fff; border-radius: 30rpx; font-size: 24rpx; margin-left: 16rpx; }
.empty { text-align: center; padding: 80rpx 40rpx; color: #999; }
.empty-icon { font-size: 80rpx; display: block; margin-bottom: 20rpx; }
.empty-text { font-size: 30rpx; color: #666; display: block; margin-bottom: 12rpx; }
.empty-hint { font-size: 24rpx; color: #bbb; display: block; }
.bottom-btns { position: fixed; bottom: 110rpx; left: 0; right: 0; display: flex; gap: 16rpx; padding: 20rpx; background: #fff; z-index: 100; }
.btn { flex: 1; text-align: center; padding: 24rpx; background: #FF6B9D; color: #fff; border-radius: 40rpx; font-size: 28rpx; }
.btn.secondary { background: #f5f5f5; color: #666; }
.dialog-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.dialog { background: #fff; border-radius: 16rpx; padding: 40rpx; width: 80%; }
.dialog-title { font-size: 32rpx; font-weight: bold; margin-bottom: 30rpx; text-align: center; }
.dialog-input { border: 1rpx solid #eee; padding: 16rpx 20rpx; border-radius: 12rpx; margin-bottom: 20rpx; font-size: 28rpx; }
.dialog-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; font-size: 28rpx; }
.dialog-btns { display: flex; gap: 20rpx; margin-top: 30rpx; }
.dialog-btn { flex: 1; text-align: center; padding: 18rpx; border-radius: 30rpx; font-size: 28rpx; }
.dialog-btn.cancel { background: #f5f5f5; color: #666; }
.dialog-btn.confirm { background: #FF6B9D; color: #fff; }
</style>
