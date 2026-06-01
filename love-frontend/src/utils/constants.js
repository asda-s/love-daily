/**
 * 全局共享常量
 * 心情配置、反应配置、等级配置等
 */

// 心情配置
export const MOOD_CONFIG = {
  happy: { emoji: '😊', name: '开心', color: '#FFD700', bg: '#FFF8DC' },
  sweet: { emoji: '🥰', name: '甜蜜', color: '#FF69B4', bg: '#FFE4EC' },
  calm: { emoji: '😌', name: '平静', color: '#87CEEB', bg: '#E0F0FF' },
  tired: { emoji: '😮‍💨', name: '疲惫', color: '#808080', bg: '#F0F0F0' },
  sad: { emoji: '😢', name: '难过', color: '#4169E1', bg: '#E8EDFF' },
  angry: { emoji: '😠', name: '生气', color: '#FF4500', bg: '#FFE8E0' },
  wronged: { emoji: '🥺', name: '委屈', color: '#9370DB', bg: '#F0E8FF' },
  surprised: { emoji: '🤩', name: '惊喜', color: '#FFA500', bg: '#FFF0E0' }
}

// 心情类型列表（用于遍历）
export const MOOD_TYPES = Object.keys(MOOD_CONFIG)

// 快速反应配置
export const REACTION_CONFIG = {
  hug: { emoji: '🤗', name: '抱抱' },
  kiss: { emoji: '😘', name: '亲亲' },
  like: { emoji: '👍', name: '点赞' },
  cheer: { emoji: '💪', name: '加油' },
  pat: { emoji: '🥰', name: '摸摸头' },
  heart: { emoji: '🫰', name: '比心' }
}

// 反应类型列表
export const REACTION_TYPES = Object.keys(REACTION_CONFIG)

// 等级配置
export const LEVEL_CONFIG = [
  { level: 1, min: 0, max: 100, name: '初识' },
  { level: 2, min: 101, max: 300, name: '心动' },
  { level: 3, min: 301, max: 600, name: '热恋' },
  { level: 4, min: 601, max: 1000, name: '甜蜜' },
  { level: 5, min: 1001, max: 2000, name: '默契' },
  { level: 6, min: 2001, max: 3500, name: '深情' },
  { level: 7, min: 3501, max: 5500, name: '守护' },
  { level: 8, min: 5501, max: 8000, name: '永恒' },
  { level: 9, min: 8001, max: 12000, name: '传奇' },
  { level: 10, min: 12001, max: Infinity, name: '心动之巅' }
]

// 等级积分阈值（兼容旧代码）
export const LEVEL_POINTS = {
  1: 0, 2: 101, 3: 301, 4: 601, 5: 1001,
  6: 2001, 7: 3501, 8: 5501, 9: 8001, 10: 12001
}

/**
 * 根据心动分获取等级信息
 * @param {number} points - 心动分
 * @returns {object} { level, name, min, max, progress }
 */
export function getLevelInfo(points) {
  for (let i = LEVEL_CONFIG.length - 1; i >= 0; i--) {
    if (points >= LEVEL_CONFIG[i].min) {
      const info = LEVEL_CONFIG[i]
      const range = info.max - info.min
      const progress = range === Infinity ? 100 : Math.min(100, ((points - info.min) / range) * 100)
      return { level: info.level, name: info.name, min: info.min, max: info.max, progress }
    }
  }
  return { level: 1, name: '初识', min: 0, max: 100, progress: 0 }
}

// 账单类型
export const BILL_TYPES = {
  food: { name: '吃饭', emoji: '🍜' },
  travel: { name: '旅行', emoji: '✈️' },
  gift: { name: '礼物', emoji: '🎁' },
  daily: { name: '日常', emoji: '🏠' },
  other: { name: '其他', emoji: '📌' }
}

// 支付人
export const PAYER_TYPES = {
  me: { name: '我' },
  lover: { name: '对方' },
  aa: { name: 'AA制' }
}

// 情绪类型
export const EMOTION_TYPES = {
  happy: { emoji: '😊', name: '开心', color: '#FFD700' },
  sad: { emoji: '😢', name: '难过', color: '#4169E1' },
  angry: { emoji: '😠', name: '生气', color: '#FF4500' },
  wronged: { emoji: '🥺', name: '委屈', color: '#9370DB' },
  anxious: { emoji: '😰', name: '焦虑', color: '#FFA500' }
}
