<template>
  <view class="register-container">
    <!-- Hello Kitty 装饰 -->
    <view class="deco-bow deco-bow-1"></view>
    <view class="deco-bow deco-bow-2"></view>
    <view class="deco-heart">♡</view>

    <!-- 注册表单 -->
    <view class="form-area">
      <view class="header">
        <text class="title">🎀 创建账号</text>
        <text class="subtitle">开启你们的心动日常</text>
      </view>

      <view class="input-group">
        <uni-icons type="person" size="20" color="#999"></uni-icons>
        <input 
          class="input" 
          type="text" 
          v-model="formData.username" 
          placeholder="请输入账号（3-32位）" 
          maxlength="32"
        />
      </view>
      
      <view class="input-group">
        <uni-icons type="locked" size="20" color="#999"></uni-icons>
        <input 
          class="input" 
          type="password" 
          v-model="formData.password" 
          placeholder="请输入密码（6-32位）" 
          maxlength="32"
        />
      </view>

      <view class="input-group">
        <uni-icons type="chat" size="20" color="#999"></uni-icons>
        <input 
          class="input" 
          type="text" 
          v-model="formData.nickname" 
          placeholder="请输入昵称（2-32位）" 
          maxlength="32"
        />
      </view>

      <button 
        class="btn-register" 
        :loading="loading" 
        @click="handleRegister"
      >
        注册
      </button>

      <view class="login-link" @click="goLogin">
        <text>已有账号？</text>
        <text class="link">立即登录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// 表单数据
const formData = reactive({
  username: '',
  password: '',
  nickname: ''
})

// 加载状态
const loading = ref(false)

/**
 * 处理注册
 */
async function handleRegister() {
  // 表单验证
  if (!formData.username) {
    uni.showToast({ title: '请输入账号', icon: 'none' })
    return
  }
  if (formData.username.length < 3) {
    uni.showToast({ title: '账号长度不能少于3位', icon: 'none' })
    return
  }
  if (!formData.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  if (formData.password.length < 6) {
    uni.showToast({ title: '密码长度不能少于6位', icon: 'none' })
    return
  }
  if (!formData.nickname) {
    uni.showToast({ title: '请输入昵称', icon: 'none' })
    return
  }
  if (formData.nickname.length < 2) {
    uni.showToast({ title: '昵称长度不能少于2位', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await userStore.register(formData)
    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (e) {
    console.error('注册失败', e)
    uni.showToast({ title: '注册失败，请重试', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/**
 * 跳转登录页
 */
function goLogin() {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFE4EC 0%, #FFFFFF 100%);
  padding: 0 40rpx;
  position: relative;
  overflow: hidden;
}
.deco-bow {
  position: absolute;
  width: 40rpx;
  height: 20rpx;
  opacity: 0.15;
  &::before, &::after {
    content: '';
    position: absolute;
    width: 18rpx;
    height: 18rpx;
    background: #FF69B4;
    border-radius: 50% 50% 50% 0;
  }
  &::before { left: 0; transform: rotate(-45deg); }
  &::after { right: 0; transform: rotate(45deg); }
}
.deco-bow-1 { top: 40rpx; right: 100rpx; transform: rotate(15deg); }
.deco-bow-2 { bottom: 200rpx; left: 60rpx; transform: rotate(-20deg); }
.deco-heart {
  position: absolute;
  top: 120rpx;
  left: 80rpx;
  font-size: 28rpx;
  color: #FF69B4;
  opacity: 0.12;
}

.form-area {
  padding-top: 80rpx;
}

.header {
  display: flex;
  flex-direction: column;
  margin-bottom: 60rpx;

  .title {
    font-size: 48rpx;
    font-weight: bold;
    color: #333333;
    margin-bottom: 12rpx;
  }

  .subtitle {
    font-size: 28rpx;
    color: #666666;
  }
}

.input-group {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);

  .input {
    flex: 1;
    margin-left: 16rpx;
    font-size: 30rpx;
  }
}

.btn-register {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #FF69B4;
  color: #FFFFFF;
  font-size: 32rpx;
  border-radius: 16rpx;
  margin-top: 40rpx;
  border: none;

  &:active {
    opacity: 0.8;
  }
}

.login-link {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40rpx;
  font-size: 28rpx;
  color: #666666;

  .link {
    color: #FF69B4;
    margin-left: 8rpx;
  }
}
</style>
