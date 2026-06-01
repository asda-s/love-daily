<template>
  <view class="todo-edit-page">
    <view class="form-section">
      <view class="form-item">
        <text class="label">标题</text>
        <input class="input" v-model="form.title" placeholder="待办事项内容" />
      </view>
      <view class="form-item">
        <text class="label">备注</text>
        <textarea class="textarea" v-model="form.note" placeholder="详细描述（可选）" />
      </view>
      <view class="form-item">
        <text class="label">类型</text>
        <view class="radio-group">
          <view class="radio" :class="{ active: form.type === 'personal' }" @click="form.type = 'personal'">个人</view>
          <view class="radio" :class="{ active: form.type === 'couple' }" @click="form.type = 'couple'">情侣</view>
        </view>
      </view>
      <view class="form-item">
        <text class="label">截止日期</text>
        <picker mode="date" :value="form.deadline" @change="form.deadline = $event.detail.value">
          <view class="picker-value">{{ form.deadline || '请选择（可选）' }}</view>
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
  note: '',
  type: 'personal',
  deadline: ''
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
        note: res.data.note || '',
        type: res.data.type || 'personal',
        deadline: res.data.deadline ? res.data.deadline.split(' ')[0] : ''
      }
    }
  } catch (e) {
    console.error('加载待办失败', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

const onSubmit = async () => {
  if (!form.value.title.trim()) {
    uni.showToast({ title: '请输入标题', icon: 'none' })
    return
  }

  try {
    const payload = {
      title: form.value.title,
      note: form.value.note || null,
      type: form.value.type,
      deadline: form.value.deadline ? form.value.deadline + ' 00:00:00' : null
    }
    if (isEdit.value) {
      const res = await put(`/life/todo/${recordId.value}`, payload)
      if (res) {
        uni.showToast({ title: '修改成功' })
        setTimeout(() => uni.navigateBack(), 1000)
      }
    } else {
      const res = await post('/life/todo', payload)
      if (res) {
        uni.showToast({ title: '创建成功' })
        setTimeout(() => uni.navigateBack(), 1000)
      }
    }
  } catch (e) {
    uni.showToast({ title: '保存失败，请重试', icon: 'none' })
  }
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
        } catch (e) {
          uni.showToast({ title: '删除失败，请重试', icon: 'none' })
        }
      }
    }
  })
}
</script>

<style scoped>
.todo-edit-page {
  background: #FFF5F9;
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
  border-bottom: 1rpx solid #FFF5F9;
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
  background: #FF69B4;
  border-color: #FF69B4;
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
  background: #FF69B4;
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
