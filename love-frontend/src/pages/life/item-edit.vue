<template>
  <view class="diary-page">
    <!-- Header -->
    <view class="page-header">
      <view class="header-back" @click="onBack">
        <text class="back-icon">&#x2190;</text>
      </view>
      <text class="header-title">{{ isEdit ? '编辑日记' : '写日记' }}</text>
      <view class="header-placeholder"></view>
    </view>

    <!-- Section 0: Date Selection -->
    <view class="section-card">
      <text class="section-label">记录日期</text>
      <picker mode="date" :value="form.diary_date" @change="onDateChange">
        <view class="date-picker">
          <text class="date-icon">📅</text>
          <text class="date-text">{{ form.diary_date || '选择日期' }}</text>
          <text class="date-hint">{{ getDateHint(form.diary_date) }}</text>
        </view>
      </picker>
    </view>

    <!-- Section 1: Mood Selection -->
    <view class="section-card">
      <text class="section-label">此刻心情</text>
      <view class="mood-grid">
        <view
          v-for="(cfg, key) in MOOD_CONFIG"
          :key="key"
          class="mood-item"
          :class="{ active: form.mood_type === key }"
          :style="form.mood_type === key ? { borderColor: cfg.color, background: cfg.bg } : {}"
          @click="selectMood(key)"
        >
          <text class="mood-emoji">{{ cfg.emoji }}</text>
          <text class="mood-name">{{ cfg.name }}</text>
        </view>
      </view>

      <!-- Intensity Slider -->
      <view class="intensity-row">
        <text class="section-label">心情强度</text>
        <view class="intensity-bar">
          <slider
            :min="1"
            :max="5"
            :step="1"
            :value="form.mood_intensity"
            activeColor="#FF69B4"
            backgroundColor="#FFE4EC"
            block-size="20"
            block-color="#FF69B4"
            @change="onIntensityChange"
          />
        </view>
        <view class="intensity-labels">
          <text v-for="(item, idx) in intensityLabels" :key="idx" class="intensity-label">{{ item }}</text>
        </view>
        <text class="intensity-value">{{ form.mood_intensity }} / 5</text>
      </view>

      <!-- Mixed Mood Toggle -->
      <view class="mixed-toggle" @click="showSecondMood = !showSecondMood">
        <text class="toggle-text">混合心情</text>
        <view class="toggle-switch" :class="{ on: showSecondMood }">
          <view class="toggle-dot"></view>
        </view>
      </view>
      <view v-if="showSecondMood" class="mood-grid mood-grid-small">
        <view
          v-for="(cfg, key) in MOOD_CONFIG"
          :key="'s-' + key"
          class="mood-item mood-item-small"
          :class="{ active: form.second_mood === key }"
          :style="form.second_mood === key ? { borderColor: cfg.color, background: cfg.bg } : {}"
          @click="selectSecondMood(key)"
        >
          <text class="mood-emoji-small">{{ cfg.emoji }}</text>
          <text class="mood-name-small">{{ cfg.name }}</text>
        </view>
      </view>
    </view>

    <!-- Section 2: Content -->
    <view class="section-card">
      <text class="section-label">日记内容</text>
      <view class="textarea-wrap">
        <textarea
          class="diary-textarea"
          v-model="form.content"
          placeholder="记录今天的心情..."
          :maxlength="5000"
          auto-height
          :style="{ minHeight: '240rpx' }"
        />
        <text class="char-count">{{ form.content.length }} / 5000</text>
      </view>
    </view>

    <!-- Section 3: Images -->
    <view class="section-card">
      <text class="section-label">配图 ({{ form.images.length }} / 9)</text>
      <view class="image-grid">
        <view v-for="(img, idx) in form.images" :key="idx" class="image-thumb">
          <image :src="resolveImageUrl(img)" mode="aspectFill" class="thumb-img" @click="previewImage(idx)" />
          <view class="img-remove" @click.stop="removeImage(idx)">
            <text class="img-remove-icon">x</text>
          </view>
        </view>
        <view v-if="form.images.length < 9" class="image-add" @click="chooseImage">
          <text class="add-icon">+</text>
        </view>
      </view>
    </view>

    <!-- Section 4: Tags -->
    <view class="section-card">
      <text class="section-label">标签 ({{ form.tags.length }} / 3)</text>
      <view class="tag-input-row">
        <input
          class="tag-input"
          v-model="tagInput"
          placeholder="添加标签..."
          :maxlength="10"
          @confirm="addTag"
        />
        <view class="tag-add-btn" @click="addTag">
          <text class="tag-add-text">添加</text>
        </view>
      </view>
      <view class="tag-list" v-if="form.tags.length > 0">
        <view v-for="(tag, idx) in form.tags" :key="idx" class="tag-chip">
          <text class="tag-text">#{{ tag }}</text>
          <text class="tag-remove" @click="removeTag(idx)">x</text>
        </view>
      </view>
    </view>

    <!-- Section 5: Publish Options -->
    <view class="section-card publish-section">
      <view v-if="showSchedule" class="schedule-row">
        <text class="section-label">定时发布</text>
        <picker mode="date" :value="scheduleDate" @change="onScheduleDateChange">
          <view class="picker-btn">{{ scheduleDate || '选择日期' }}</view>
        </picker>
        <picker mode="time" :value="scheduleTime" @change="onScheduleTimeChange">
          <view class="picker-btn">{{ scheduleTime || '选择时间' }}</view>
        </picker>
      </view>
      <view class="publish-btns">
        <view class="btn-draft" @click="onSaveDraft">
          <text class="btn-text">存为草稿</text>
        </view>
        <view class="btn-schedule" :class="{ active: showSchedule }" @click="toggleSchedule">
          <text class="btn-text">定时发布</text>
        </view>
        <view class="btn-publish" @click="onPublish">
          <text class="btn-text btn-text-white">发布</text>
        </view>
      </view>
    </view>

    <!-- Bottom Spacer -->
    <view class="bottom-spacer"></view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { get, post, put } from '@/utils/request'
import { getToken } from '@/utils/auth'
import { resolveImageUrl, getApiBaseUrl } from '@/utils/common'

// ---- Constants ----
const MOOD_CONFIG = {
  happy:     { emoji: '😊', name: '开心', color: '#FFD700', bg: '#FFF8DC' },
  sweet:     { emoji: '🥰', name: '甜蜜', color: '#FF69B4', bg: '#FFE4EC' },
  calm:      { emoji: '😌', name: '平静', color: '#87CEEB', bg: '#E0F0FF' },
  tired:     { emoji: '😮‍💨', name: '疲惫', color: '#808080', bg: '#F0F0F0' },
  sad:       { emoji: '😢', name: '难过', color: '#4169E1', bg: '#E8EDFF' },
  angry:     { emoji: '😠', name: '生气', color: '#FF4500', bg: '#FFE8E0' },
  wronged:   { emoji: '🥺', name: '委屈', color: '#9370DB', bg: '#F0E8FF' },
  surprised: { emoji: '🤩', name: '惊喜', color: '#FFA500', bg: '#FFF0E0' }
}

const intensityLabels = ['😢', '😐', '🙂', '😄', '🤩']

// ---- State ----
const isEdit = ref(false)
const recordId = ref(null)
const showSecondMood = ref(false)
const showSchedule = ref(false)
const tagInput = ref('')
const scheduleDate = ref('')
const scheduleTime = ref('')
const uploading = ref(false)
let autoSaveTimer = null
let hasChanges = false

const form = reactive({
  mood_type: 'happy',
  mood_intensity: 3,
  second_mood: null,
  content: '',
  images: [],
  tags: [],
  diary_date: new Date().toISOString().split('T')[0],
  publish_status: 'published',
  scheduled_time: ''
})

// 跟踪表单变化
watch(form, () => { hasChanges = true }, { deep: true })

// ---- Lifecycle ----
onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1]
  if (page.options && page.options.id) {
    isEdit.value = true
    recordId.value = page.options.id
    loadDiary()
  } else {
    loadDraft()
    // 仅新日记启用自动保存
    autoSaveTimer = setInterval(() => {
      if (hasChanges) {
        autoSaveDraft()
        hasChanges = false
      }
    }, 30000)
  }
})

onUnmounted(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
    autoSaveTimer = null
  }
})

// ---- Data Loading ----
const loadDiary = async () => {
  try {
    const res = await get(`/life/diary/${recordId.value}`)
    if (res && res.data) {
      const d = res.data
      form.mood_type = d.mood_type || 'happy'
      form.mood_intensity = d.mood_intensity || 3
      form.second_mood = d.second_mood || null
      form.content = d.content || ''
      form.images = d.images || []
      form.tags = d.tags || []
      form.diary_date = d.diary_date || new Date().toISOString().split('T')[0]
      form.publish_status = d.publish_status || 'published'
      form.scheduled_time = d.scheduled_time || ''
      if (form.second_mood) {
        showSecondMood.value = true
      }
      if (form.publish_status === 'scheduled' && form.scheduled_time) {
        showSchedule.value = true
        const dt = new Date(form.scheduled_time)
        scheduleDate.value = dt.toISOString().slice(0, 10)
        scheduleTime.value = dt.toTimeString().slice(0, 5)
      }
    }
  } catch (e) {
    console.error('加载日记失败', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

const loadDraft = async () => {
  try {
    const res = await get('/life/diary/draft')
    if (res && res.data && res.data.content) {
      const draft = JSON.parse(res.data.content)
      uni.showModal({
        title: '恢复草稿',
        content: '发现未发布的草稿，是否恢复？',
        success: (r) => {
          if (r.confirm) {
            Object.assign(form, draft)
            if (form.second_mood) {
              showSecondMood.value = true
            }
            if (form.publish_status === 'scheduled' && form.scheduled_time) {
              showSchedule.value = true
              const dt = new Date(form.scheduled_time)
              scheduleDate.value = dt.toISOString().slice(0, 10)
              scheduleTime.value = dt.toTimeString().slice(0, 5)
            }
          }
        }
      })
    }
  } catch (e) {
    // No draft found, ignore
  }
}

// ---- Date Selection ----
const onDateChange = (e) => {
  form.diary_date = e.detail.value
}

const getDateHint = (dateStr) => {
  if (!dateStr) return ''
  const today = new Date().toISOString().split('T')[0]
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0]
  if (dateStr === today) return '今天'
  if (dateStr === yesterday) return '昨天'
  return ''
}

// ---- Mood Selection ----
const selectMood = (key) => {
  form.mood_type = key
}

const selectSecondMood = (key) => {
  if (form.second_mood === key) {
    form.second_mood = null
  } else {
    form.second_mood = key
  }
}

const onIntensityChange = (e) => {
  form.mood_intensity = e.detail.value
}

// ---- Image Handling ----
const chooseImage = () => {
  const remaining = 9 - form.images.length
  if (remaining <= 0) return
  uni.chooseImage({
    count: remaining,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      for (const tempPath of res.tempFilePaths) {
        await uploadImage(tempPath)
      }
    }
  })
}

const uploadImage = async (filePath) => {
  uploading.value = true
  try {
    const token = getToken()
    const uploadRes = await new Promise((resolve, reject) => {
      uni.uploadFile({
        url: getApiBaseUrl() + '/memory/upload',
        filePath: filePath,
        name: 'file',
        header: {
          'Authorization': token ? `Bearer ${token}` : ''
        },
        success: (res) => {
          if (res.statusCode === 200) {
            const data = JSON.parse(res.data)
            if (data.code === 200) {
              resolve(data)
            } else {
              reject(data)
            }
          } else {
            reject(res)
          }
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
    if (uploadRes && uploadRes.data && uploadRes.data.url) {
      form.images.push(uploadRes.data.url)
    }
  } catch (e) {
    uni.showToast({ title: '图片上传失败', icon: 'none' })
  } finally {
    uploading.value = false
  }
}

const removeImage = (idx) => {
  form.images.splice(idx, 1)
}

const previewImage = (idx) => {
  uni.previewImage({
    current: idx,
    urls: form.images
  })
}

// ---- Tags ----
const addTag = () => {
  const val = tagInput.value.trim()
  if (!val) return
  if (form.tags.length >= 3) {
    uni.showToast({ title: '最多添加3个标签', icon: 'none' })
    return
  }
  if (form.tags.includes(val)) {
    uni.showToast({ title: '标签已存在', icon: 'none' })
    return
  }
  form.tags.push(val)
  tagInput.value = ''
}

const removeTag = (idx) => {
  form.tags.splice(idx, 1)
}

// ---- Schedule ----
const toggleSchedule = () => {
  showSchedule.value = !showSchedule.value
  if (!showSchedule.value) {
    scheduleDate.value = ''
    scheduleTime.value = ''
    form.scheduled_time = ''
  }
}

const onScheduleDateChange = (e) => {
  scheduleDate.value = e.detail.value
}

const onScheduleTimeChange = (e) => {
  scheduleTime.value = e.detail.value
}

// ---- Build payload ----
const buildPayload = (status) => {
  const payload = {
    mood_type: form.mood_type,
    mood_intensity: form.mood_intensity,
    second_mood: form.second_mood,
    content: form.content,
    images: form.images,
    tags: form.tags,
    diary_date: form.diary_date,
    publish_status: status || form.publish_status
  }
  if (payload.publish_status === 'scheduled') {
    if (!scheduleDate.value || !scheduleTime.value) {
      uni.showToast({ title: '请选择定时发布时间', icon: 'none' })
      return null
    }
    payload.scheduled_time = `${scheduleDate.value}T${scheduleTime.value}:00`
  }
  return payload
}

// ---- Actions ----
const onPublish = async () => {
  if (!form.content.trim()) {
    uni.showToast({ title: '请写点什么吧', icon: 'none' })
    return
  }
  if (uploading.value) {
    uni.showToast({ title: '图片正在上传中', icon: 'none' })
    return
  }
  const status = showSchedule.value ? 'scheduled' : 'published'
  const payload = buildPayload(status)
  if (!payload) return
  try {
    if (isEdit.value) {
      await put(`/life/diary/${recordId.value}`, payload)
      uni.showToast({ title: '修改成功' })
    } else {
      await post('/life/diary', payload)
      uni.showToast({ title: '发布成功' })
    }
    // 发布成功后清除草稿
    if (!isEdit.value) {
      try { await put('/life/diary/draft', { content: '' }, { useLoading: false, showError: false }) } catch (_) {}
    }
    setTimeout(() => uni.navigateBack(), 1000)
  } catch (e) {
    console.error('发布失败', e)
    uni.showToast({ title: '发布失败，请重试', icon: 'none' })
  }
}

const onSaveDraft = async () => {
  const payload = buildPayload('draft')
  if (!payload) return
  try {
    if (isEdit.value) {
      await put(`/life/diary/${recordId.value}`, payload)
    } else {
      await post('/life/diary', payload)
    }
    uni.showToast({ title: '已存为草稿' })
    setTimeout(() => uni.navigateBack(), 1000)
  } catch (e) {
    console.error('保存草稿失败', e)
    uni.showToast({ title: '保存失败，请重试', icon: 'none' })
  }
}

const autoSaveDraft = async () => {
  if (!form.content.trim() && !form.mood_type) return
  try {
    const draftData = {
      mood_type: form.mood_type,
      mood_intensity: form.mood_intensity,
      second_mood: form.second_mood,
      content: form.content,
      images: form.images,
      tags: form.tags,
      publish_status: showSchedule.value ? 'scheduled' : 'draft',
      scheduled_time: showSchedule.value && scheduleDate.value && scheduleTime.value
        ? `${scheduleDate.value}T${scheduleTime.value}:00`
        : ''
    }
    await put('/life/diary/draft', { content: JSON.stringify(draftData) }, { useLoading: false, showError: false })
  } catch (e) {
    // Silent fail for auto-save
  }
}

const onBack = () => {
  uni.navigateBack()
}
</script>

<style scoped>
.diary-page {
  min-height: 100vh;
  background: #FFF5F9;
  padding: 0 0 40rpx 0;
}

/* Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 30rpx;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-back {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.back-icon {
  font-size: 36rpx;
  color: #333;
}
.header-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
}
.header-placeholder {
  width: 60rpx;
}

/* Section Card */
.section-card {
  margin: 24rpx 24rpx 0;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 12rpx rgba(255, 105, 180, 0.06);
}
.section-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

/* Date Picker */
.date-picker {
  display: flex;
  align-items: center;
  background: #FFF5F9;
  border: 2rpx solid #FFD6E4;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
}
.date-icon { font-size: 36rpx; margin-right: 16rpx; }
.date-text { font-size: 30rpx; color: #333; font-weight: 500; }
.date-hint { font-size: 24rpx; color: #FF69B4; margin-left: 16rpx; }

/* Mood Grid */
.mood-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.mood-item {
  width: calc(25% - 12rpx);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20rpx 0;
  border-radius: 20rpx;
  border: 3rpx solid #f0f0f0;
  background: #fafafa;
  transition: all 0.2s;
}
.mood-item.active {
  transform: scale(1.05);
}
.mood-emoji {
  font-size: 48rpx;
  margin-bottom: 8rpx;
}
.mood-name {
  font-size: 22rpx;
  color: #666;
}

/* Small mood grid for second mood */
.mood-grid-small {
  margin-top: 20rpx;
  gap: 12rpx;
}
.mood-item-small {
  padding: 14rpx 0;
  border-radius: 16rpx;
}
.mood-emoji-small {
  font-size: 36rpx;
  margin-bottom: 4rpx;
}
.mood-name-small {
  font-size: 20rpx;
  color: #666;
}

/* Intensity */
.intensity-row {
  margin-top: 30rpx;
}
.intensity-bar {
  margin: 10rpx 0;
}
.intensity-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 10rpx;
}
.intensity-label {
  font-size: 28rpx;
}
.intensity-value {
  display: block;
  text-align: center;
  font-size: 26rpx;
  color: #FF69B4;
  font-weight: 600;
  margin-top: 10rpx;
}

/* Mixed Toggle */
.mixed-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f5f5f5;
}
.toggle-text {
  font-size: 26rpx;
  color: #666;
}
.toggle-switch {
  width: 80rpx;
  height: 44rpx;
  border-radius: 22rpx;
  background: #ddd;
  position: relative;
  transition: background 0.2s;
}
.toggle-switch.on {
  background: #FF69B4;
}
.toggle-dot {
  width: 36rpx;
  height: 36rpx;
  border-radius: 18rpx;
  background: #fff;
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  transition: left 0.2s;
  box-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.15);
}
.toggle-switch.on .toggle-dot {
  left: 40rpx;
}

/* Textarea */
.textarea-wrap {
  position: relative;
}
.diary-textarea {
  width: 100%;
  font-size: 30rpx;
  color: #333;
  line-height: 1.8;
  padding: 16rpx;
  box-sizing: border-box;
  background: #FFFAFC;
  border-radius: 16rpx;
  min-height: 240rpx;
}
.char-count {
  display: block;
  text-align: right;
  font-size: 22rpx;
  color: #bbb;
  margin-top: 8rpx;
}

/* Image Grid */
.image-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.image-thumb {
  width: calc(33.33% - 11rpx);
  aspect-ratio: 1;
  border-radius: 16rpx;
  overflow: hidden;
  position: relative;
}
.thumb-img {
  width: 100%;
  height: 100%;
}
.img-remove {
  position: absolute;
  top: 0;
  right: 0;
  width: 44rpx;
  height: 44rpx;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 0 16rpx 0 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.img-remove-icon {
  color: #fff;
  font-size: 24rpx;
  font-weight: bold;
}
.image-add {
  width: calc(33.33% - 11rpx);
  aspect-ratio: 1;
  border-radius: 16rpx;
  border: 3rpx dashed #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
}
.add-icon {
  font-size: 60rpx;
  color: #ccc;
  line-height: 1;
}

/* Tags */
.tag-input-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.tag-input {
  flex: 1;
  height: 64rpx;
  font-size: 28rpx;
  padding: 0 20rpx;
  background: #FFFAFC;
  border-radius: 32rpx;
  border: 2rpx solid #f0e0e8;
}
.tag-add-btn {
  background: #FF69B4;
  border-radius: 32rpx;
  padding: 0 30rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.tag-add-text {
  color: #fff;
  font-size: 26rpx;
  font-weight: 500;
}
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 16rpx;
}
.tag-chip {
  display: flex;
  align-items: center;
  background: #FFE4EC;
  border-radius: 24rpx;
  padding: 8rpx 20rpx;
  gap: 8rpx;
}
.tag-text {
  font-size: 24rpx;
  color: #FF69B4;
}
.tag-remove {
  font-size: 22rpx;
  color: #FF69B4;
  font-weight: bold;
  padding: 0 4rpx;
}

/* Publish Section */
.publish-section {
  padding-bottom: 20rpx;
}
.schedule-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
  flex-wrap: wrap;
}
.schedule-row .section-label {
  margin-bottom: 0;
}
.picker-btn {
  background: #FFFAFC;
  border: 2rpx solid #f0e0e8;
  border-radius: 16rpx;
  padding: 10rpx 24rpx;
  font-size: 26rpx;
  color: #666;
}
.publish-btns {
  display: flex;
  gap: 16rpx;
}
.btn-draft,
.btn-schedule,
.btn-publish {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-draft {
  background: #f5f5f5;
}
.btn-schedule {
  background: #FFE4EC;
}
.btn-schedule.active {
  background: #FF69B4;
}
.btn-schedule.active .btn-text {
  color: #fff;
}
.btn-publish {
  background: linear-gradient(135deg, #FF69B4, #FF8EC7);
}
.btn-text {
  font-size: 28rpx;
  font-weight: 500;
  color: #666;
}
.btn-text-white {
  color: #fff;
}

.bottom-spacer {
  height: 60rpx;
}
</style>
