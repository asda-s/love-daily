<template>
  <view class="send-container">
    <!-- 表单 -->
    <view class="form-area">
      <view class="form-item">
        <text class="label">悄悄话内容</text>
        <textarea 
          class="textarea" 
          v-model="formData.content" 
          placeholder="写下你想对TA说的话..." 
          maxlength="1000"
        />
      </view>

      <view class="form-item switch-item">
        <text class="label">定时发送</text>
        <switch 
          :checked="formData.is_scheduled" 
          @change="formData.is_scheduled = $event.detail.value"
          color="#FF6B9D"
        />
      </view>

      <view v-if="formData.is_scheduled" class="form-item">
        <text class="label">发送时间</text>
        <picker mode="multiSelector" :range="timeRange" :value="timeValue" @change="onTimeChange">
          <view class="picker-value">
            <text>{{ scheduledTimeStr || '请选择发送时间' }}</text>
            <uni-icons type="right" size="16" color="#999"></uni-icons>
          </view>
        </picker>
      </view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-area">
      <button 
        class="btn-submit" 
        :loading="loading" 
        @click="handleSubmit"
      >
        {{ formData.is_scheduled ? '设置定时发送' : '立即发送' }}
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { post } from '@/utils/request'
import { formatDate } from '@/utils/common'

// 表单数据
const formData = reactive({
  content: '',
  is_scheduled: false,
  scheduled_time: ''
})

// 加载状态
const loading = ref(false)

// 时间选择器数据
const now = new Date()
const timeRange = [
  Array.from({ length: 7 }, (_, i) => {
    const date = new Date(now.getTime() + i * 24 * 60 * 60 * 1000)
    return formatDate(date, 'MM月DD日')
  }),
  Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}时`),
  Array.from({ length: 60 }, (_, i) => `${String(i).padStart(2, '0')}分`)
]
const timeValue = ref([0, now.getHours(), now.getMinutes()])

// 定时发送时间显示
const scheduledTimeStr = computed(() => {
  if (!formData.is_scheduled) return ''
  const date = new Date(now.getTime() + timeValue.value[0] * 24 * 60 * 60 * 1000)
  const hours = String(timeValue.value[1]).padStart(2, '0')
  const minutes = String(timeValue.value[2]).padStart(2, '0')
  return `${formatDate(date, 'YYYY年MM月DD日')} ${hours}:${minutes}`
})

/**
 * 时间选择
 */
function onTimeChange(e) {
  timeValue.value = e.detail.value
  const date = new Date(now.getTime() + timeValue.value[0] * 24 * 60 * 60 * 1000)
  const hours = String(timeValue.value[1]).padStart(2, '0')
  const minutes = String(timeValue.value[2]).padStart(2, '0')
  formData.scheduled_time = `${formatDate(date, 'YYYY-MM-DD')} ${hours}:${minutes}:00`
}

/**
 * 提交表单
 */
async function handleSubmit() {
  // 表单验证
  if (!formData.content) {
    uni.showToast({ title: '请输入悄悄话内容', icon: 'none' })
    return
  }
  if (formData.is_scheduled && !formData.scheduled_time) {
    uni.showToast({ title: '请选择发送时间', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await post('/memory/whisper', formData)
    uni.showToast({ 
      title: formData.is_scheduled ? '已设置定时发送' : '发送成功', 
      icon: 'success' 
    })
    
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (e) {
    console.error('发送失败', e)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.send-container {
  min-height: 100vh;
  background: #f8f8f8;
  padding-bottom: 40rpx;
}

.form-area {
  margin: 20rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  overflow: hidden;
}

.form-item {
  padding: 24rpx;
  border-bottom: 1rpx solid #f5f5f5;

  &:last-child {
    border-bottom: none;
  }
}

.label {
  font-size: 28rpx;
  color: #333333;
  font-weight: 500;
  margin-bottom: 16rpx;
  display: block;
}

.textarea {
  width: 100%;
  height: 300rpx;
  font-size: 28rpx;
  line-height: 1.6;
}

.switch-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.picker-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 80rpx;
  font-size: 28rpx;
  color: #333333;
}

.submit-area {
  margin: 40rpx 20rpx;
}

.btn-submit {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #FF6B9D;
  color: #FFFFFF;
  font-size: 32rpx;
  border-radius: 16rpx;
  border: none;

  &:active {
    opacity: 0.8;
  }
}
</style>
