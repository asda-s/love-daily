/**
 * 项目入口文件
 * 初始化Vue3、Pinia状态管理
 */

import App from './App'
import { createSSRApp } from 'vue'
import { createPinia } from 'pinia'

export function createApp() {
  const app = createSSRApp(App)
  const pinia = createPinia()
  
  app.use(pinia)
  
  return {
    app
  }
}
