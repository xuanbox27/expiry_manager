<template>
  <div class="page">
    <div class="container">
      <div class="header">
        <h1>通知</h1>
        <div style="display: flex; gap: 10px;">
          <button 
            :class="['btn', unreadOnly ? 'btn-primary' : 'btn-secondary']"
            @click="toggleUnreadOnly"
          >
            仅未读
          </button>
          <button 
            class="btn btn-secondary"
            @click="markAllAsRead"
            :disabled="notifications.length === 0"
          >
            全部已读
          </button>
        </div>
      </div>

      <div v-if="loading" style="text-align: center; padding: 40px;">
        加载中...
      </div>

      <div v-else-if="notifications.length === 0" class="empty-state">
        <h2>暂无通知</h2>
        <p>物品即将过期时会在此提醒您</p>
      </div>

      <div v-else class="notification-list">
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          :class="['notification-card', { unread: !notification.is_read }]"
        >
          <div class="notification-content">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
          </div>
          <div class="notification-actions">
            <button 
              v-if="!notification.is_read"
              class="btn-icon"
              @click="markAsRead(notification.id)"
              title="标记已读"
            >
              ✓
            </button>
            <button 
              class="btn-icon"
              @click="deleteNotification(notification.id)"
              title="删除"
            >
              ×
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { notificationsApi } from '../api'

const showNotification = inject('showNotification')

const notifications = ref([])
const loading = ref(true)
const unreadOnly = ref(false)

const fetchNotifications = async () => {
  loading.value = true
  try {
    const response = await notificationsApi.getAll(unreadOnly.value)
    notifications.value = response.data
  } catch (error) {
    showNotification('加载通知失败', 'error')
  } finally {
    loading.value = false
  }
}

const toggleUnreadOnly = () => {
  unreadOnly.value = !unreadOnly.value
  fetchNotifications()
}

const markAsRead = async (id) => {
  try {
    await notificationsApi.markRead(id)
    const notification = notifications.value.find(n => n.id === id)
    if (notification) notification.is_read = true
  } catch (error) {
    showNotification('标记失败', 'error')
  }
}

const markAllAsRead = async () => {
  try {
    await notificationsApi.markAllRead()
    notifications.value.forEach(n => n.is_read = true)
    showNotification('已全部标记为已读')
  } catch (error) {
    showNotification('操作失败', 'error')
  }
}

const deleteNotification = async (id) => {
  try {
    await notificationsApi.delete(id)
    notifications.value = notifications.value.filter(n => n.id !== id)
    showNotification('已删除')
  } catch (error) {
    showNotification('删除失败', 'error')
  }
}

const formatTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

onMounted(fetchNotifications)
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-left: 3px solid var(--gray-400);
}

.notification-card.unread {
  border-left-color: var(--primary);
  background: rgba(37, 99, 235, 0.05);
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.notification-message {
  color: var(--gray-600);
  font-size: 14px;
  margin-bottom: 8px;
}

.notification-time {
  font-size: 12px;
  color: var(--gray-500);
}

.notification-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: transparent;
  border: 1px solid var(--gray-300);
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  color: var(--gray-600);
  font-size: 14px;
}

.btn-icon:hover {
  background: var(--gray-100);
}
</style>
