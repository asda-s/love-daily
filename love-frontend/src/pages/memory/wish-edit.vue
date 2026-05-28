<template>
  <view class="edit-container">
    <!-- 表单 -->
    <view class="form-area">
      <view class="form-item">
        <text class="label">心愿内容</text>
        <textarea 
          class="textarea" 
          v-model="formData.content" 
          placeholder="写下你的心愿..." 
          maxlength="200"
        />
      </view>

      <view class="form-item">
        <text class="label">类型</text>
        <view class="type-options">
          <view 
            class="type-option"
            :class="{ active: formData.type === 'personal' }"
            @click="formData.type = 'personal'"
          >
            <text>个人心愿</text>
          </view>
          <view 
            class="type-option"
            :class="{ active: formData.type === 'couple' }"
            @click="formData.type = 'couple'"
          >
            <text>情侣心愿</text>
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
        {{ isEdit ? '保存修改' : '许下心愿' }}
      </button>
    </view>

    <!-- 删除按钮 -->
    <view v-if="isEdit" class="delete-area">
      <button class="btn-delete" @click="handleDelete">删除心愿</button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { get, post, put, del } from '@/utils/request'

// 是否为编辑模式
const isEdit = ref(false)
const wishId = ref('')

// 表单数据
const formData = reactive({
  content: '',
  type: 'personal',
  note: ''
})

// 加载状态
const loading = ref(false)

/**
 * 获取详情
 */
async function fetchDetail() {
  try {
    const res = await get('/memory/wish')
    const wish = res.data.find(item => item.id == wishId.value)
    if (wish) {
      formData.content = wish.content
      formData.type = wish.type
      formData.note = wish.note || ''
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
  if (!formData.content) {
    uni.showToast({ title: '请输入心愿内容', icon: 'none' })
    return
  }

  loading.value = true
  try {
    if (isEdit.value) {
      await put(`/memory/wish/${wishId.value}`, formData)
      uni.showToast({ title: '修改成功！', icon: 'success' })
    } else {
      await post('/memory/wish', formData)
      uni.showToast({ title: '许愿成功！', icon: 'success' })
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
 * 删除心愿
 */
function handleDelete() {
  uni.showModal({
    title: '提示',
    content: '确定要删除这个心愿吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/memory/wish/${wishId.value}`)
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
  wishId.value = currentPage.options.id
  
  if (wishId.value) {
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

.textarea {
  width: 100%;
  height: 150rpx;
  font-size: 28rpx;
  line-height: 1.6;
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
