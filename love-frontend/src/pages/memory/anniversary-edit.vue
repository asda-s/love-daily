<template>
  <view class="edit-container">
    <!-- 表单 -->
    <view class="form-area">
      <view class="form-item">
        <text class="label">纪念日标题</text>
        <input 
          class="input" 
          type="text" 
          v-model="formData.title" 
          placeholder="请输入标题" 
          maxlength="100"
        />
      </view>

      <view class="form-item">
        <text class="label">目标日期</text>
        <picker mode="date" :value="formData.target_date" @change="onDateChange">
          <view class="picker-value">
            <text>{{ formData.target_date || '请选择日期' }}</text>
            <uni-icons type="right" size="16" color="#999"></uni-icons>
          </view>
        </picker>
      </view>

      <view class="form-item switch-item">
        <text class="label">每年循环</text>
        <switch 
          :checked="formData.is_yearly" 
          @change="formData.is_yearly = $event.detail.value"
          color="#FF69B4"
        />
      </view>

      <view class="form-item">
        <text class="label">提前提醒天数</text>
        <view class="remind-days">
          <view 
            v-for="day in [1, 3, 7, 14, 30]" 
            :key="day"
            class="day-option"
            :class="{ active: formData.remind_days === day }"
            @click="formData.remind_days = day"
          >
            <text>{{ day }}天</text>
          </view>
        </view>
      </view>

      <view class="form-item">
        <text class="label">类型</text>
        <view class="type-options">
          <view 
            class="type-option"
            :class="{ active: formData.type === 'personal' }"
            @click="formData.type = 'personal'"
          >
            <text>个人纪念日</text>
          </view>
          <view 
            class="type-option"
            :class="{ active: formData.type === 'couple' }"
            @click="formData.type = 'couple'"
          >
            <text>情侣纪念日</text>
          </view>
        </view>
      </view>

      <view class="form-item">
        <text class="label">备注</text>
        <textarea 
          class="textarea" 
          v-model="formData.note" 
          placeholder="添加备注..." 
          maxlength="500"
        />
      </view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-area">
      <button 
        class="btn-submit" 
        :loading="loading" 
        @click="handleSubmit"
      >
        {{ isEdit ? '保存修改' : '创建纪念日' }}
      </button>
    </view>

    <!-- 删除按钮 -->
    <view v-if="isEdit" class="delete-area">
      <button class="btn-delete" @click="handleDelete">删除纪念日</button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { get, post, put, del } from '@/utils/request'
import { formatDate } from '@/utils/common'

// 是否为编辑模式
const isEdit = ref(false)
const anniversaryId = ref('')

// 表单数据
const formData = reactive({
  title: '',
  target_date: formatDate(new Date(), 'YYYY-MM-DD'),
  is_yearly: false,
  remind_days: 3,
  type: 'personal',
  note: ''
})

// 加载状态
const loading = ref(false)

/**
 * 日期选择
 */
function onDateChange(e) {
  formData.target_date = e.detail.value
}

/**
 * 获取详情
 */
async function fetchDetail() {
  try {
    const res = await get('/memory/anniversary')
    const anniversary = res.data.find(item => item.id == anniversaryId.value)
    if (anniversary) {
      formData.title = anniversary.title
      formData.target_date = anniversary.target_date
      formData.is_yearly = anniversary.is_yearly
      formData.remind_days = anniversary.remind_days
      formData.type = anniversary.type
      formData.note = anniversary.note || ''
    }
  } catch (e) {
    console.error('获取详情失败', e)
  }
}

/**
 * 提交表单
 */
async function handleSubmit() {
  // 表单验证
  if (!formData.title) {
    uni.showToast({ title: '请输入标题', icon: 'none' })
    return
  }
  if (!formData.target_date) {
    uni.showToast({ title: '请选择日期', icon: 'none' })
    return
  }

  loading.value = true
  try {
    if (isEdit.value) {
      await put(`/memory/anniversary/${anniversaryId.value}`, formData)
      uni.showToast({ title: '修改成功', icon: 'success' })
    } else {
      await post('/memory/anniversary', formData)
      uni.showToast({ title: '创建成功', icon: 'success' })
    }
    
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (e) {
    console.error('提交失败', e)
  } finally {
    loading.value = false
  }
}

/**
 * 删除纪念日
 */
function handleDelete() {
  uni.showModal({
    title: '提示',
    content: '确定要删除这个纪念日吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/memory/anniversary/${anniversaryId.value}`)
          uni.showToast({ title: '删除成功', icon: 'success' })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        } catch (e) {
          console.error('删除失败', e)
        }
      }
    }
  })
}

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  anniversaryId.value = currentPage.options.id
  
  if (anniversaryId.value) {
    isEdit.value = true
    fetchDetail()
  }
})
</script>

<style lang="scss" scoped>
.edit-container {
  min-height: 100vh;
  background: transparent;
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
  border-bottom: 1rpx solid #FFF5F9;

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

.input {
  width: 100%;
  height: 80rpx;
  font-size: 28rpx;
}

.textarea {
  width: 100%;
  height: 150rpx;
  font-size: 28rpx;
  line-height: 1.6;
}

.picker-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 80rpx;
  font-size: 28rpx;
  color: #333333;
}

.switch-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remind-days {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.day-option {
  padding: 12rpx 24rpx;
  background: #FFF5F9;
  border-radius: 8rpx;
  font-size: 26rpx;
  color: #666666;

  &.active {
    background: #FFE4EC;
    color: #FF69B4;
  }
}

.type-options {
  display: flex;
  gap: 16rpx;
}

.type-option {
  flex: 1;
  padding: 20rpx;
  background: #FFF5F9;
  border-radius: 8rpx;
  text-align: center;
  font-size: 26rpx;
  color: #666666;

  &.active {
    background: #FFE4EC;
    color: #FF69B4;
  }
}

.submit-area {
  margin: 40rpx 20rpx;
}

.btn-submit {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #FF69B4;
  color: #FFFFFF;
  font-size: 32rpx;
  border-radius: 16rpx;
  border: none;
}

.delete-area {
  margin: 0 20rpx;
}

.btn-delete {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #FFFFFF;
  color: #FF69B4;
  font-size: 32rpx;
  border-radius: 16rpx;
  border: 2rpx solid #FF69B4;
}
</style>
