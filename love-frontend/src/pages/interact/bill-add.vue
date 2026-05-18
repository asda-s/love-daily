<template>
  <view class="bill-add-page">
    <view class="form-section">
      <view class="form-item">
        <text class="label">金额</text>
        <input class="input amount" type="digit" v-model="form.amount" placeholder="0.00" />
      </view>
      <view class="form-item">
        <text class="label">类型</text>
        <view class="type-grid">
          <view class="type-item" v-for="(name, key) in typeNames" :key="key" :class="{ active: form.type === key }" @click="form.type = key">{{ name }}</view>
        </view>
      </view>
      <view class="form-item">
        <text class="label">支付人</text>
        <view class="radio-group">
          <view class="radio" :class="{ active: form.payer === 'me' }" @click="form.payer = 'me'">我</view>
          <view class="radio" :class="{ active: form.payer === 'lover' }" @click="form.payer = 'lover'">TA</view>
          <view class="radio" :class="{ active: form.payer === 'aa' }" @click="form.payer = 'aa'">AA</view>
        </view>
      </view>
      <view class="form-item">
        <text class="label">日期</text>
        <picker mode="date" :value="form.date" @change="form.date = $event.detail.value">
          <view class="picker-value">{{ form.date }}</view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">备注</text>
        <input class="input" v-model="form.note" placeholder="可选" />
      </view>
    </view>
    <view class="submit-btn" @click="onSubmit">保存</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { post } from '@/utils/request'

const today = new Date().toISOString().slice(0, 10)
const typeNames = { food: '餐饮', travel: '旅行', gift: '礼物', daily: '日常', other: '其他' }
const form = ref({ amount: '', type: 'food', payer: 'me', date: today, note: '', is_aa: false })

const onSubmit = async () => {
  if (!form.value.amount || parseFloat(form.value.amount) <= 0) {
    uni.showToast({ title: '请输入金额', icon: 'none' })
    return
  }
  try {
    const data = {
      amount: parseFloat(form.value.amount),
      type: form.value.type,
      payer: form.value.payer,
      pay_time: form.value.date + 'T00:00:00',
      note: form.value.note,
      is_aa: form.value.payer === 'aa'
    }
    const res = await post('/interact/bill', data)
    if (res) {
      uni.showToast({ title: '记录成功' })
      setTimeout(() => uni.navigateBack(), 1000)
    }
  } catch (e) {}
}
</script>

<style scoped>
.bill-add-page { background: #f5f5f5; min-height: 100vh; padding: 20rpx; }
.form-section { background: #fff; border-radius: 16rpx; padding: 10rpx 30rpx; }
.form-item { padding: 24rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.label { font-size: 26rpx; color: #666; margin-bottom: 16rpx; display: block; }
.input { font-size: 28rpx; }
.input.amount { font-size: 48rpx; font-weight: bold; color: #333; }
.type-grid { display: flex; gap: 16rpx; flex-wrap: wrap; }
.type-item { padding: 12rpx 24rpx; border: 1rpx solid #ddd; border-radius: 30rpx; font-size: 26rpx; color: #666; }
.type-item.active { background: #FF6B9D; border-color: #FF6B9D; color: #fff; }
.radio-group { display: flex; gap: 20rpx; }
.radio { padding: 12rpx 32rpx; border: 1rpx solid #ddd; border-radius: 30rpx; font-size: 26rpx; color: #666; }
.radio.active { background: #FF6B9D; border-color: #FF6B9D; color: #fff; }
.picker-value { font-size: 28rpx; color: #333; }
.submit-btn { background: #FF6B9D; color: #fff; text-align: center; padding: 24rpx; border-radius: 40rpx; font-size: 30rpx; margin-top: 40rpx; }
</style>
