<template>
  <view class="todo-edit-page">
    <view class="form-section">
      <view class="form-item">
        <text class="label">标题</text>
        <input class="input" v-model="form.title" placeholder="待办事项内容" />
      </view>
      <view class="form-item">
        <text class="label">描述</text>
        <textarea class="textarea" v-model="form.description" placeholder="详细描述（可选）" />
      </view>
      <view class="form-item">
        <text class="label">范围</text>
        <view class="radio-group">
          <view class="radio" :class="{ active: form.scope === 'personal' }" @click="form.scope = 'personal'">个人</view>
          <view class="radio" :class="{ active: form.scope === 'couple' }" @click="form.scope = 'couple'">情侣</view>
        </view>
      </view>
      <view class="form-item">
        <text class="label">优先级</text>
        <view class="radio-group">
          <view class="radio" :class="{ active: form.priority === 1 }" @click="form.priority = 1">高</view>
          <view class="radio" :class="{ active: form.priority === 2 }" @click="form.priority = 2">中</view>
          <view class="radio" :class="{ active: form.priority === 3 }" @click="form.priority = 3">低</view>
        </view>
      </view>
      <view class="form-item">
        <text class="label">截止日期</text>
        <picker mode="date" :value="form.due_date" @change="form.due_date = $event.detail.value">
          <view class="picker-value">{{ form.due_date || '请选择（可选）' }}</view>
        </picker>
      </view>
    </view>
    <view class="btn-group">
      <view class="submit-btn" @click="onSubmit">{{ isEdit ? '修改' : '创建' }}</view>
      <view class="delete-btn" v-if="isEdit" @click="onDelete">删除</view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, post, put, del } from '@/utils/request'

const form = ref({
  title: '',
  description: '',
  scope: 'personal',
  priority: 2,
  due_date: ''
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
})

const loadRecord = async () => {
  try {
    const res = await get(`/life/todo/${recordId.value}`)
    if (res && res.data) {
      form.value = {
        title: res.data.title,
        description: res.data.description || '',
        scope: res.data.scope,
        priority: res.data.priority,
        due_date: res.data.due_date || ''
      }
    }
  } catch (e) {
    console.error('加载待办失败', e)
  }
}

const onSubmit = async () => {
  if (!form.value.title.trim()) {
    uni.showToast({ title: '请输入标题', icon: 'none' })
    return
  }

  try {
    if (isEdit.value) {
      const res = await put(`/life/todo/${recordId.value}`, form.value)
      if (res) {
        uni.showToast({ title: '修改成功' })
        setTimeout(() => uni.navigateBack(), 1000)
      }
    } else {
      const res = await post('/life/todo', form.value)
      if (res) {
        uni.showToast({ title: '创建成功' })
        setTimeout(() => uni.navigateBack(), 1000)
      }
    }
  } catch (e) {}
}

const onDelete = async () => {
  uni.showModal({
    title: '确认',
    content: '确定删除此待办？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/life/todo/${recordId.value}`)
          uni.showToast({ title: '已删除' })
          setTimeout(() => uni.navigateBack(), 1000)
        } catch (e) {}
      }
    }
  })
}
</script>

<style scoped>
.todo-edit-page {
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
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}
.label {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 16rpx;
  display: block;
}
.input {
  font-size: 28rpx;
}
.textarea {
  width: 100%;
  font-size: 28rpx;
  min-height: 120rpx;
}
.radio-group {
  display: flex;
  gap: 20rpx;
}
.radio {
  padding: 12rpx 32rpx;
  border: 1rpx solid #ddd;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #666;
}
.radio.active {
  background: #FF6B9D;
  border-color: #FF6B9D;
  color: #fff;
}
.picker-value {
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
