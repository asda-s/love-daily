<template>
  <view class="profile-page">
    <view class="profile-header">
      <view class="header-bg">
        <view class="header-deco-bow"></view>
      </view>
      <view class="user-card">
        <view class="avatar-wrap" @click="changeAvatar">
          <image class="avatar" :src="userInfo.avatar || '/static/default-avatar.png'" mode="aspectFill" />
          <view class="avatar-edit">修改头像</view>
        </view>
        <view class="user-meta">
          <text class="nickname">{{ userInfo.nickname || '未设置昵称' }}</text>
          <text class="username">ID: {{ userInfo.username }}</text>
        </view>
      </view>
      <view v-if="userStore.isBindLover && loverInfo" class="couple-bar">
        <image class="couple-avatar" :src="loverInfo.avatar || '/static/default-avatar.png'" mode="aspectFill" />
        <text class="couple-name">{{ loverInfo.nickname || 'TA' }}</text>
        <text class="couple-label">已绑定</text>
      </view>
    </view>

    <view class="stats-row">
      <view class="stat-item">
        <text class="stat-num">{{ daysTogether }}</text>
        <text class="stat-label">在一起天数</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item" @click="goLove">
        <text class="stat-num">Lv.{{ userInfo.level || 1 }}</text>
        <text class="stat-label">恋爱等级</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item" @click="goLove">
        <text class="stat-num">{{ userInfo.heart_points || 0 }}</text>
        <text class="stat-label">心动分</text>
      </view>
    </view>

    <view class="card invite-card" @click="copyInviteCode">
      <text class="card-title">我的邀请码</text>
      <view class="code-row">
        <text class="code-text">{{ userInfo.invite_code || '--' }}</text>
        <text class="code-copy">复制</text>
      </view>
    </view>

    <view v-if="userStore.isBindLover" class="card love-card">
      <text class="card-title">恋爱养成</text>
      <view class="love-progress">
        <view class="love-level-row">
          <text class="love-level">Lv.{{ userInfo.level || 1 }}</text>
          <text class="love-points">{{ userInfo.heart_points || 0 }} / {{ nextLevelPoints }} 心动分</text>
        </view>
        <view class="love-bar">
          <view class="love-fill" :style="{ width: levelProgress + '%' }"></view>
        </view>
        <text class="love-hint">距下一级还需 {{ Math.max(0, nextLevelPoints - (userInfo.heart_points || 0)) }} 分</text>
      </view>
      <view class="love-actions">
        <view class="love-action-item" @click="goAchievement">
          <text class="action-icon">🏆</text>
          <text class="action-text">成就</text>
        </view>
        <view class="love-action-item" @click="goLevelBenefit">
          <text class="action-icon">🎁</text>
          <text class="action-text">福利</text>
        </view>
        <view class="love-action-item" @click="goLove">
          <text class="action-icon">📊</text>
          <text class="action-text">积分</text>
        </view>
      </view>
      <view class="points-guide">
        <text class="guide-title">积分获取指南</text>
        <view class="guide-item">
          <text class="guide-icon">✅</text>
          <text class="guide-text">每日打卡</text>
          <text class="guide-pts">+5分</text>
        </view>
        <view class="guide-item">
          <text class="guide-icon">📅</text>
          <text class="guide-text">纪念日惊喜</text>
          <text class="guide-pts">+100分</text>
        </view>
        <view class="guide-item">
          <text class="guide-icon">✨</text>
          <text class="guide-text">完成心愿</text>
          <text class="guide-pts">+30分</text>
        </view>
        <view class="guide-item">
          <text class="guide-icon">💌</text>
          <text class="guide-text">发送悄悄话</text>
          <text class="guide-pts">+5分</text>
        </view>
      </view>
    </view>

    <view class="card menu-card">
      <view class="menu-item" @click="showNicknameEdit">
        <text class="menu-icon">📝</text>
        <text class="menu-text">修改昵称</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="showPasswordEdit">
        <text class="menu-icon">🔒</text>
        <text class="menu-text">修改密码</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goAchievement">
        <text class="menu-icon">🏆</text>
        <text class="menu-text">我的成就</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goLevelBenefit">
        <text class="menu-icon">🎁</text>
        <text class="menu-text">等级福利</text>
        <text class="menu-arrow">></text>
      </view>
      <view v-if="userStore.isBindLover" class="menu-item danger" @click="handleUnbind">
        <text class="menu-icon">💔</text>
        <text class="menu-text">解除绑定</text>
        <text class="menu-arrow">></text>
      </view>
    </view>

    <view class="logout-btn" @click="handleLogout">退出登录</view>

    <view v-if="showNickname" class="dialog-mask" @click.self="showNickname = false">
      <view class="dialog-box">
        <text class="dialog-title">修改昵称</text>
        <input class="dialog-input" v-model="newNickname" placeholder="请输入新昵称" maxlength="32" />
        <view class="dialog-btns">
          <view class="dialog-btn cancel" @click="showNickname = false">取消</view>
          <view class="dialog-btn confirm" @click="saveNickname">保存</view>
        </view>
      </view>
    </view>

    <view v-if="showPassword" class="dialog-mask" @click.self="showPassword = false">
      <view class="dialog-box">
        <text class="dialog-title">修改密码</text>
        <input class="dialog-input" v-model="oldPassword" type="password" placeholder="请输入原密码" />
        <input class="dialog-input" v-model="newPassword" type="password" placeholder="请输入新密码（至少6位）" />
        <input class="dialog-input" v-model="confirmPassword" type="password" placeholder="请再次输入新密码" />
        <view class="dialog-btns">
          <view class="dialog-btn cancel" @click="showPassword = false">取消</view>
          <view class="dialog-btn confirm" @click="savePassword">保存</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user.js'
import { put, post } from '@/utils/request'
import { getToken } from '@/utils/auth'
import { LEVEL_CONFIG } from '@/utils/constants'

const userStore = useUserStore()
const userInfo = ref({})
const loverInfo = ref({})
const showNickname = ref(false)
const showPassword = ref(false)
const newNickname = ref('')
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const nextLevelPoints = computed(() => {
  const next = LEVEL_CONFIG.find(l => l.level === (userInfo.value.level || 1) + 1)
  return next ? next.min : LEVEL_CONFIG[LEVEL_CONFIG.length - 1].max
})

const levelProgress = computed(() => {
  const pts = userInfo.value.heart_points || 0
  const current = LEVEL_CONFIG.find(l => l.level === (userInfo.value.level || 1)) || LEVEL_CONFIG[0]
  const range = current.max === Infinity ? current.min + 1 : current.max - current.min
  return Math.min(100, Math.round(((pts - current.min) / range) * 100))
})

const daysTogether = computed(() => {
  const since = userInfo.value.bind_time || userInfo.value.created_at
  if (!since) return 0
  const d = new Date(since)
  return Math.max(0, Math.floor((Date.now() - d.getTime()) / 86400000))
})

onShow(async () => {
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/user/login' })
    return
  }
  const info = await userStore.getUserInfoFromServer()
  if (info) {
    userInfo.value = info
    if (info.lover_id) {
      const lover = await userStore.getLoverInfo()
      if (lover) loverInfo.value = lover
    }
  }
})

function copyInviteCode() {
  uni.setClipboardData({
    data: userInfo.value.invite_code || '',
    success: () => uni.showToast({ title: '已复制', icon: 'success' })
  })
}

function showNicknameEdit() {
  newNickname.value = userInfo.value.nickname || ''
  showNickname.value = true
}

async function saveNickname() {
  if (!newNickname.value || newNickname.value.length < 2) {
    uni.showToast({ title: '昵称至少2个字', icon: 'none' })
    return
  }
  try {
    const res = await put('/user/info', { nickname: newNickname.value })
    if (res) {
      userInfo.value.nickname = newNickname.value
      uni.showToast({ title: '修改成功' })
      showNickname.value = false
    }
  } catch (e) {
    uni.showToast({ title: '保存失败，请重试', icon: 'none' })
  }
}

function showPasswordEdit() {
  oldPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  showPassword.value = true
}

async function savePassword() {
  if (!oldPassword.value) { uni.showToast({ title: '请输入原密码', icon: 'none' }); return }
  if (!newPassword.value || newPassword.value.length < 6) { uni.showToast({ title: '新密码至少6位', icon: 'none' }); return }
  if (newPassword.value !== confirmPassword.value) { uni.showToast({ title: '两次输入的密码不一致', icon: 'none' }); return }
  try {
    const res = await put('/user/info', { old_password: oldPassword.value, new_password: newPassword.value })
    if (res) {
      uni.showToast({ title: '修改成功' })
      showPassword.value = false
    }
  } catch (e) {
    uni.showToast({ title: '保存失败，请重试', icon: 'none' })
  }
}

function goAchievement() { uni.navigateTo({ url: '/pages/love/achievement' }) }
function goLevelBenefit() { uni.navigateTo({ url: '/pages/love/level-benefit' }) }
function goLove() { uni.switchTab({ url: '/pages/love/index' }) }

function handleUnbind() {
  uni.showModal({
    title: '解除绑定',
    content: '解除后将无法查看对方数据，确定解除情侣绑定？',
    confirmColor: '#e43d33',
    success: async (res) => {
      if (res.confirm) {
        try {
          await post('/user/unbind')
          userStore.loverInfo = null
          userInfo.value.lover_id = null
          loverInfo.value = {}
          uni.showToast({ title: '已解除绑定' })
        } catch (e) {
          uni.showToast({ title: '操作失败，请重试', icon: 'none' })
        }
      }
    }
  })
}

function changeAvatar() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (chooseRes) => {
      const filePath = chooseRes.tempFilePaths[0]
      const token = getToken()
      if (!token) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        return
      }
      uni.showLoading({ title: '上传中...', mask: true })
      try {
        const uploadRes = await new Promise((resolve, reject) => {
          uni.uploadFile({
            url: `${import.meta.env.VITE_API_BASE_URL || ''}/memory/upload`,
            filePath: filePath,
            name: 'file',
            header: { Authorization: `Bearer ${token}` },
            success: (res) => {
              if (res.statusCode === 200) {
                try {
                  const data = JSON.parse(res.data)
                  if (data.code === 200) resolve(data)
                  else reject(new Error(data.message || '上传失败'))
                } catch (e) {
                  reject(new Error('响应解析失败'))
                }
              } else if (res.statusCode === 401) {
                reject(new Error('登录已过期，请重新登录'))
              } else {
                try {
                  const data = JSON.parse(res.data)
                  reject(new Error(data.message || `上传失败(${res.statusCode})`))
                } catch (e) {
                  reject(new Error(`上传失败(${res.statusCode})`))
                }
              }
            },
            fail: (err) => {
              reject(new Error(err.errMsg || '网络连接失败'))
            }
          })
        })
        const avatarUrl = uploadRes.data.url
        await put('/user/info', { avatar: avatarUrl })
        userInfo.value.avatar = avatarUrl
        await userStore.getUserInfoFromServer()
        uni.hideLoading()
        uni.showToast({ title: '头像已更新' })
      } catch (e) {
        uni.hideLoading()
        uni.showToast({ title: e.message || '上传失败，请重试', icon: 'none' })
      }
    }
  })
}

function handleLogout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
        uni.reLaunch({ url: '/pages/user/login' })
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.profile-page {
  min-height: 100vh;
  background: #FFF5F9;
  padding-bottom: 120rpx;
}
.profile-header {
  position: relative;
  padding-bottom: 20rpx;
}
.header-bg {
  height: 280rpx;
  background: linear-gradient(135deg, #FF69B4, #FF8FB1);
  position: relative;
  overflow: hidden;
}
.header-deco-bow {
  position: absolute;
  top: 30rpx;
  right: 40rpx;
  width: 60rpx;
  height: 30rpx;
  &::before, &::after {
    content: '';
    position: absolute;
    width: 28rpx;
    height: 28rpx;
    background: rgba(255,255,255,0.2);
    border-radius: 50% 50% 50% 0;
  }
  &::before { left: 0; transform: rotate(-45deg); }
  &::after { right: 0; transform: rotate(45deg); }
}
.user-card {
  display: flex;
  align-items: center;
  padding: 0 40rpx;
  margin-top: -100rpx;
}
.avatar {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  border: 6rpx solid #fff;
  background: #eee;
}
.avatar-wrap {
  position: relative;
}
.avatar-edit {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.5);
  color: #fff;
  font-size: 18rpx;
  text-align: center;
  padding: 4rpx 0;
  border-radius: 0 0 70rpx 70rpx;
}
.user-meta {
  margin-left: 28rpx;
  flex: 1;
  min-width: 0;
}
.nickname {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 8rpx;
  text-shadow: 0 2rpx 4rpx rgba(0,0,0,0.15);
}
.username {
  display: block;
  font-size: 24rpx;
  color: #fff;
  opacity: 0.9;
  text-shadow: 0 1rpx 2rpx rgba(0,0,0,0.1);
}
.couple-bar {
  display: flex;
  align-items: center;
  margin: 20rpx 40rpx 0;
  padding: 16rpx 24rpx;
  background: rgba(255,255,255,0.85);
  border-radius: 40rpx;
}
.couple-avatar {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  margin-right: 12rpx;
}
.couple-name {
  flex: 1;
  font-size: 26rpx;
  color: #333;
}
.couple-label {
  font-size: 22rpx;
  color: #666;
}
.stats-row {
  display: flex;
  align-items: center;
  background: #fff;
  margin: 20rpx;
  border-radius: 20rpx;
  padding: 30rpx 0;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}
.stat-item {
  flex: 1;
  text-align: center;
}
.stat-num {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #FF69B4;
}
.stat-label {
  display: block;
  font-size: 22rpx;
  color: #999;
  margin-top: 8rpx;
}
.stat-divider {
  width: 1rpx;
  height: 60rpx;
  background: #eee;
}
.card {
  background: #fff;
  margin: 20rpx;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}
.card-title {
  display: block;
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}
.invite-card {}
.code-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff5f7;
  border: 2rpx dashed #FF69B4;
  border-radius: 16rpx;
  padding: 24rpx;
}
.code-text {
  font-size: 44rpx;
  font-weight: bold;
  color: #FF69B4;
  letter-spacing: 10rpx;
}
.code-copy {
  font-size: 24rpx;
  color: #FF69B4;
  background: rgba(255,107,157,0.15);
  padding: 8rpx 24rpx;
  border-radius: 30rpx;
}
.love-card {}
.love-progress { margin-bottom: 24rpx; }
.love-level-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}
.love-level {
  font-size: 36rpx;
  font-weight: bold;
  color: #FF69B4;
}
.love-points {
  font-size: 24rpx;
  color: #999;
}
.love-bar {
  height: 16rpx;
  background: #f0f0f0;
  border-radius: 8rpx;
  overflow: hidden;
}
.love-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF69B4, #FF8FB1);
  border-radius: 8rpx;
  transition: width 0.3s;
}
.love-hint {
  display: block;
  font-size: 22rpx;
  color: #bbb;
  margin-top: 8rpx;
}
.love-actions {
  display: flex;
  justify-content: space-around;
  padding: 20rpx 0;
  border-top: 1rpx solid #FFF5F9;
  border-bottom: 1rpx solid #FFF5F9;
}
.love-action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}
.action-icon { font-size: 44rpx; }
.action-text { font-size: 22rpx; color: #666; }
.points-guide { margin-top: 24rpx; }
.guide-title {
  display: block;
  font-size: 26rpx;
  color: #666;
  margin-bottom: 16rpx;
}
.guide-item {
  display: flex;
  align-items: center;
  padding: 12rpx 0;
}
.guide-icon { font-size: 32rpx; margin-right: 16rpx; }
.guide-text { flex: 1; font-size: 26rpx; color: #666; }
.guide-pts { font-size: 26rpx; color: #FF69B4; font-weight: bold; }
.menu-card {}
.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 0;
  border-bottom: 1rpx solid #FFF5F9;
}
.menu-item:last-child { border-bottom: none; }
.menu-item.danger .menu-text { color: #e43d33; }
.menu-icon { font-size: 36rpx; margin-right: 20rpx; }
.menu-text { flex: 1; font-size: 28rpx; color: #333; }
.menu-arrow { font-size: 28rpx; color: #ccc; }
.logout-btn {
  margin: 40rpx 20rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  text-align: center;
  font-size: 30rpx;
  color: #FF4757;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}
.dialog-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.dialog-box {
  width: 600rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
}
.dialog-title {
  display: block;
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
  text-align: center;
}
.dialog-input {
  border: 2rpx solid #eee;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  margin-bottom: 20rpx;
}
.dialog-btns {
  display: flex;
  gap: 20rpx;
  margin-top: 10rpx;
}
.dialog-btn {
  flex: 1;
  padding: 20rpx;
  border-radius: 40rpx;
  text-align: center;
  font-size: 28rpx;
}
.dialog-btn.cancel {
  background: #FFF5F9;
  color: #666;
}
.dialog-btn.confirm {
  background: #FF69B4;
  color: #fff;
}
</style>
