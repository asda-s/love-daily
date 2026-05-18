/**
 * 通用页面辅助工具
 * 提供下拉刷新、删除确认等通用逻辑
 */
import { ref } from 'vue'

/**
 * 下拉刷新 + 上拉加载 composable
 * @param {Function} fetchFn - 数据获取函数，接收 (isRefresh) 参数
 */
export function useRefreshLoad(fetchFn) {
  const refreshing = ref(false)
  const loading = ref(false)

  async function onRefresh() {
    refreshing.value = true
    await fetchFn(true)
    refreshing.value = false
  }

  async function onLoadMore(noMore, page, pageSize) {
    if (noMore.value || loading.value) return false
    page.value++
    return true
  }

  return { refreshing, loading, onRefresh, onLoadMore }
}

/**
 * 删除确认弹窗
 * @param {String} itemName - 删除对象名称（如"这条记录"）
 * @returns {Promise<boolean>} 用户是否确认删除
 */
export function confirmDelete(itemName = '这条记录') {
  return new Promise((resolve) => {
    uni.showModal({
      title: '确认删除',
      content: `确定要删除${itemName}吗？删除后无法恢复。`,
      confirmText: '删除',
      confirmColor: '#e43d33',
      success: (res) => {
        resolve(res.confirm)
      }
    })
  })
}

/**
 * 通用成功提示
 */
export function showSuccess(msg = '操作成功') {
  uni.showToast({ title: msg, icon: 'success' })
}

/**
 * 通用失败提示
 */
export function showError(msg = '操作失败') {
  uni.showToast({ title: msg, icon: 'none' })
}
