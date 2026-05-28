<template>
  <view class="diet-page">
    <view class="my-preference">
      <view class="section-title">我的饮食偏好</view>
      <view class="form-section">
        <view class="form-item">
          <text class="label">喜欢的食物</text>
          <input class="input" v-model="myPreference.liked_food" placeholder="如：火锅、奶茶" />
        </view>
        <view class="form-item">
          <text class="label">忌口食物</text>
          <input class="input" v-model="myPreference.avoid_food" placeholder="如：香菜、苦瓜" />
        </view>
        <view class="form-item">
          <text class="label">过敏食物</text>
          <input class="input" v-model="myPreference.allergic_food" placeholder="如：海鲜、花生" />
        </view>
        <view class="form-item">
          <text class="label">咖啡偏好</text>
          <input class="input" v-model="myPreference.coffee_pref" placeholder="如：美式、拿铁、不喝咖啡" />
        </view>
        <view class="form-item">
          <text class="label">外卖地址</text>
          <input class="input" v-model="myPreference.delivery_address" placeholder="常用外卖配送地址" />
        </view>
        <view class="form-item">
          <text class="label">备注</text>
          <input class="input" v-model="myPreference.note" placeholder="其他饮食偏好" />
        </view>
        <view class="save-btn" @click="saveMyPreference">保存</view>
      </view>
    </view>

    <view class="lover-preference" v-if="loverPreference">
      <view class="section-title">TA的饮食偏好</view>
      <view class="info-card">
        <view class="info-row">
          <text class="info-label">喜欢的食物</text>
          <text class="info-value">{{ loverPreference.liked_food || '未设置' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">忌口食物</text>
          <text class="info-value">{{ loverPreference.avoid_food || '无' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">过敏食物</text>
          <text class="info-value">{{ loverPreference.allergic_food || '无' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">咖啡偏好</text>
          <text class="info-value">{{ loverPreference.coffee_pref || '未设置' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">外卖地址</text>
          <text class="info-value">{{ loverPreference.delivery_address || '未设置' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, post } from '@/utils/request'
import { useUserStore } from '@/store/user.js'

const userStore = useUserStore()
const myPreference = ref({
  liked_food: '',
  avoid_food: '',
  allergic_food: '',
  coffee_pref: '',
  delivery_address: '',
  note: ''
})
const loverPreference = ref(null)

onMounted(() => {
  loadData()
})

const loadData = async () => {
  try {
    const mine = await get('/life/diet')
    if (mine && mine.data) {
      myPreference.value = {
        liked_food: mine.data.liked_food || '',
        avoid_food: mine.data.avoid_food || '',
        allergic_food: mine.data.allergic_food || '',
        coffee_pref: mine.data.coffee_pref || '',
        delivery_address: mine.data.delivery_address || '',
        note: mine.data.note || ''
      }
    }
  } catch (e) {
    console.error('加载饮食偏好失败', e)
  }
  if (userStore.userInfo?.lover_id) {
    try {
      const lover = await get(`/life/diet/${userStore.userInfo.lover_id}`)
      if (lover && lover.data) {
        loverPreference.value = lover.data
      }
    } catch (e) {
      console.error('加载TA的偏好失败', e)
    }
  }
}

const saveMyPreference = async () => {
  try {
    await post('/life/diet', myPreference.value)
    uni.showToast({ title: '保存成功' })
  } catch (e) {}
}
</script>

<style scoped>
.diet-page {
  background: #FFF5F9;
  min-height: 100vh;
  padding: 20rpx;
}
.section-title {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}
.form-section {
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx 30rpx;
}
.form-item {
  padding: 20rpx 0;
  border-bottom: 1rpx solid #FFF5F9;
}
.label {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 16rpx;
  display: block;
}
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.tag {
  padding: 10rpx 24rpx;
  border: 1rpx solid #ddd;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #666;
}
.tag.active {
  background: #FF69B4;
  border-color: #FF69B4;
  color: #fff;
}
.input {
  font-size: 28rpx;
  padding: 10rpx 0;
}
.save-btn {
  background: #FF69B4;
  color: #fff;
  text-align: center;
  padding: 24rpx;
  border-radius: 40rpx;
  margin-top: 30rpx;
  font-size: 30rpx;
}
.lover-preference {
  margin-top: 30rpx;
}
.info-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx 30rpx;
}
.info-row {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #FFF5F9;
}
.info-label {
  color: #666;
  font-size: 28rpx;
}
.info-value {
  font-size: 28rpx;
  max-width: 400rpx;
  text-align: right;
}
</style>
