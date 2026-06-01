/**
 * 全局请求封装模块
 * 实现Token自动携带、统一错误处理、登录态过期自动跳转登录页、统一加载提示
 */

import { getToken, removeToken } from './auth'

// API基础地址配置
// #ifdef MP-WEIXIN
const BASE_URL = 'https://你的域名'  // TODO: 替换为你的后端HTTPS域名
// #endif
// #ifndef MP-WEIXIN
const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
// #endif

// 请求队列，用于控制loading显示
let requestCount = 0

let loadingTimer = null

/**
 * 显示加载提示
 */
function showLoading() {
  if (requestCount === 0) {
    uni.showLoading({
      title: '加载中...',
      mask: true
    })
    // 5秒后更新提示，可能是服务器冷启动
    loadingTimer = setTimeout(() => {
      uni.showLoading({
        title: '服务器启动中，请稍候...',
        mask: true
      })
    }, 5000)
  }
  requestCount++
}

/**
 * 隐藏加载提示
 */
function hideLoading() {
  requestCount--
  if (requestCount <= 0) {
    requestCount = 0
    if (loadingTimer) {
      clearTimeout(loadingTimer)
      loadingTimer = null
    }
    uni.hideLoading()
  }
}

/**
 * 统一请求方法
 * @param {Object} options - 请求配置
 * @param {string} options.url - 请求路径
 * @param {string} options.method - 请求方法
 * @param {Object} options.data - 请求数据
 * @param {boolean} options.showLoading - 是否显示loading
 * @param {boolean} options.showError - 是否显示错误提示
 * @returns {Promise} 请求结果
 */
function request(options = {}) {
  const {
    url,
    method = 'GET',
    data = {},
    useLoading = true,
    showError = true
  } = options

  return new Promise((resolve, reject) => {
    if (useLoading) {
      showLoading()
    }

    // 获取Token
    const token = getToken()

    // 构建请求头
    const header = {
      'Content-Type': 'application/json'
    }
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    // 发起请求
    uni.request({
      url: `${BASE_URL}${url}`,
      method: method,
      data: data,
      header: header,
      timeout: 60000,
      success: (res) => {
        if (useLoading) {
          hideLoading()
        }

        if (res.statusCode === 200) {
          const result = res.data
          if (result.code === 200) {
            resolve(result)
          } else if (result.code === 401) {
            removeToken()
            uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
            setTimeout(() => { uni.reLaunch({ url: '/pages/user/login' }) }, 500)
            reject(result)
          } else {
            if (showError) {
              uni.showToast({ title: result.message || '操作失败', icon: 'none' })
            }
            reject(result)
          }
        } else if (res.statusCode === 401) {
          removeToken()
          uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
          setTimeout(() => { uni.reLaunch({ url: '/pages/user/login' }) }, 500)
          reject(res.data)
        } else if (res.statusCode === 403) {
          if (showError) uni.showToast({ title: '没有访问权限', icon: 'none' })
          reject(res.data)
        } else if (res.statusCode === 404) {
          if (showError) uni.showToast({ title: '请求的资源不存在', icon: 'none' })
          reject(res.data)
        } else if (res.statusCode >= 500) {
          if (showError) uni.showToast({ title: '服务器开小差了，请稍后再试', icon: 'none' })
          reject(res.data)
        } else {
          if (showError) uni.showToast({ title: '网络请求失败', icon: 'none' })
          reject(res.data)
        }
      },
      fail: (err) => {
        if (useLoading) {
          hideLoading()
        }
        const msg = err.errMsg?.includes('timeout') ? '服务器响应超时，可能正在重启，请稍后再试' : '网络连接失败，请检查网络'
        if (showError) uni.showToast({ title: msg, icon: 'none' })
        reject(err)
      }
    })
  })
}

/**
 * GET请求
 * @param {string} url - 请求路径
 * @param {Object} data - 请求参数
 * @param {Object} options - 其他配置
 * @returns {Promise}
 */
export function get(url, data = {}, options = {}) {
  return request({ url, method: 'GET', data, ...options })
}

/**
 * POST请求
 * @param {string} url - 请求路径
 * @param {Object} data - 请求数据
 * @param {Object} options - 其他配置
 * @returns {Promise}
 */
export function post(url, data = {}, options = {}) {
  return request({ url, method: 'POST', data, ...options })
}

/**
 * PUT请求
 * @param {string} url - 请求路径
 * @param {Object} data - 请求数据
 * @param {Object} options - 其他配置
 * @returns {Promise}
 */
export function put(url, data = {}, options = {}) {
  return request({ url, method: 'PUT', data, ...options })
}

/**
 * DELETE请求
 * @param {string} url - 请求路径
 * @param {Object} data - 请求数据
 * @param {Object} options - 其他配置
 * @returns {Promise}
 */
export function del(url, data = {}, options = {}) {
  return request({ url, method: 'DELETE', data, ...options })
}

export default {
  request,
  get,
  post,
  put,
  del
}
