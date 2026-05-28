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
import homeIcon from '@/static/tab/home.png'
import homeActiveIcon from '@/static/tab/home-active.png'
import timeIcon from '@/static/tab/time.png'
import timeActiveIcon from '@/static/tab/time-active.png'
import lifeIcon from '@/static/tab/life.png'
import lifeActiveIcon from '@/static/tab/life-active.png'
import interactIcon from '@/static/tab/interact.png'
import interactActiveIcon from '@/static/tab/interact-active.png'
import loveIcon from '@/static/tab/love.png'
import loveActiveIcon from '@/static/tab/love-active.png'

const props = defineProps({
  current: { type: Number, default: 0 }
})

const tabs = [
  { text: '首页', icon: homeIcon, activeIcon: homeActiveIcon, path: '/pages/index/index' },
  { text: '时光', icon: timeIcon, activeIcon: timeActiveIcon, path: '/pages/memory/timeline' },
  { text: '管家', icon: lifeIcon, activeIcon: lifeActiveIcon, path: '/pages/life/todo' },
  { text: '打卡', icon: interactIcon, activeIcon: interactActiveIcon, path: '/pages/interact/checkin' },
  { text: '养成', icon: loveIcon, activeIcon: loveActiveIcon, path: '/pages/love/index' }
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
  background: rgba(255, 255, 255, 0.92);
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
    color: #FF69B4;
    font-weight: 600;
  }
}
</style>
