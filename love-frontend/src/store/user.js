/**
 * 用户信息状态管理模块
 * 使用Pinia管理用户信息、情侣信息、登录态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { get, post, put } from '@/utils/request'
import {
  getToken, setToken, removeToken,
  getUserInfo, setUserInfo, removeUserInfo,
  clearAuth
} from '@/utils/auth'
import { connect as wsConnect, disconnect as wsDisconnect } from '@/utils/websocket'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(getToken())
  const userInfo = ref(getUserInfo())
  const loverInfo = ref(null)
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isBindLover = computed(() => !!userInfo.value?.lover_id)
  const heartPoints = computed(() => userInfo.value?.heart_points || 0)
  const level = computed(() => userInfo.value?.level || 1)
  
  /**
   * 用户登录
   * @param {Object} loginData - 登录数据
   */
  async function login(loginData) {
    const res = await post('/user/login', loginData)
    if (!res?.data?.token) throw new Error('登录响应数据异常')
    token.value = res.data.token
    setToken(res.data.token)
    wsConnect(res.data.token)
    await getUserInfoFromServer()
    return res
  }
  
  /**
   * 用户注册
   * @param {Object} registerData - 注册数据
   */
  async function register(registerData) {
    return await post('/user/register', registerData)
  }
  
  /**
   * 获取用户信息
   */
  async function getUserInfoFromServer() {
    const res = await get('/user/info')
    userInfo.value = res.data
    setUserInfo(res.data)
    return res.data
  }
  
  /**
   * 修改用户信息
   * @param {Object} updateData - 修改数据
   */
  async function updateUserInfo(updateData) {
    const res = await put('/user/info', updateData)
    await getUserInfoFromServer()
    return res
  }
  
  /**
   * 绑定情侣
   * @param {string} inviteCode - 邀请码
   */
  async function bindLover(inviteCode) {
    const res = await post('/user/bind', { invite_code: inviteCode })
    await getUserInfoFromServer()
    await getLoverInfo()
    return res
  }
  
  /**
   * 获取情侣信息
   */
  async function getLoverInfo() {
    if (!isBindLover.value) {
      loverInfo.value = null
      return null
    }
    const res = await get('/user/lover')
    loverInfo.value = res.data
    return res.data
  }

  /**
   * 解除情侣绑定
   */
  async function unbindLover() {
    const res = await post('/user/unbind')
    await getUserInfoFromServer()
    loverInfo.value = null
    uni.removeStorageSync('invite_dialog_skipped')
    return res
  }
  
  /**
   * 退出登录
   */
  function logout() {
    wsDisconnect()
    token.value = null
    userInfo.value = null
    loverInfo.value = null
    clearAuth()
  }
  
  /**
   * 检查登录态
   */
  function checkAuth() {
    if (!isLoggedIn.value) {
      uni.navigateTo({
        url: '/pages/user/login'
      })
      return false
    }
    return true
  }
  
  return {
    token,
    userInfo,
    loverInfo,
    isLoggedIn,
    isBindLover,
    heartPoints,
    level,
    login,
    register,
    getUserInfoFromServer,
    updateUserInfo,
    bindLover,
    unbindLover,
    getLoverInfo,
    logout,
    checkAuth
  }
})
