<template>
  <view class="item-edit-page">
    <view class="form-section">
      <view class="form-item">
        <text class="label">物品名称</text>
        <input class="input" v-model="form.name" placeholder="请输入物品名称" />
      </view>
      <view class="form-item">
        <text class="label">分类</text>
        <picker :range="categoryOptions" :value="categoryIndex" @change="onCategoryChange">
          <view class="picker-value">{{ categoryOptions[categoryIndex] }}</view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">数量</text>
        <input class="input" type="number" v-model="form.quantity" placeholder="1" />
      </view>
      <view class="form-item">
        <text class="label">存放位置</text>
        <input class="input" v-model="form.location" placeholder="如：冰箱、卧室" />
      </view>
      <view class="form-item">
        <text class="label">到期日期</text>
        <picker mode="date" :value="form.expiry_date" @change="form.expiry_date = $event.detail.value">
          <view class="picker-value">{{ form.expiry_date || '请选择（可选）' }}</view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">备注</text>
        <input class="input" v-model="form.note" placeholder="可选" />
      </view>
    </view>
    <view class="btn-group">
      <view class="submit-btn" @click="onSubmit">{{ isEdit ? '修改' : '添加' }}</view>
      <view class="delete-btn" v-if="isEdit" @click="onDelete">删除</view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { get, post, put, del } from '@/utils/request'

const categoryOptions = ['食品', '日用品', '药品', '其他']
const form = ref({
  name: '',
  category: '食品',
  quantity: 1,
  location: '',
  expiry_date: '',
  note: ''
})
const categoryIndex = ref(0)
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
    const res = await get(`/life/item/${recordId.value}`)
    if (res && res.data) {
      form.value = {
        name: res.data.name,
        category: res.data.category,
        quantity: res.data.quantity,
        location: res.data.location || '',
        expiry_date: res.data.expiry_date || '',
        note: res.data.note || ''
      }
      categoryIndex.value = categoryOptions.indexOf(res.data.category)
    }
  } catch (e) {
    console.error('加载物品失败', e)
  }
}

const onCategoryChange = (e) => {
  categoryIndex.value = e.detail.value
  form.value.category = categoryOptions[e.detail.value]
}

const onSubmit = async () => {
  if (!form.value.name.trim()) {
    uni.showToast({ title: '请输入物品名称', icon: 'none' })
    return
  }
  form.value.quantity = parseInt(form.value.quantity) || 1
  form.value.category = categoryOptions[categoryIndex.value]

  try {
    if (isEdit.value) {
      const res = await put(`/life/item/${recordId.value}`, form.value)
      if (res) {
        uni.showToast({ title: '修改成功' })
        setTimeout(() => uni.navigateBack(), 1000)
      }
    } else {
      const res = await post('/life/item', form.value)
      if (res) {
        uni.showToast({ title: '添加成功' })
        setTimeout(() => uni.navigateBack(), 1000)
      }
    }
  } catch (e) {}
}

const onDelete = async () => {
  uni.showModal({
    title: '确认',
    content: '确定删除此物品？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/life/item/${recordId.value}`)
          uni.showToast({ title: '已删除' })
          setTimeout(() => uni.navigateBack(), 1000)
        } catch (e) {}
      }
    }
  })
}
</script>

<style scoped>
.item-edit-page {
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
.input, .picker-value {
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
