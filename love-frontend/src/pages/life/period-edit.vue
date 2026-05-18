<template>
  <view class="period-edit-page">
    <view class="form-section">
      <view class="form-item">
        <text class="label">开始日期</text>
        <picker mode="date" :value="form.start_date" @change="onStartDateChange">
          <view class="picker-value">{{ form.start_date || '请选择' }}</view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">结束日期</text>
        <picker mode="date" :value="form.end_date" @change="onEndDateChange">
          <view class="picker-value">{{ form.end_date || '请选择' }}</view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">周期天数</text>
        <input class="input" type="number" v-model="form.cycle_days" placeholder="两次月经间隔天数，默认28" />
      </view>
      <view class="form-item">
        <text class="label">备注</text>
        <input class="input" v-model="form.note" placeholder="可选，记录感受等" />
      </view>
    </view>
    <view class="btn-group">
      <view class="submit-btn" @click="onSubmit">保存</view>
      <view class="delete-btn" v-if="isEdit" @click="onDelete">删除</view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, post, put, del } from '@/utils/request'

const form = ref({
  start_date: '',
  end_date: '',
  cycle_days: '28',
  note: ''
})
const isEdit = ref(false)
const recordId = ref(null)

onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1]
  if (page.options && page.options.id) {
    isEdit.value = true
    recordId.value = page.options.id
    loadRecord()
  }
  if (page.options && page.options.date) {
    form.value.start_date = page.options.date
    form.value.end_date = page.options.date
  }
})

const loadRecord = async () => {
  try {
    const res = await get(`/life/period/${recordId.value}`)
    if (res && res.data) {
      form.value.start_date = res.data.start_date
      form.value.end_date = res.data.end_date
      form.value.cycle_days = String(res.data.cycle_days || 28)
      form.value.note = res.data.note || ''
    }
  } catch (e) {
    console.error('加载经期记录失败', e)
  }
}

const onStartDateChange = (e) => {
  form.value.start_date = e.detail.value
}

const onEndDateChange = (e) => {
  form.value.end_date = e.detail.value
}

const onSubmit = async () => {
  if (!form.value.start_date || !form.value.end_date) {
    uni.showToast({ title: '请选择日期', icon: 'none' })
    return
  }
  if (form.value.start_date > form.value.end_date) {
    uni.showToast({ title: '结束日期不能早于开始日期', icon: 'none' })
    return
  }

  const start = new Date(form.value.start_date)
  const end = new Date(form.value.end_date)
  const duration_days = Math.round((end - start) / 86400000) + 1
  const cycle_days = parseInt(form.value.cycle_days) || 28

  const payload = {
    start_date: form.value.start_date,
    cycle_days,
    duration_days,
    note: form.value.note || null
  }

  try {
    if (isEdit.value) {
      const res = await put(`/life/period/${recordId.value}`, payload)
      if (res) {
        uni.showToast({ title: '修改成功' })
        setTimeout(() => uni.navigateBack(), 1000)
      }
    } else {
      const res = await post('/life/period', payload)
      if (res) {
        uni.showToast({ title: '记录成功' })
        setTimeout(() => uni.navigateBack(), 1000)
      }
    }
  } catch (e) {}
}

const onDelete = async () => {
  uni.showModal({
    title: '确认',
    content: '确定删除此记录？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/life/period/${recordId.value}`)
          uni.showToast({ title: '已删除' })
          setTimeout(() => uni.navigateBack(), 1000)
        } catch (e) {}
      }
    }
  })
}
</script>

<style scoped>
.period-edit-page {
  background: #f5f5f5;
  min-height: 100vh;
  padding: 20rpx;
}
.form-section {
  background: #fff;
  border-radius: 16rpx;
  padding: 10rpx 30rpx;
}
.form-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}
.label {
  width: 160rpx;
  font-size: 28rpx;
  color: #333;
}
.picker-value, .input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}
.btn-group {
  margin-top: 40rpx;
}
.submit-btn {
  background: #FF6B9D;
  color: #fff;
  text-align: center;
  padding: 24rpx;
  border-radius: 40rpx;
  font-size: 30rpx;
}
.delete-btn {
  text-align: center;
  padding: 24rpx;
  color: #ff4d4f;
  font-size: 28rpx;
  margin-top: 20rpx;
}
</style>
