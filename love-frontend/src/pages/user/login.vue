<template>
  <view class="login-container">
    <!-- 顶部Logo区域 -->
    <view class="logo-area">
      <image class="logo" src="/static/logo.png" mode="aspectFit"></image>
      <text class="title">心动日常</text>
      <text class="subtitle">记录我们的每一天</text>
    </view>

    <!-- 登录表单 -->
    <view class="form-area">
      <view class="input-group">
        <uni-icons type="person" size="20" color="#999"></uni-icons>
        <input 
          class="input" 
          type="text" 
          v-model="formData.username" 
          placeholder="请输入账号" 
          maxlength="32"
        />
      </view>
      
      <view class="input-group">
        <uni-icons type="locked" size="20" color="#999"></uni-icons>
        <input 
          class="input" 
          type="password" 
          v-model="formData.password" 
          placeholder="请输入密码" 
          maxlength="32"
        />
      </view>

      <button 
        class="btn-login" 
        :loading="loading" 
        @click="handleLogin"
      >
        登录
      </button>

      <view class="register-link" @click="goRegister">
        <text>还没有账号？</text>
        <text class="link">立即注册</text>
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
  password: ''
})

// 加载状态
const loading = ref(false)

/**
 * 处理登录
 */
async function handleLogin() {
  // 表单验证
  if (!formData.username) {
    uni.showToast({ title: '请输入账号', icon: 'none' })
    return
  }
  if (!formData.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  if (formData.username.length < 3) {
    uni.showToast({ title: '账号长度不能少于3位', icon: 'none' })
    return
  }
  if (formData.password.length < 6) {
    uni.showToast({ title: '密码长度不能少于6位', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await userStore.login(formData)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1500)
  } catch (e) {
    console.error('登录失败', e)
  } finally {
    loading.value = false
  }
}

/**
 * 跳转注册页
 */
function goRegister() {
  uni.navigateTo({ url: '/pages/user/register' })
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFE8F0 0%, #FFFFFF 100%);
  padding: 0 40rpx;
  display: flex;
  flex-direction: column;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 120rpx;
  margin-bottom: 80rpx;

  .logo {
    width: 160rpx;
    height: 160rpx;
    margin-bottom: 24rpx;
  }

  .title {
    font-size: 48rpx;
    font-weight: bold;
    color: #FF6B9D;
    margin-bottom: 12rpx;
  }

  .subtitle {
    font-size: 28rpx;
    color: #666666;
  }
}

.form-area {
  flex: 1;
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

.btn-login {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #FF6B9D;
  color: #FFFFFF;
  font-size: 32rpx;
  border-radius: 16rpx;
  margin-top: 40rpx;
  border: none;

  &:active {
    opacity: 0.8;
  }
}

.register-link {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40rpx;
  font-size: 28rpx;
  color: #666666;

  .link {
    color: #FF6B9D;
    margin-left: 8rpx;
  }
}
</style>
