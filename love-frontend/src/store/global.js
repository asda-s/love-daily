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
  
  return {
    isLoading,
    isNetworkConnected,
    systemInfo,
    setLoading,
    setNetworkStatus,
    getSystemInfo,
    getStatusBarHeight,
    getNavBarHeight
  }
})
