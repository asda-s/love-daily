<template>
  <view v-if="visible" class="celebration-overlay" @click="dismiss">
    <!-- 粒子容器 -->
    <view class="particles">
      <view
        v-for="i in particleCount"
        :key="i"
        class="particle"
        :class="particleClass"
        :style="particleStyle(i)"
      >
        <text v-if="type === 'hearts'" class="particle-emoji">❤️</text>
        <text v-else-if="type === 'burst'" class="particle-emoji">✨</text>
      </view>
    </view>

    <!-- 中央内容 -->
    <view class="celebration-content">
      <text class="celebration-title">{{ title }}</text>
      <text v-if="subtitle" class="celebration-subtitle">{{ subtitle }}</text>
    </view>
  </view>
</template>

<script setup>
import { computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  type: { type: String, default: 'confetti' },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' }
})

const emit = defineEmits(['dismiss'])

let dismissTimer = null

const particleCount = computed(() => {
  if (props.type === 'hearts') return 20
  if (props.type === 'burst') return 24
  return 30 // confetti
})

const particleClass = computed(() => `particle-${props.type}`)

function particleStyle(i) {
  const left = (i * 37) % 100
  const delay = ((i * 0.13) % 2).toFixed(2)
  const duration = (2 + (i % 3)).toFixed(1)
  const hue = (i * 47) % 360

  const style = {
    left: left + '%',
    animationDelay: delay + 's',
    animationDuration: duration + 's'
  }

  if (props.type === 'confetti') {
    style.backgroundColor = `hsl(${hue}, 80%, 60%)`
  }

  if (props.type === 'burst') {
    // 每个粒子飞向不同方向（均匀分布 360 度）
    const angle = (i / 24) * 2 * Math.PI
    const distance = 150 + (i % 3) * 80
    const tx = Math.cos(angle) * distance
    const ty = Math.sin(angle) * distance
    style['--tx'] = tx + 'rpx'
    style['--ty'] = ty + 'rpx'
  }

  return style
}

function dismiss() {
  clearTimeout(dismissTimer)
  emit('dismiss')
}

watch(() => props.visible, (val) => {
  clearTimeout(dismissTimer)
  if (val) {
    dismissTimer = setTimeout(() => {
      emit('dismiss')
    }, 3000)
  }
}, { immediate: true })

onUnmounted(() => {
  clearTimeout(dismissTimer)
})
</script>

<style lang="scss" scoped>
.celebration-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
}

.particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  top: -20rpx;
}

/* 彩纸粒子 */
.particle-confetti {
  width: 16rpx;
  height: 16rpx;
  border-radius: 4rpx;
  animation: confetti-fall linear forwards;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) rotate(720deg);
    opacity: 0;
  }
}

/* 爱心粒子 */
.particle-hearts {
  bottom: 0;
  top: auto;
  animation: heart-float ease-in-out forwards;
}

.particle-emoji {
  font-size: 40rpx;
}

@keyframes heart-float {
  0% {
    transform: translateY(0) scale(0.5);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) scale(1.2) translateX(40rpx);
    opacity: 0;
  }
}

/* 爆散粒子 */
.particle-burst {
  top: 50%;
  left: 50%;
  animation: burst-out ease-out forwards;
}

@keyframes burst-out {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 1;
  }
  100% {
    transform: translate(
      calc(-50% + var(--tx, 200rpx)),
      calc(-50% + var(--ty, -200rpx))
    ) scale(1.5);
    opacity: 0;
  }
}

/* 中央内容 */
.celebration-content {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: content-pop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.celebration-title {
  font-size: 56rpx;
  font-weight: bold;
  color: #FFFFFF;
  text-shadow: 0 4rpx 12rpx rgba(255, 105, 180, 0.6);
  margin-bottom: 16rpx;
}

.celebration-subtitle {
  font-size: 30rpx;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.3);
  max-width: 500rpx;
  text-align: center;
}

@keyframes content-pop {
  0% {
    transform: scale(0.3);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
