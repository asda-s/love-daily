<template>
  <view class="index-container">
    <view v-if="showInviteDialog" class="dialog-mask">
      <view class="invite-dialog">
        <view class="dialog-title">绑定伴侣</view>
        <view class="my-code-section">
          <text class="my-code-label">我的邀请码</text>
          <view class="my-code-row">
            <text class="my-code-text">{{ myInviteCode }}</text>
            <view class="copy-btn" @click="copyCode">复制</view>
          </view>
          <text class="my-code-hint">发送给对方，让TA在注册时填写</text>
        </view>
        <view class="divider"><text class="divider-text">或</text></view>
        <view class="input-section">
          <input class="invite-input" v-model="inviteCode" placeholder="输入对方的邀请码" />
        </view>
        <view class="dialog-buttons">
          <view class="btn-skip" @click="skipInvite">先逛逛</view>
          <view class="btn-bind" @click="bindLover">绑定</view>
        </view>
      </view>
    </view>

    <view class="header">
      <view class="header-left">
        <text class="app-title">💕 心动日常</text>
      </view>
      <view class="header-right" @click="goProfile">
        <image class="header-avatar" :src="userStore.userInfo?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
      </view>
    </view>

    <view class="couple-card" v-if="userStore.isBindLover" @click="goProfile">
      <view class="couple-avatars">
        <image class="avatar" :src="userStore.userInfo?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
        <text class="heart-icon">💕</text>
        <image class="avatar" :src="userStore.loverInfo?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
      </view>
      <view class="couple-names">
        <text>{{ userStore.userInfo?.nickname || '我' }}</text>
        <text class="amp">&</text>
        <text>{{ userStore.loverInfo?.nickname || 'TA' }}</text>
      </view>
      <view class="together-days" v-if="togetherDays > 0">
        <text class="days-number">{{ togetherDays }}</text>
        <text class="days-label">天</text>
      </view>
    </view>

    <view class="couple-card single" v-else @click="showInviteDialog = true">
      <text class="single-emoji">💌</text>
      <text class="single-text">邀请你的另一半，开启心动旅程</text>
      <view class="bind-btn">立即绑定</view>
    </view>

    <view class="stats-card" v-if="userStore.isBindLover">
      <view class="stats-grid">
        <view class="stats-item">
          <text class="stats-value">{{ stats.memory_count || 0 }}</text>
          <text class="stats-label">时光线</text>
        </view>
        <view class="stats-item">
          <text class="stats-value">{{ stats.wish_completed || 0 }}</text>
          <text class="stats-label">心愿达成</text>
        </view>
        <view class="stats-item">
          <text class="stats-value">{{ stats.month_checkins || 0 }}</text>
          <text class="stats-label">本月打卡</text>
        </view>
        <view class="stats-item">
          <text class="stats-value">{{ stats.emotion_count || 0 }}</text>
          <text class="stats-label">情绪记录</text>
        </view>
      </view>
      <view class="stats-bottom">
        <text class="stats-expense">本月共同支出 ¥{{ stats.month_expense || 0 }}</text>
        <text class="stats-anniversary">{{ stats.anniversary_count || 0 }} 个纪念日</text>
      </view>
    </view>

    <view class="module-section">
      <view class="section-header">
        <text class="section-icon">📖</text>
        <text class="section-title">时光档案馆</text>
      </view>
      <view class="module-grid">
        <view class="module-item" @click="go('/pages/memory/timeline')">
          <text class="module-emoji">📷</text>
          <text class="module-name">时光线</text>
          <text class="module-desc">记录爱的点滴</text>
        </view>
        <view class="module-item" @click="go('/pages/memory/anniversary')">
          <text class="module-emoji">📅</text>
          <text class="module-name">纪念日</text>
          <text class="module-desc">重要日子不忘</text>
        </view>
        <view class="module-item" @click="go('/pages/memory/wish')">
          <text class="module-emoji">⭐</text>
          <text class="module-name">心愿清单</text>
          <text class="module-desc">共同的愿望</text>
        </view>
        <view class="module-item" @click="go('/pages/memory/whisper')">
          <text class="module-emoji">💌</text>
          <text class="module-name">悄悄话</text>
          <text class="module-desc">说给TA的心里话</text>
        </view>
      </view>
    </view>

    <view class="module-section">
      <view class="section-header">
        <text class="section-icon">🏠</text>
        <text class="section-title">生活管家</text>
      </view>
      <view class="module-grid">
        <view class="module-item" @click="go('/pages/life/period')">
          <text class="module-emoji">🩸</text>
          <text class="module-name">生理期</text>
          <text class="module-desc">贴心记录</text>
        </view>
        <view class="module-item" @click="go('/pages/life/diet')">
          <text class="module-emoji">🍽️</text>
          <text class="module-name">饮食偏好</text>
          <text class="module-desc">口味记忆</text>
        </view>
        <view class="module-item" @click="go('/pages/life/todo')">
          <text class="module-emoji">⏰</text>
          <text class="module-name">全能提醒</text>
          <text class="module-desc">待办不遗漏</text>
        </view>
        <view class="module-item" @click="go('/pages/life/item')">
          <text class="module-emoji">📦</text>
          <text class="module-name">好物收纳</text>
          <text class="module-desc">共享物品</text>
        </view>
      </view>
    </view>

    <view class="module-section">
      <view class="section-header">
        <text class="section-icon">🎮</text>
        <text class="section-title">互动与陪伴</text>
      </view>
      <view class="module-grid">
        <view class="module-item" @click="go('/pages/interact/checkin')">
          <text class="module-emoji">✅</text>
          <text class="module-name">情侣打卡</text>
          <text class="module-desc">一起坚持</text>
        </view>
        <view class="module-item" @click="go('/pages/interact/benefit')">
          <text class="module-emoji">🎁</text>
          <text class="module-name">积分福利</text>
          <text class="module-desc">心动分兑换</text>
        </view>
        <view class="module-item" @click="go('/pages/interact/emotion')">
          <text class="module-emoji">🫧</text>
          <text class="module-name">情绪树洞</text>
          <text class="module-desc">匿名心事</text>
        </view>
        <view class="module-item" @click="go('/pages/interact/bill')">
          <text class="module-emoji">🧾</text>
          <text class="module-name">情侣账本</text>
          <text class="module-desc">AA或轮流请</text>
        </view>
      </view>
    </view>

    <view class="module-section">
      <view class="section-header">
        <text class="section-icon">🌱</text>
        <text class="section-title">恋爱养成</text>
      </view>
      <view class="love-card" @click="go('/pages/love/index')">
        <view class="love-left">
          <text class="love-level">Lv.{{ loveLevel }}</text>
          <text class="love-name">{{ levelName }}</text>
          <view class="love-progress-bar">
            <view class="love-progress-fill" :style="{ width: levelProgress + '%' }"></view>
          </view>
          <text class="love-points">{{ heartPoints }} 心动分</text>
        </view>
        <view class="love-right">
          <text class="love-emoji">🌱</text>
        </view>
      </view>
      <view class="love-actions">
        <view class="love-action-item" @click="go('/pages/interact/checkin')">
          <text class="action-emoji">✅</text>
          <text class="action-name">打卡得分</text>
        </view>
        <view class="love-action-item" @click="go('/pages/love/achievement')">
          <text class="action-emoji">🏅</text>
          <text class="action-name">成就</text>
        </view>
        <view class="love-action-item" @click="go('/pages/interact/benefit')">
          <text class="action-emoji">🎁</text>
          <text class="action-name">福利</text>
        </view>
        <view class="love-action-item" @click="go('/pages/love/index')">
          <text class="action-emoji">📊</text>
          <text class="action-name">详情</text>
        </view>
      </view>
    </view>

    <view class="footer-space"></view>
    <custom-tabbar :current="0" />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { get } from '@/utils/request'
import { getLevelInfo } from '@/utils/common'
import CustomTabbar from '@/components/custom-tabbar.vue'

const userStore = useUserStore()

const inviteCode = ref('')
const showInviteDialog = ref(false)
const myInviteCode = ref('')
const heartPoints = ref(0)
const loveLevel = ref(1)
const stats = ref({})

onShow(async () => {
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/user/login' })
    return
  }
  try {
    await userStore.getUserInfoFromServer()
    if (userStore.isBindLover && !userStore.loverInfo) {
      await userStore.getLoverInfo()
    }
  } catch (e) {}
  if (!userStore.isBindLover) {
    const code = userStore.userInfo?.invite_code || uni.getStorageSync('invite_code')
    if (code) myInviteCode.value = code
    showInviteDialog.value = true
  } else {
    showInviteDialog.value = false
  }
  loadLoveData()
})

const togetherDays = computed(() => {
  const bindDate = userStore.userInfo?.bind_time
  if (!bindDate) return 0
  return Math.floor((Date.now() - new Date(bindDate).getTime()) / 86400000)
})

const levelName = computed(() => getLevelInfo(heartPoints.value).name)
const levelProgress = computed(() => {
  const info = getLevelInfo(heartPoints.value)
  return Math.min(100, Math.floor(info.progress || 0))
})

async function loadLoveData() {
  try {
    const [overviewRes, statsRes] = await Promise.all([
      get('/love/overview'),
      get('/love/stats')
    ])
    if (overviewRes && overviewRes.data) {
      loveLevel.value = overviewRes.data.level || 1
      heartPoints.value = overviewRes.data.heart_points || 0
    }
    if (statsRes && statsRes.data) {
      stats.value = statsRes.data
    }
  } catch (e) {}
}

function copyCode() {
  uni.setClipboardData({
    data: myInviteCode.value,
    success: () => uni.showToast({ title: '已复制' })
  })
}

async function bindLover() {
  if (!inviteCode.value.trim()) {
    uni.showToast({ title: '请输入邀请码', icon: 'none' })
    return
  }
  try {
    await userStore.bindLover(inviteCode.value.trim())
    showInviteDialog.value = false
    uni.showToast({ title: '绑定成功' })
  } catch (e) {
    uni.showToast({ title: e.message || '绑定失败', icon: 'none' })
  }
}

function skipInvite() {
  showInviteDialog.value = false
}

const tabPages = ['/pages/index/index', '/pages/memory/timeline', '/pages/life/todo', '/pages/interact/checkin', '/pages/love/index']

function go(url) {
  if (tabPages.includes(url)) {
    uni.switchTab({ url })
  } else {
    uni.navigateTo({ url })
  }
}

function goProfile() {
  uni.navigateTo({ url: '/pages/user/profile' })
}
</script>

<style lang="scss" scoped>
.index-container {
  min-height: 100vh;
  background: #FFF5F8;
  padding-bottom: 140rpx;
}

.header {
  background: linear-gradient(135deg, #FF6B9D, #FF8E8E);
  padding: 60rpx 30rpx 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  .app-title { font-size: 38rpx; font-weight: bold; color: #fff; }
  .header-avatar { width: 68rpx; height: 68rpx; border-radius: 50%; border: 3rpx solid #fff; }
}

.couple-card {
  margin: -20rpx 30rpx 24rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 36rpx;
  box-shadow: 0 4rpx 20rpx rgba(255, 107, 157, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  &.single { padding: 48rpx 36rpx; }
  .couple-avatars {
    display: flex;
    align-items: center;
    gap: 20rpx;
    .avatar { width: 96rpx; height: 96rpx; border-radius: 50%; border: 4rpx solid #FFD6E4; }
    .heart-icon { font-size: 40rpx; }
  }
  .couple-names {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-top: 16rpx;
    font-size: 30rpx; color: #333; font-weight: 600;
    .amp { color: #FF6B9D; font-size: 36rpx; }
  }
  .together-days {
    margin-top: 16rpx;
    display: flex; align-items: baseline; gap: 6rpx;
    .days-number { font-size: 56rpx; font-weight: bold; color: #FF6B9D; }
    .days-label { font-size: 24rpx; color: #999; }
  }
  .single-emoji { font-size: 64rpx; }
  .single-text { font-size: 28rpx; color: #666; margin: 16rpx 0; }
  .bind-btn {
    background: linear-gradient(135deg, #FF6B9D, #FF8E8E);
    color: #fff; font-size: 28rpx; padding: 16rpx 48rpx;
    border-radius: 36rpx; margin-top: 8rpx;
  }
}

.stats-card {
  margin: 0 30rpx 24rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx 30rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  .stats-grid {
    display: flex;
    justify-content: space-around;
    .stats-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      .stats-value { font-size: 36rpx; font-weight: bold; color: #FF6B9D; }
      .stats-label { font-size: 22rpx; color: #999; margin-top: 6rpx; }
    }
  }
  .stats-bottom {
    display: flex;
    justify-content: space-between;
    margin-top: 20rpx;
    padding-top: 20rpx;
    border-top: 1rpx solid #f5f5f5;
    .stats-expense { font-size: 24rpx; color: #666; }
    .stats-anniversary { font-size: 24rpx; color: #999; }
  }
}

.module-section {
  margin: 0 30rpx 28rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  .section-header {
    display: flex;
    align-items: center;
    gap: 10rpx;
    margin-bottom: 24rpx;
    .section-icon { font-size: 36rpx; }
    .section-title { font-size: 32rpx; font-weight: bold; color: #333; }
  }
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx;
  .module-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20rpx 0;
    border-radius: 16rpx;
    background: #FFF9FB;
    transition: all 0.2s;
    &:active { background: #FFE8F0; transform: scale(0.95); }
    .module-emoji { font-size: 48rpx; margin-bottom: 8rpx; }
    .module-name { font-size: 24rpx; color: #333; font-weight: 600; }
    .module-desc { font-size: 20rpx; color: #999; margin-top: 4rpx; }
  }
}

.love-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #FF6B9D, #FF8E8E);
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  .love-left {
    flex: 1;
    .love-level {
      font-size: 32rpx; font-weight: bold; color: #fff;
      background: rgba(255,255,255,0.25); padding: 4rpx 16rpx;
      border-radius: 8rpx; display: inline-block;
    }
    .love-name { display: block; font-size: 26rpx; color: rgba(255,255,255,0.85); margin-top: 12rpx; }
    .love-progress-bar {
      width: 100%; height: 12rpx; background: rgba(255,255,255,0.3);
      border-radius: 6rpx; margin-top: 16rpx; overflow: hidden;
      .love-progress-fill { height: 100%; background: #fff; border-radius: 6rpx; transition: width 0.3s; }
    }
    .love-points { display: block; font-size: 22rpx; color: rgba(255,255,255,0.75); margin-top: 8rpx; }
  }
  .love-right .love-emoji { font-size: 72rpx; opacity: 0.6; }
}

.love-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  .love-action-item {
    display: flex; flex-direction: column; align-items: center;
    padding: 16rpx 0;
    .action-emoji { font-size: 40rpx; margin-bottom: 6rpx; }
    .action-name { font-size: 22rpx; color: #666; }
  }
}

.footer-space { height: 30rpx; }

.dialog-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.invite-dialog {
  width: 600rpx;
  background: #fff;
  border-radius: 32rpx;
  padding: 48rpx 40rpx;
  .dialog-title { font-size: 36rpx; font-weight: bold; color: #333; text-align: center; margin-bottom: 36rpx; }
  .my-code-section {
    background: #FFF5F8; border-radius: 16rpx; padding: 24rpx; margin-bottom: 24rpx;
    .my-code-label { font-size: 24rpx; color: #999; display: block; margin-bottom: 12rpx; }
    .my-code-row {
      display: flex; align-items: center; justify-content: space-between;
      .my-code-text { font-size: 40rpx; font-weight: bold; color: #FF6B9D; letter-spacing: 8rpx; }
      .copy-btn {
        font-size: 24rpx; color: #FF6B9D; border: 2rpx solid #FF6B9D;
        padding: 6rpx 20rpx; border-radius: 24rpx;
      }
    }
    .my-code-hint { font-size: 22rpx; color: #bbb; display: block; margin-top: 8rpx; }
  }
  .divider {
    text-align: center; margin-bottom: 24rpx;
    border-bottom: 2rpx solid #eee; position: relative; height: 20rpx;
    .divider-text {
      position: absolute; top: -10rpx; left: 50%; transform: translateX(-50%);
      background: #fff; padding: 0 16rpx; font-size: 24rpx; color: #ccc;
    }
  }
  .input-section {
    margin-bottom: 32rpx;
    .invite-input {
      border: 2rpx solid #eee; border-radius: 16rpx;
      padding: 20rpx 24rpx; font-size: 30rpx; text-align: center;
    }
  }
  .dialog-buttons {
    display: flex; gap: 24rpx;
    .btn-skip {
      flex: 1; text-align: center; padding: 20rpx; border-radius: 36rpx;
      font-size: 28rpx; color: #999; background: #f5f5f5;
    }
    .btn-bind {
      flex: 1; text-align: center; padding: 20rpx; border-radius: 36rpx;
      font-size: 28rpx; color: #fff;
      background: linear-gradient(135deg, #FF6B9D, #FF8E8E);
    }
  }
}
</style>
