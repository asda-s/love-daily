/**
 * WebSocket 实时通信客户端
 * 基于 uni.connectSocket API，兼容 H5 和微信小程序
 * 支持心跳、自动重连、消息分发
 */

import { getToken } from '@/utils/auth'

// 连接状态
let socketTask = null
let heartbeatTimer = null
let heartbeatTimeout = null
let reconnectTimer = null
let reconnectAttempts = 0
let manuallyClosed = false
let connected = false

const MAX_RECONNECT_ATTEMPTS = 10
const HEARTBEAT_INTERVAL = 30000
const HEARTBEAT_TIMEOUT = 10000
const listeners = {}

/**
 * 获取 WebSocket 连接地址
 */
function getWsUrl() {
  const token = getToken()
  if (!token) return null

  // #ifdef H5
  const base = import.meta.env.VITE_API_BASE_URL || ''
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  // 开发模式下直接用当前 host，生产模式用配置的 API 地址
  let host
  if (import.meta.env.DEV) {
    host = window.location.host
  } else {
    // 从 http(s)://xxx 转为 ws(s)://xxx
    host = base.replace(/^https?:\/\//, '')
  }
  return `${protocol}//${host}/ws/notifications?token=${token}`
  // #endif

  // #ifdef MP-WEIXIN || APP-PLUS
  return `wss://love-daily-api.onrender.com/ws/notifications?token=${token}`
  // #endif
}

/**
 * 建立 WebSocket 连接
 */
export function connect(token) {
  if (socketTask) {
    disconnect()
  }

  manuallyClosed = false
  connected = false
  const url = getWsUrl()
  if (!url) return

  socketTask = uni.connectSocket({
    url,
    success: () => console.log('[WS] 正在连接...')
  })

  // 使用 socketTask 实例方法，避免全局事件监听器堆积
  if (socketTask && socketTask.onOpen) {
    socketTask.onOpen(() => {
      console.log('[WS] 连接成功')
      reconnectAttempts = 0
      connected = true
      startHeartbeat()
      dispatch('connected', {})
    })

    socketTask.onMessage((res) => {
      const data = res.data
      if (data === 'pong') {
        clearTimeout(heartbeatTimeout)
        heartbeatTimeout = null
        dispatch('pong', {})
        return
      }
      try {
        const msg = JSON.parse(data)
        if (msg.type) {
          dispatch(msg.type, msg.data || {})
        }
      } catch (e) {
        console.warn('[WS] 消息解析失败:', data)
      }
    })

    socketTask.onClose(() => {
      console.log('[WS] 连接关闭')
      stopHeartbeat()
      connected = false
      socketTask = null
      if (!manuallyClosed) {
        scheduleReconnect()
      }
    })

    socketTask.onError((err) => {
      console.error('[WS] 连接错误:', err)
      stopHeartbeat()
      connected = false
      socketTask = null
      if (!manuallyClosed) {
        scheduleReconnect()
      }
    })
  } else {
    // 回退：部分平台不支持 socketTask 实例方法，使用全局 API
    uni.onSocketOpen(() => {
      console.log('[WS] 连接成功')
      reconnectAttempts = 0
      connected = true
      startHeartbeat()
      dispatch('connected', {})
    })

    uni.onSocketMessage((res) => {
      const data = res.data
      if (data === 'pong') {
        clearTimeout(heartbeatTimeout)
        heartbeatTimeout = null
        dispatch('pong', {})
        return
      }
      try {
        const msg = JSON.parse(data)
        if (msg.type) {
          dispatch(msg.type, msg.data || {})
        }
      } catch (e) {
        console.warn('[WS] 消息解析失败:', data)
      }
    })

    uni.onSocketClose(() => {
      console.log('[WS] 连接关闭')
      stopHeartbeat()
      connected = false
      socketTask = null
      if (!manuallyClosed) {
        scheduleReconnect()
      }
    })

    uni.onSocketError((err) => {
      console.error('[WS] 连接错误:', err)
      stopHeartbeat()
      connected = false
      socketTask = null
      if (!manuallyClosed) {
        scheduleReconnect()
      }
    })
  }
}

/**
 * 断开连接
 */
export function disconnect() {
  manuallyClosed = true
  stopHeartbeat()
  clearTimeout(reconnectTimer)
  reconnectTimer = null
  reconnectAttempts = 0
  if (socketTask) {
    uni.closeSocket()
    socketTask = null
  }
}

/**
 * 发送消息
 */
export function send(data) {
  if (!socketTask) return
  const text = typeof data === 'string' ? data : JSON.stringify(data)
  uni.sendSocketMessage({ data: text })
}

/**
 * 是否已连接
 */
export function isConnected() {
  return connected && !!socketTask
}

/**
 * 订阅消息类型
 */
export function subscribe(type, callback) {
  if (!listeners[type]) {
    listeners[type] = []
  }
  listeners[type].push(callback)
}

/**
 * 取消订阅
 */
export function unsubscribe(type, callback) {
  if (!listeners[type]) return
  if (!callback) {
    delete listeners[type]
    return
  }
  listeners[type] = listeners[type].filter(cb => cb !== callback)
}

/**
 * 分发消息到订阅者
 */
function dispatch(type, data) {
  const cbs = listeners[type]
  if (cbs) {
    cbs.forEach(cb => {
      try {
        cb(data)
      } catch (e) {
        console.error(`[WS] 消息处理异常 (${type}):`, e)
      }
    })
  }
}

/**
 * 启动心跳
 */
function startHeartbeat() {
  stopHeartbeat()
  heartbeatTimer = setInterval(() => {
    if (socketTask) {
      uni.sendSocketMessage({ data: 'ping' })
      // 10秒内无 pong 响应则判定连接断开，触发重连
      clearTimeout(heartbeatTimeout)
      heartbeatTimeout = setTimeout(() => {
        console.warn('[WS] 心跳超时，触发重连')
        if (socketTask) {
          uni.closeSocket()
        }
      }, HEARTBEAT_TIMEOUT)
    }
  }, HEARTBEAT_INTERVAL)
}

/**
 * 停止心跳
 */
function stopHeartbeat() {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
  clearTimeout(heartbeatTimeout)
  heartbeatTimeout = null
}

/**
 * 计划重连（指数退避）
 */
function scheduleReconnect() {
  if (manuallyClosed) return
  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
    console.log('[WS] 达到最大重连次数，停止重连')
    return
  }

  const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000)
  reconnectAttempts++
  console.log(`[WS] ${delay / 1000}秒后第${reconnectAttempts}次重连...`)

  reconnectTimer = setTimeout(() => {
    const token = getToken()
    if (token) {
      connect(token)
    }
  }, delay)
}
