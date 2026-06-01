/**
 * 通用工具函数模块
 * 提供日期格式化、倒计时计算等常用工具函数
 */

/**
 * 格式化日期
 * @param {Date|string|number} date - 日期对象、日期字符串或时间戳
 * @param {string} format - 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return ''
  
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 计算倒计时天数
 * @param {Date|string} targetDate - 目标日期
 * @returns {number} 倒计时天数（负数表示已过期）
 */
export function getDaysLeft(targetDate) {
  const target = new Date(targetDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  
  const diffTime = target.getTime() - today.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

/**
 * 获取相对时间描述
 * @param {Date|string} date - 日期
 * @returns {string} 相对时间描述
 */
export function getRelativeTime(date) {
  const now = new Date()
  const target = new Date(date)
  const diff = now.getTime() - target.getTime()
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 30) {
    return formatDate(date, 'YYYY-MM-DD')
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

/**
 * 防抖函数
 * @param {Function} fn - 需要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn - 需要节流的函数
 * @param {number} interval - 间隔时间（毫秒）
 * @returns {Function} 节流后的函数
 */
export function throttle(fn, interval = 300) {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

/**
 * 生成唯一ID
 * @returns {string} 唯一ID
 */
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * 深拷贝对象
 * @param {Object} obj - 需要拷贝的对象
 * @returns {Object} 拷贝后的对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  return JSON.parse(JSON.stringify(obj))
}

/**
 * 格式化金额
 * @param {number} amount - 金额
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的金额
 */
export function formatAmount(amount, decimals = 2) {
  return Number(amount).toFixed(decimals)
}

/**
 * 获取等级信息
 * @param {number} heartPoints - 心动分
 * @returns {Object} 等级信息
 */
export function getLevelInfo(heartPoints) {
  const { LEVEL_CONFIG } = require('./constants')

  let current = LEVEL_CONFIG[0]
  for (let i = LEVEL_CONFIG.length - 1; i >= 0; i--) {
    if (heartPoints >= LEVEL_CONFIG[i].min) {
      current = LEVEL_CONFIG[i]
      break
    }
  }

  const next = LEVEL_CONFIG.find(l => l.level === current.level + 1)
  const range = current.max === Infinity ? current.min + 1 : current.max - current.min
  const progress = current.max === Infinity ? 100 : Math.min(100, ((heartPoints - current.min) / range) * 100)

  return {
    level: current.level,
    name: current.name,
    min: current.min,
    max: current.max,
    progress: Math.min(progress, 100),
    nextLevel: next || null,
    pointsToNext: next ? next.min - heartPoints : 0
  }
}

export default {
  formatDate,
  getDaysLeft,
  getRelativeTime,
  debounce,
  throttle,
  generateId,
  deepClone,
  formatAmount,
  getLevelInfo
}
