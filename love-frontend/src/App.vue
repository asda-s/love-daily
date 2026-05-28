<script>
/**
 * 项目根组件
 * 负责全局登录态检查、应用初始化
 */
import { useUserStore } from '@/store/user'

export default {
  onLaunch() {
    console.log('App Launch')
    // 应用启动时检查登录态
    this.checkLoginState()
  },
  onShow() {
    console.log('App Show')
  },
  onHide() {
    console.log('App Hide')
  },
  methods: {
    /**
     * 检查登录态
     * 如果已登录，获取用户信息
     */
    async checkLoginState() {
      const userStore = useUserStore()
      if (userStore.isLoggedIn) {
        try {
          await userStore.getUserInfoFromServer()
          if (userStore.isBindLover) {
            await userStore.getLoverInfo()
          }
        } catch (e) {
          console.error('获取用户信息失败', e)
        }
      }
    }
  }
}
</script>

<style>
/* 全局样式 - Hello Kitty 主题 */
page {
  background-color: #FFF5F9;
  background-image: url('/static/bg.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  background-repeat: no-repeat;
  font-size: 28rpx;
  color: #333333;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 全局变量 */
:root {
  --primary-color: #FF69B4;
  --primary-light: #FFE4EC;
  --accent-color: #FF2D55;
  --bg-color: #FFFFFF;
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-disabled: #999999;
  --border-color: #EEEEEE;
  --border-radius: 16rpx;
  --page-padding: 20rpx;
  --element-spacing: 16rpx;
}

/* 通用按钮样式 */
.btn-primary {
  background-color: var(--primary-color);
  color: #FFFFFF;
  border-radius: var(--border-radius);
  padding: 20rpx 40rpx;
  text-align: center;
  font-size: 32rpx;
}

.btn-primary:active {
  opacity: 0.8;
}

/* 通用卡片样式 */
.card {
  background-color: var(--bg-color);
  border-radius: var(--border-radius);
  padding: 24rpx;
  margin-bottom: var(--element-spacing);
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

/* 安全区域适配 */
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
