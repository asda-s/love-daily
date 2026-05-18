<template>
  <view class="custom-tabbar">
    <view
      v-for="(item, index) in tabs"
      :key="index"
      class="tab-item"
      :class="{ active: current === index }"
      @click="switchTab(index)"
    >
      <image class="tab-icon" :src="current === index ? item.activeIcon : item.icon" mode="aspectFit" />
      <text class="tab-text">{{ item.text }}</text>
    </view>
  </view>
</template>

<script setup>
const props = defineProps({
  current: { type: Number, default: 0 }
})

const tabs = [
  { text: '首页', icon: '/static/tab/home.png', activeIcon: '/static/tab/home-active.png', path: '/pages/index/index' },
  { text: '时光', icon: '/static/tab/time.png', activeIcon: '/static/tab/time-active.png', path: '/pages/memory/timeline' },
  { text: '管家', icon: '/static/tab/life.png', activeIcon: '/static/tab/life-active.png', path: '/pages/life/todo' },
  { text: '打卡', icon: '/static/tab/interact.png', activeIcon: '/static/tab/interact-active.png', path: '/pages/interact/checkin' },
  { text: '养成', icon: '/static/tab/love.png', activeIcon: '/static/tab/love-active.png', path: '/pages/love/index' }
]

function switchTab(index) {
  if (props.current === index) return
  uni.switchTab({ url: tabs[index].path })
}
</script>

<style lang="scss" scoped>
.custom-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 110rpx;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-around;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.06);
  z-index: 999;
  padding-bottom: env(safe-area-inset-bottom);
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8rpx 0;
  transition: all 0.2s;

  .tab-icon {
    width: 48rpx;
    height: 48rpx;
    margin-bottom: 4rpx;
  }

  .tab-text {
    font-size: 22rpx;
    color: #999999;
  }

  &.active .tab-text {
    color: #FF6B9D;
    font-weight: 600;
  }
}
</style>
