/**
 * 全局通用状态管理模块
 * 管理全局加载状态、网络状态等
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGlobalStore = defineStore('global', () => {
  // 状态
  const isLoading = ref(false)
  const isNetworkConnected = ref(true)
  const systemInfo = ref(null)

  // 庆祝动画状态
  const showCelebration = ref(false)
  const celebrationType = ref('confetti')
  const celebrationTitle = ref('')
  const celebrationSubtitle = ref('')
  
  /**
   * 设置加载状态
   * @param {boolean} status - 加载状态
   */
  function setLoading(status) {
    isLoading.value = status
  }
  
  /**
   * 设置网络状态
   * @param {boolean} status - 网络状态
   */
  function setNetworkStatus(status) {
    isNetworkConnected.value = status
  }
  
  /**
   * 获取系统信息
   */
  function getSystemInfo() {
    if (!systemInfo.value) {
      systemInfo.value = uni.getSystemInfoSync()
    }
    return systemInfo.value
  }
  
  /**
   * 获取状态栏高度
   */
  function getStatusBarHeight() {
    const info = getSystemInfo()
    return info.statusBarHeight || 0
  }
  
  /**
   * 获取导航栏高度
   */
  function getNavBarHeight() {
    const statusBarHeight = getStatusBarHeight()
    return statusBarHeight + 44
  }

  /**
   * 触发庆祝动画
   */
  function celebrate(type, title, subtitle = '') {
    celebrationType.value = type
    celebrationTitle.value = title
    celebrationSubtitle.value = subtitle
    showCelebration.value = true
    try {
      uni.vibrateShort({ type: 'heavy' })
    } catch (e) {}
  }

  /**
   * 关闭庆祝动画
   */
  function dismissCelebration() {
    showCelebration.value = false
  }
  
  return {
    isLoading,
    isNetworkConnected,
    systemInfo,
    showCelebration,
    celebrationType,
    celebrationTitle,
    celebrationSubtitle,
    setLoading,
    setNetworkStatus,
    getSystemInfo,
    getStatusBarHeight,
    getNavBarHeight,
    celebrate,
    dismissCelebration
  }
})
