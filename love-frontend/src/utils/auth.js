/**
 * 鉴权工具函数模块
 * 负责Token存储、获取、清除，登录态判断
 */

// Token存储键名
const TOKEN_KEY = 'love_daily_token'
const USER_INFO_KEY = 'love_daily_user_info'

/**
 * 获取Token
 * @returns {string|null} Token字符串
 */
export function getToken() {
  return uni.getStorageSync(TOKEN_KEY) || null
}

/**
 * 设置Token
 * @param {string} token - Token字符串
 */
export function setToken(token) {
  uni.setStorageSync(TOKEN_KEY, token)
}

/**
 * 移除Token
 */
export function removeToken() {
  uni.removeStorageSync(TOKEN_KEY)
}

/**
 * 获取用户信息
 * @returns {Object|null} 用户信息对象
 */
export function getUserInfo() {
  const info = uni.getStorageSync(USER_INFO_KEY)
  return info ? JSON.parse(info) : null
}

/**
 * 设置用户信息
 * @param {Object} userInfo - 用户信息对象
 */
export function setUserInfo(userInfo) {
  uni.setStorageSync(USER_INFO_KEY, JSON.stringify(userInfo))
}

/**
 * 移除用户信息
 */
export function removeUserInfo() {
  uni.removeStorageSync(USER_INFO_KEY)
}

/**
 * 判断是否已登录
 * @returns {boolean} 是否已登录
 */
export function isLoggedIn() {
  return !!getToken()
}

/**
 * 清除所有登录态
 */
export function clearAuth() {
  removeToken()
  removeUserInfo()
}

/**
 * 检查登录态，未登录则跳转登录页
 * @returns {boolean} 是否已登录
 */
export function checkLogin() {
  if (!isLoggedIn()) {
    uni.navigateTo({
      url: '/pages/user/login'
    })
    return false
  }
  return true
}

export default {
  getToken,
  setToken,
  removeToken,
  getUserInfo,
  setUserInfo,
  removeUserInfo,
  isLoggedIn,
  clearAuth,
  checkLogin
}
