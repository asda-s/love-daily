<template>
  <view class="publish-container">
    <!-- 表单 -->
    <view class="form-area">
      <view class="form-item">
        <text class="label">标题</text>
        <input 
          class="input" 
          type="text" 
          v-model="formData.title" 
          placeholder="请输入标题" 
          maxlength="100"
        />
      </view>

      <view class="form-item">
        <text class="label">内容</text>
        <textarea 
          class="textarea" 
          v-model="formData.content" 
          placeholder="记录这一刻的心情..." 
          maxlength="1000"
        />
      </view>

      <view class="form-item">
        <text class="label">事件时间</text>
        <picker mode="date" :value="formData.eventDate" @change="onDateChange">
          <view class="picker-value">
            <text>{{ formData.eventDate || '请选择日期' }}</text>
            <uni-icons type="right" size="16" color="#999"></uni-icons>
          </view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">图片</text>
        <view class="image-list">
          <view 
            v-for="(img, index) in formData.images" 
            :key="index" 
            class="image-item"
          >
            <image class="preview" :src="img" mode="aspectFill"></image>
            <view class="delete-btn" @click="deleteImage(index)">
              <uni-icons type="clear" size="20" color="#FF69B4"></uni-icons>
            </view>
          </view>
          
          <view v-if="formData.images.length < 9" class="add-image" @click="chooseImage">
            <uni-icons type="plusempty" size="32" color="#999"></uni-icons>
          </view>
        </view>
      </view>

      <view class="form-item switch-item">
        <text class="label">同步给情侣</text>
        <switch 
          :checked="formData.isSync" 
          @change="formData.isSync = $event.detail.value"
          color="#FF69B4"
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
        {{ editId ? '保存修改' : '发布' }}
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { get, post, put } from '@/utils/request'
import { formatDate } from '@/utils/common'
import { getToken } from '@/utils/auth'

const editId = ref(null)
const formData = reactive({
  title: '',
  content: '',
  eventDate: formatDate(new Date(), 'YYYY-MM-DD'),
  images: [],
  isSync: true
})

const loading = ref(false)

onMounted(async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  if (currentPage.options.id) {
    editId.value = currentPage.options.id
    try {
      const res = await get(`/memory/timeline/${editId.value}`)
      if (res && res.data) {
        const d = res.data
        formData.title = d.title || ''
        formData.content = d.content || ''
        formData.eventDate = d.event_time ? d.event_time.split(' ')[0] : formatDate(new Date(), 'YYYY-MM-DD')
        formData.images = d.images || []
        formData.isSync = d.is_sync !== false
      }
    } catch (e) {
      console.error('加载详情失败', e)
      uni.showToast({ title: '加载失败', icon: 'none' })
    }
  }
})

function onDateChange(e) {
  formData.eventDate = e.detail.value
}

function chooseImage() {
  const remaining = 9 - formData.images.length
  uni.chooseImage({
    count: remaining,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const token = getToken()
      if (!token) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        return
      }
      uni.showLoading({ title: '上传中...', mask: true })
      try {
        const uploadedUrls = []
        for (const filePath of res.tempFilePaths) {
          const uploadRes = await new Promise((resolve, reject) => {
            uni.uploadFile({
              url: `${import.meta.env.VITE_API_BASE_URL || ''}/memory/upload`,
              filePath: filePath,
              name: 'file',
              header: { Authorization: `Bearer ${token}` },
              success: (r) => {
                if (r.statusCode === 200) {
                  const data = JSON.parse(r.data)
                  if (data.code === 200) resolve(data)
                  else reject(new Error(data.message || '上传失败'))
                } else {
                  reject(new Error('上传失败'))
                }
              },
              fail: (err) => reject(new Error(err.errMsg || '网络连接失败'))
            })
          })
          uploadedUrls.push(uploadRes.data.url)
        }
        formData.images = [...formData.images, ...uploadedUrls]
        uni.hideLoading()
      } catch (e) {
        uni.hideLoading()
        uni.showToast({ title: e.message || '图片上传失败', icon: 'none' })
      }
    }
  })
}

function deleteImage(index) {
  formData.images.splice(index, 1)
}

async function handleSubmit() {
  if (!formData.title) {
    uni.showToast({ title: '请输入标题', icon: 'none' })
    return
  }
  if (!formData.eventDate) {
    uni.showToast({ title: '请选择事件时间', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const payload = {
      title: formData.title,
      content: formData.content,
      event_time: formData.eventDate + ' 00:00:00',
      images: JSON.stringify(formData.images),
      is_sync: formData.isSync
    }
    if (editId.value) {
      await put(`/memory/timeline/${editId.value}`, payload)
      uni.showToast({ title: '修改成功', icon: 'success' })
    } else {
      await post('/memory/timeline', payload)
      uni.showToast({ title: '发布成功', icon: 'success' })
    }
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (e) {
    console.error('提交失败', e)
    uni.showToast({ title: '提交失败，请重试', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.publish-container {
  min-height: 100vh;
  background: #FFF5F9;
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
  height: 200rpx;
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

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.image-item {
  position: relative;
  width: 200rpx;
  height: 200rpx;
}

.preview {
  width: 100%;
  height: 100%;
  border-radius: 8rpx;
}

.delete-btn {
  position: absolute;
  top: -10rpx;
  right: -10rpx;
  width: 40rpx;
  height: 40rpx;
  background: #FFFFFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-image {
  width: 200rpx;
  height: 200rpx;
  border: 2rpx dashed #DDDDDD;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.switch-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

  &:active {
    opacity: 0.8;
  }
}
</style>
